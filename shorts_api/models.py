from django.db import models

# Create your models here.

class VideoProcessing(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )
    
    username = models.CharField(max_length=100, default='anonymous')
    youtube_url = models.URLField()
    original_video_path = models.CharField(max_length=512, blank=True, null=True)
    final_video_path = models.CharField(max_length=512, blank=True, null=True)
    cloudinary_url = models.URLField(blank=True, null=True)
    cloudinary_public_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Video Processing: {self.username} - {self.youtube_url} - {self.status}"

    class Meta:
        ordering = ['-created_at']
