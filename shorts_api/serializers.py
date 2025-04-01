from rest_framework import serializers
from .models import VideoProcessing

class VideoProcessingSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoProcessing
        fields = ['id', 'username', 'youtube_url', 'status', 'cloudinary_url', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'cloudinary_url', 'created_at', 'updated_at']

class VideoRequestSerializer(serializers.Serializer):
    url = serializers.URLField(required=True)
    username = serializers.CharField(required=True, max_length=100) 