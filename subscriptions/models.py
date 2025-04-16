from django.db import models

# Create your models here.

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    is_paid = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    pdf_generated = models.BooleanField(default=False)
    pdf_path = models.CharField(max_length=255, blank=True, null=True)
    email_sent = models.BooleanField(default=False)
    
    def __str__(self):
        return self.email
