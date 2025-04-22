from django.contrib import admin
from django.utils.html import format_html
from .models import Subscriber
from .mongodb_utils import get_subscribers_from_mongodb, get_subscriber_by_email

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_paid', 'created_at', 'pdf_generated', 'email_sent', 'mongodb_status')
    list_filter = ('is_paid', 'pdf_generated', 'email_sent')
    search_fields = ('email', 'payment_id')
    readonly_fields = ('created_at', 'mongodb_info')
    
    def mongodb_status(self, obj):
        """Display whether the subscriber exists in MongoDB."""
        mongodb_record = get_subscriber_by_email(obj.email)
        if mongodb_record:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    
    mongodb_status.short_description = 'MongoDB'
    
    def mongodb_info(self, obj):
        """Display detailed MongoDB information for this subscriber."""
        mongodb_record = get_subscriber_by_email(obj.email)
        if not mongodb_record:
            return "Not found in MongoDB"
        
        # Format MongoDB data
        html = "<h3>MongoDB Data:</h3>"
        html += "<table>"
        for key, value in mongodb_record.items():
            if key != '_id':  # Skip MongoDB ID
                html += f"<tr><th>{key}</th><td>{value}</td></tr>"
        html += "</table>"
        
        return format_html(html)
    
    mongodb_info.short_description = 'MongoDB Info'
