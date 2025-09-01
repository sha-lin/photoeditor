import cv2
import numpy as np
from PIL import Image, ImageFilter
import os
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import io

class ImageProcessor:
    
    @staticmethod
    def compress_image(image_path, quality=85):
        """Compress image while maintaining aspect ratio"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Create a BytesIO object to save compressed image
                output = io.BytesIO()
                
                # Save with specified quality
                img.save(output, format='JPEG', quality=quality, optimize=True)
                output.seek(0)
                
                return ContentFile(output.getvalue())
        except Exception as e:
            print(f"Error compressing image: {e}")
            return None
    
    @staticmethod
    def remove_watermark_simple(image_path):
        """Simple watermark removal using inpainting"""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return None
                
            # Convert to grayscale for mask creation
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Create mask for potential watermark areas
            # This is a simple approach - you may need to adjust based on your needs
            mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)[1]
            
            # Dilate the mask to cover watermark completely
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.dilate(mask, kernel, iterations=2)
            
            # Apply inpainting
            result = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
            
            # Convert back to PIL Image and save to BytesIO
            result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(result_rgb)
            
            output = io.BytesIO()
            pil_image.save(output, format='JPEG', quality=90)
            output.seek(0)
            
            return ContentFile(output.getvalue())
            
        except Exception as e:
            print(f"Error removing watermark: {e}")
            return None
    
    @staticmethod
    def remove_watermark_advanced(image_path):
        """Advanced watermark removal using multiple techniques"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            # Convert to different color spaces for analysis
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            
            # Create mask based on color and brightness thresholds
            # Adjust these values based on typical watermark characteristics
            mask1 = cv2.inRange(hsv, (0, 0, 200), (180, 30, 255))  # Light colors
            mask2 = cv2.inRange(lab, (200, 0, 0), (255, 255, 255))  # Bright areas
            
            # Combine masks
            mask = cv2.bitwise_or(mask1, mask2)
            
            # Morphological operations to clean up the mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Apply inpainting with different algorithms
            result1 = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
            result2 = cv2.inpaint(img, mask, 3, cv2.INPAINT_NS)
            
            # Blend results (you can choose one or blend)
            result = cv2.addWeighted(result1, 0.7, result2, 0.3, 0)
            
            # Convert and save
            result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(result_rgb)
            
            output = io.BytesIO()
            pil_image.save(output, format='JPEG', quality=90)
            output.seek(0)
            
            return ContentFile(output.getvalue())
            
        except Exception as e:
            print(f"Error in advanced watermark removal: {e}")
            return None

def get_file_size(file_field):
    """Get file size in bytes"""
    try:
        return file_field.size
    except:
        return 0