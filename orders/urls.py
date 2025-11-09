from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart'),
    path('add/<int:product_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('remove/<str:item_key>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('update/<str:item_key>/', views.UpdateCartView.as_view(), name='update_cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('payment/success/', views.PaymentSuccessView.as_view(), name='payment_success'),
    path('payment/cancel/', views.PaymentCancelView.as_view(), name='payment_cancel'),
    path('webhook/stripe/', views.StripeWebhookView.as_view(), name='stripe_webhook'),
    path('my-orders/', views.OrderListView.as_view(), name='order_list'),
    path('my-orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
]