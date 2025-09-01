from django.db import models
from django.core.validators import FileExtensionValidator
import uuid

class Photo(models.Model):
    PROCESSING_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_image = models.ImageField(
        upload_to='uploads/original/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'bmp', 'tiff'])]
    )
    compressed_image = models.ImageField(upload_to='uploads/compressed/', blank=True, null=True)
    watermark_removed_image = models.ImageField(upload_to='uploads/watermark_removed/', blank=True, null=True)
    
    # Processing options
    compress_image = models.BooleanField(default=False)
    remove_watermark = models.BooleanField(default=False)
    compression_quality = models.IntegerField(default=85, help_text="Quality percentage (1-100)")
    
    # Status tracking
    status = models.CharField(max_length=20, choices=PROCESSING_CHOICES, default='pending')
    original_size = models.IntegerField(blank=True, null=True, help_text="Size in bytes")
    compressed_size = models.IntegerField(blank=True, null=True, help_text="Size in bytes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Photo {self.id} - {self.status}"
    
    def get_compression_ratio(self):
        if self.original_size and self.compressed_size:
            return round((1 - self.compressed_size / self.original_size) * 100, 2)
        return 0