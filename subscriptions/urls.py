from django.urls import path
from . import views

urlpatterns = [
    path('', views.subscription_form, name='subscription_form'),
    path('stripe-redirect/', views.stripe_redirect, name='stripe_redirect'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('resend-email/<int:subscriber_id>/', views.resend_email, name='resend_email'),
] 