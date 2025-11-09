
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

import stripe
import json
from decimal import Decimal

from .models import Order, OrderItem, ShippingAddress
from .forms import OrderCreateForm
from products.models import Product

import logging

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


class AddToCartView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, available=True)
        quantity = int(request.POST.get('quantity', 1))
        size = request.POST.get('size')
        color = request.POST.get('color')
        
        cart = request.session.get('cart', {})
        
        item_key = f"{product.id}"
        if size:
            item_key += f"_{size}"
        if color:
            item_key += f"_{color}"

        if item_key in cart:
            cart[item_key]['quantity'] += quantity
        else:
            cart[item_key] = {
                'product_id': product.id,
                'quantity': quantity,
                'size': size,
                'color': color,
            }

        request.session['cart'] = cart
        messages.success(request, f"Added {product.name} to your cart.")
        
        return redirect('cart')


class CartView(View):
    template_name = 'orders/cart.html'
    
    def get(self, request):
        cart = request.session.get('cart', {})
        cart_items = []
        total = Decimal('0.00')
        keys_to_delete = []
        cart_needs_update = False

        updated_cart = {}
        for item_key, item_data in cart.items():
            if not isinstance(item_data, dict):
                cart_needs_update = True
                try:
                    product_id = int(item_key)
                    quantity = int(item_data)
                    new_key = str(product_id)
                    updated_cart[new_key] = {
                        'product_id': product_id,
                        'quantity': quantity,
                        'size': None,
                        'color': None,
                    }
                except (ValueError, TypeError):
                    keys_to_delete.append(item_key)
            else:
                updated_cart[item_key] = item_data
        
        if cart_needs_update:
            cart = updated_cart
            request.session['cart'] = cart

        for item_key, item_data in cart.items():
            try:
                product_id = item_data['product_id']
                product = Product.objects.get(id=product_id)
                price = product.get_price(request.user)
                quantity = item_data['quantity']
                item_total = price * quantity
                
                cart_items.append({
                    'item_key': item_key,
                    'product': product,
                    'quantity': quantity,
                    'price': price,
                    'total': item_total,
                    'size': item_data.get('size'),
                    'color': item_data.get('color'),
                })
                total += item_total
            except (Product.DoesNotExist, KeyError, TypeError) as e:
                logger.warning(f"Removing invalid item {item_key} from cart. Reason: {e}")
                keys_to_delete.append(item_key)

        if keys_to_delete:
            for key in keys_to_delete:
                if key in cart:
                    del cart[key]
            request.session['cart'] = cart
        
        context = {
            'cart_items': cart_items,
            'total': total,
            'user_type': 'guest' if not request.user.is_authenticated else request.user.user_type
        }
        return render(request, self.template_name, context)


class RemoveFromCartView(View):
    def post(self, request, item_key):
        cart = request.session.get('cart', {})
        
        if item_key in cart:
            del cart[item_key]
            request.session['cart'] = cart
            messages.success(request, "Item removed from your cart.")
        
        return redirect('cart')


class UpdateCartView(View):
    def post(self, request, item_key):
        cart = request.session.get('cart', {})
        quantity = int(request.POST.get('quantity', 1))
        
        if item_key in cart and quantity > 0:
            cart[item_key]['quantity'] = quantity
            request.session['cart'] = cart
            messages.success(request, "Cart updated.")
        elif item_key in cart and quantity <= 0:
            del cart[item_key]
            request.session['cart'] = cart
            messages.success(request, "Item removed from your cart.")
            
        return redirect('cart')


class CheckoutView(View):
    template_name = 'orders/checkout.html'
    
    def get(self, request):
        cart = request.session.get('cart', {})
        if not cart:
            messages.warning(request, "Your cart is empty.")
            return redirect('product_list')

        cart_items = []
        total = Decimal('0.00')
        for item_key, item_data in cart.items():
            try:
                product = Product.objects.get(id=item_data['product_id'])
                price = product.get_price(request.user)
                cart_items.append({
                    'product': product,
                    'quantity': item_data['quantity'],
                    'price': price,
                    'total': price * item_data['quantity'],
                    'size': item_data.get('size'),
                    'color': item_data.get('color'),
                })
                total += price * item_data['quantity']
            except (Product.DoesNotExist, KeyError, TypeError):
                continue

        initial_data = {'email': request.user.email} if request.user.is_authenticated else {}
        if request.user.is_authenticated:
            shipping_address = ShippingAddress.objects.filter(user=request.user, default=True).first()
            if shipping_address:
                initial_data.update({
                    'full_name': shipping_address.full_name, 'address': shipping_address.address,
                    'city': shipping_address.city, 'state': shipping_address.state,
                    'postal_code': shipping_address.postal_code, 'country': shipping_address.country,
                    'phone': shipping_address.phone
                })
        
        form = OrderCreateForm(initial=initial_data)
        context = {
            'form': form, 'cart_items': cart_items, 'total': total,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'shipping_addresses': ShippingAddress.objects.filter(user=request.user) if request.user.is_authenticated else None,
            'user_type': 'guest' if not request.user.is_authenticated else request.user.user_type
        }
        return render(request, self.template_name, context)

    def post(self, request):
        try:
            data = json.loads(request.body)
            cart = request.session.get('cart', {})
            if not cart:
                return JsonResponse({'error': 'Cart is empty'}, status=400)

            line_items = []
            for item_key, item_data in cart.items():
                try:
                    product = Product.objects.get(id=item_data['product_id'])
                    price = product.get_price(request.user)
                    product_name = product.name

                    line_items.append({
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {'name': product_name},
                            'unit_amount': int(price * 100),
                        },
                        'quantity': item_data['quantity'],
                    })
                except (Product.DoesNotExist, KeyError, TypeError):
                    continue
            
            if not line_items:
                return JsonResponse({'error': 'No valid items in cart to process.'}, status=400)
            
            metadata = {
                'order_data': json.dumps(data),
                'cart': json.dumps(cart)
            }
            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items, mode='payment',
                success_url=request.build_absolute_uri(reverse('payment_success')),
                cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
                customer_email=data.get('email'), metadata=metadata
            )
            
            request.session['stripe_checkout_session_id'] = checkout_session.id

            return JsonResponse({'session_id': checkout_session.id})

        except Exception as e:
            logger.error(f"Error creating Stripe session: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)


class PaymentSuccessView(View):
    template_name = 'orders/payment_success.html'

    @transaction.atomic
    def get(self, request):
        session_id = request.session.pop('stripe_checkout_session_id', None)
        
        if not session_id:
            messages.error(request, "Could not find payment session. If payment was made, please check your orders.")
            return redirect('order_list')
        
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            order_data = json.loads(session.metadata.get('order_data', '{}'))
            cart_data = json.loads(session.metadata.get('cart', '{}'))

            if Order.objects.filter(stripe_session_id=session.id).exists():
                messages.info(request, "This order has already been processed.")
                order = Order.objects.get(stripe_session_id=session.id)
                return render(request, self.template_name, {'order': order})

            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                email=order_data['email'], full_name=order_data['full_name'],
                address=order_data['address'], city=order_data.get('city', ''),
                state=order_data.get('state', ''), postal_code=order_data.get('postal_code', ''),
                country=order_data.get('country', ''), phone=order_data.get('phone', ''),
                status='processing', total_amount=Decimal(session.amount_total) / 100,
                stripe_payment_id=session.payment_intent, stripe_session_id=session.id,
            )

            for item_key, item_data in cart_data.items():
                try:
                    product = Product.objects.get(id=item_data['product_id'])
                    OrderItem.objects.create(
                        order=order, product=product,
                        price=product.get_price(request.user),
                        quantity=item_data['quantity'],
                        size=item_data.get('size'),
                        color=item_data.get('color'),
                    )
                    product.stock -= item_data['quantity']
                    product.save()
                except Product.DoesNotExist:
                    logger.warning(f"Product with id {item_data['product_id']} not found during order creation.")
                    continue
            
            if 'cart' in request.session:
                del request.session['cart']

            messages.success(request, "Your payment was successful and your order has been placed!")
            return render(request, self.template_name, {'order': order})

        except stripe.error.StripeError as e:
            messages.error(request, "Payment verification failed. Please contact support.")
            logger.error(f"Stripe Error on success page: {str(e)}")
            return redirect('checkout')
        except Exception as e:
            messages.error(request, "An unexpected error occurred while creating your order.")
            logger.error(f"Error in PaymentSuccessView: {str(e)}")
            return redirect('checkout')


class PaymentCancelView(View):
    def get(self, request):
        messages.warning(request, "Your payment was cancelled.")
        return redirect('checkout')


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    def post(self, request):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            return HttpResponse(status=400)
        
        if event['type'] == 'checkout.session.completed':
            self.handle_checkout_session(event['data']['object'])
            
        return HttpResponse(status=200)
    
    def handle_checkout_session(self, session):
        pass


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        return context
