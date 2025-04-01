import os
import cloudinary
import cloudinary.uploader
from supabase import create_client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def upload_to_cloudinary(file_path, public_id_prefix='shorts'):
    """
    Upload a video file to Cloudinary and return the URL
    """
    try:
        # Get environment variables directly
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        api_key = os.getenv('CLOUDINARY_API_KEY')
        api_secret = os.getenv('CLOUDINARY_API_SECRET')
        
        # Debug logging
        logger.info(f"Direct env - Cloudinary cloud_name: {cloud_name}")
        logger.info(f"Direct env - Cloudinary API key: {api_key}")
        logger.info(f"Direct env - Cloudinary API secret: {api_secret[:5]}..." if api_secret else 'None')
        
        # Also log from settings for comparison
        logger.info(f"Settings - Cloudinary cloud_name: {settings.CLOUDINARY['cloud_name']}")
        logger.info(f"Settings - Cloudinary API key: {settings.CLOUDINARY['api_key']}")
        logger.info(f"Settings - Cloudinary API secret: {settings.CLOUDINARY['api_secret'][:5]}..." if settings.CLOUDINARY['api_secret'] else 'None')
        
        # Configure cloudinary with direct env vars
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        
        # Generate a unique public_id based on the filename
        filename = os.path.basename(file_path)
        public_id = f"{public_id_prefix}/{os.path.splitext(filename)[0]}"
        
        # Ensure the file exists
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
            
        # Upload the file
        upload_result = cloudinary.uploader.upload(
            file_path,
            resource_type="video",
            public_id=public_id,
            overwrite=True,
            folder="shorts"
        )
        
        return {
            'url': upload_result['secure_url'],
            'public_id': upload_result['public_id']
        }
    except Exception as e:
        logger.error(f"Cloudinary upload error: {str(e)}")
        return None

def update_supabase(username, youtube_url, cloudinary_url):
    """
    Update the Supabase database with the video information
    """
    try:
        # Get environment variables directly
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        supabase_table = os.getenv('SUPABASE_TABLE', 'shorts')
        
        # Debug logging
        logger.info(f"Direct env - Supabase URL: {supabase_url}")
        logger.info(f"Direct env - Supabase key: {supabase_key[:10]}..." if supabase_key else 'None')
        logger.info(f"Direct env - Supabase table: {supabase_table}")
        
        # Create Supabase client with direct env vars
        supabase = create_client(supabase_url, supabase_key)
        
        # Insert the record
        response = supabase.table(supabase_table).insert({
            "username": username,
            "youtube_url": youtube_url,
            "short_url": cloudinary_url,
            "created_at": "now()"
        }).execute()
        
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"Supabase update error: {str(e)}")
        return None 