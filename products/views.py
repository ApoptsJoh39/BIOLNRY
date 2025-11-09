from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Category, Product

class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(available=True)
        
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)
        
        sort_by = self.request.GET.get('sort')
        if sort_by == 'latest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'price_low_to_high':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_high_to_low':
            queryset = queryset.order_by('-price')
        elif sort_by == 'name_a_to_z':
            queryset = queryset.order_by('name')
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        
        # Process pricing based on user authentication status
        products_with_prices = []
        for product in context['products']:
            products_with_prices.append({
                'product': product,
                'price': product.get_price(self.request.user)
            })
        context['products_with_prices'] = products_with_prices
        
        # Add user type info for price display explanation
        user = self.request.user
        if user.is_authenticated:
            context['user_type'] = user.user_type
        else:
            context['user_type'] = 'guest'
            
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get price based on user type
        product = context['product']
        context['price'] = product.get_price(self.request.user)
        
        # Add user type info
        user = self.request.user
        if user.is_authenticated:
            context['user_type'] = user.user_type
        else:
            context['user_type'] = 'guest'
            
        # Add related products
        context['related_products'] = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:4]
        
        return context