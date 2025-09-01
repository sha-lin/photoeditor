from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io
from .models import Photo

class PhotoProcessingTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
    def create_test_image(self):
        """Create a test image file"""
        image = Image.new('RGB', (100, 100), color='red')
        img_file = io.BytesIO()
        image.save(img_file, format='JPEG')
        img_file.seek(0)
        return SimpleUploadedFile("test.jpg", img_file.getvalue(), content_type="image/jpeg")
    
    def test_photo_upload(self):
        """Test basic photo upload"""
        test_image = self.create_test_image()
        
        response = self.client.post(reverse('upload_photo'), {
            'original_image': test_image,
            'compress_image': True,
            'compression_quality': 80
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after successful upload
        self.assertEqual(Photo.objects.count(), 1)
        
        photo = Photo.objects.first()
        self.assertTrue(photo.compress_image)
        self.assertEqual(photo.compression_quality, 80)
    
    def test_photo_detail_view(self):
        """Test photo detail view"""
        test_image = self.create_test_image()
        photo = Photo.objects.create(
            original_image=test_image,
            compress_image=True
        )
        
        response = self.client.get(reverse('photo_detail', kwargs={'photo_id': photo.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Photo Processing Status')