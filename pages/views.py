from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from products.models import Product, Category

class HomeView(ListView):
    model = Product
    template_name = 'pages/home.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        return Product.objects.filter(available=True)[:8]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()[:6]
        
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

class AboutView(TemplateView):
    template_name = 'pages/about.html'

class ContactView(TemplateView):
    template_name = 'pages/contact.html'