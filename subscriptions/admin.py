from django.contrib import admin
from .models import Subscriber

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_paid', 'created_at', 'pdf_generated', 'email_sent')
    list_filter = ('is_paid', 'pdf_generated', 'email_sent')
    search_fields = ('email', 'payment_id')
    readonly_fields = ('created_at',)
