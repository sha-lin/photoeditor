from django import forms
from .models import Photo

class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['original_image', 'compress_image', 'remove_watermark', 'compression_quality']
        widgets = {
            'original_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'multiple': False
            }),
            'compress_image': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'remove_watermark': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'compression_quality': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 100,
                'value': 85
            })
        }
    
    def clean_compression_quality(self):
        quality = self.cleaned_data.get('compression_quality')
        if quality and (quality < 1 or quality > 100):
            raise forms.ValidationError("Quality must be between 1 and 100")
        return quality