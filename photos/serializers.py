from rest_framework import serializers
from .models import Photo

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'
        read_only_fields = ('id', 'status', 'original_size', 'compressed_size', 'created_at', 'updated_at')