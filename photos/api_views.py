from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Photo
from .serializers import PhotoSerializer
import threading
from .views import process_photo_async

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    
    def perform_create(self, serializer):
        photo = serializer.save()
        # Start processing
        thread = threading.Thread(target=process_photo_async, args=(photo.id,))
        thread.daemon = True
        thread.start()
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        photo = self.get_object()
        return Response({
            'status': photo.status,
            'compression_ratio': photo.get_compression_ratio(),
            'has_compressed': bool(photo.compressed_image),
            'has_watermark_removed': bool(photo.watermark_removed_image),
        })