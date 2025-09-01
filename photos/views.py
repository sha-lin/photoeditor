from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.conf import settings
import os
import threading

from .models import Photo
from .forms import PhotoUploadForm
from .utils import ImageProcessor, get_file_size

def upload_photo(request):
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.original_size = get_file_size(photo.original_image)
            photo.save()
            
            # Process image in background
            thread = threading.Thread(target=process_photo_async, args=(photo.id,))
            thread.daemon = True
            thread.start()
            
            messages.success(request, 'Photo uploaded successfully! Processing will begin shortly.')
            return redirect('photo_detail', photo_id=photo.id)
    else:
        form = PhotoUploadForm()
    
    return render(request, 'photos/upload.html', {'form': form})

def process_photo_async(photo_id):
    """Process photo asynchronously"""
    try:
        photo = Photo.objects.get(id=photo_id)
        photo.status = 'processing'
        photo.save()
        
        processor = ImageProcessor()
        
        # Get the full path to the original image
        original_path = photo.original_image.path
        
        # Compress image if requested
        if photo.compress_image:
            compressed_content = processor.compress_image(
                original_path, 
                quality=photo.compression_quality
            )
            if compressed_content:
                filename = f"compressed_{os.path.basename(original_path)}"
                photo.compressed_image.save(filename, compressed_content, save=False)
                photo.compressed_size = get_file_size(photo.compressed_image)
        
        # Remove watermark if requested
        if photo.remove_watermark:
            # Use the compressed image if available, otherwise original
            source_path = photo.compressed_image.path if photo.compressed_image else original_path
            
            watermark_removed_content = processor.remove_watermark_advanced(source_path)
            if watermark_removed_content:
                filename = f"watermark_removed_{os.path.basename(original_path)}"
                photo.watermark_removed_image.save(filename, watermark_removed_content, save=False)
        
        photo.status = 'completed'
        photo.save()
        
    except Exception as e:
        try:
            photo = Photo.objects.get(id=photo_id)
            photo.status = 'failed'
            photo.save()
        except:
            pass
        print(f"Error processing photo {photo_id}: {e}")

def photo_detail(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    return render(request, 'photos/detail.html', {'photo': photo})

def photo_status(request, photo_id):
    """AJAX endpoint to check processing status"""
    photo = get_object_or_404(Photo, id=photo_id)
    data = {
        'status': photo.status,
        'compression_ratio': photo.get_compression_ratio(),
        'original_size': photo.original_size,
        'compressed_size': photo.compressed_size,
        'has_compressed': bool(photo.compressed_image),
        'has_watermark_removed': bool(photo.watermark_removed_image),
    }
    return JsonResponse(data)

def download_image(request, photo_id, image_type):
    """Download processed images"""
    photo = get_object_or_404(Photo, id=photo_id)
    
    if image_type == 'compressed' and photo.compressed_image:
        response = HttpResponse(photo.compressed_image.read(), content_type='image/jpeg')
        response['Content-Disposition'] = f'attachment; filename="compressed_{photo.id}.jpg"'
        return response
    elif image_type == 'watermark_removed' and photo.watermark_removed_image:
        response = HttpResponse(photo.watermark_removed_image.read(), content_type='image/jpeg')
        response['Content-Disposition'] = f'attachment; filename="watermark_removed_{photo.id}.jpg"'
        return response
    elif image_type == 'original':
        response = HttpResponse(photo.original_image.read(), content_type='image/jpeg')
        response['Content-Disposition'] = f'attachment; filename="original_{photo.id}.jpg"'
        return response
    
    return HttpResponse("Image not found", status=404)

def photo_list(request):
    photos = Photo.objects.all().order_by('-created_at')
    return render(request, 'photos/list.html', {'photos': photos})



# Add this to your existing views.py

def batch_upload(request):
    """Handle multiple file uploads"""
    if request.method == 'POST':
        files = request.FILES.getlist('images')
        compress_images = request.POST.get('compress_images') == 'on'
        remove_watermarks = request.POST.get('remove_watermarks') == 'on'
        compression_quality = int(request.POST.get('compression_quality', 85))
        
        photo_ids = []
        for file in files:
            photo = Photo.objects.create(
                original_image=file,
                compress_image=compress_images,
                remove_watermark=remove_watermarks,
                compression_quality=compression_quality,
                original_size=get_file_size(file)
            )
            photo_ids.append(str(photo.id))
            
            # Process each photo
            thread = threading.Thread(target=process_photo_async, args=(photo.id,))
            thread.daemon = True
            thread.start()
        
        messages.success(request, f'{len(files)} photos uploaded and processing started!')
        return redirect('batch_status', photo_ids=','.join(photo_ids))
    
    return render(request, 'photos/batch_upload.html')

def batch_status(request, photo_ids):
    """Show status of batch processing"""
    photo_id_list = photo_ids.split(',')
    photos = Photo.objects.filter(id__in=photo_id_list).order_by('-created_at')
    return render(request, 'photos/batch_status.html', {'photos': photos})