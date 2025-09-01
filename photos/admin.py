from django.contrib import admin
from .models import Photo

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'compress_image', 'remove_watermark', 'original_size', 'compressed_size', 'created_at']
    list_filter = ['status', 'compress_image', 'remove_watermark', 'created_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'original_size', 'compressed_size']
    search_fields = ['id']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'status', 'created_at', 'updated_at')
        }),
        ('Images', {
            'fields': ('original_image', 'compressed_image', 'watermark_removed_image')
        }),
        ('Processing Options', {
            'fields': ('compress_image', 'compression_quality', 'remove_watermark')
        }),
        ('File Sizes', {
            'fields': ('original_size', 'compressed_size')
        })
    )