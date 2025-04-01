import os
import threading
from .models import VideoProcessing
from .utils import upload_to_cloudinary, update_supabase
from Components.YoutubeDownloader import download_youtube_video
from Components.Edit import extractAudio, crop_video
from Components.Transcription import transcribeAudio
from Components.LanguageTasks import GetHighlight
from Components.FaceCrop import crop_to_vertical, combine_videos

def ensure_directories():
    """Ensure all necessary directories exist"""
    directories = ['media', 'videos']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

def process_video_task(video_processing_id):
    """
    Process a video in a background thread
    """
    video_processing = VideoProcessing.objects.get(id=video_processing_id)
    
    try:
        video_processing.status = 'PROCESSING'
        video_processing.save()
        
        # Ensure directories exist
        ensure_directories()
        
        # For testing without processing the entire pipeline
        test_mode = os.getenv('TEST_MODE', 'False').lower() == 'true'
        
        if test_mode:
            # In test mode, we'll skip actual processing and just upload a sample video
            final_path = "media/final_15.mp4"
            if not os.path.exists(final_path):
                # Try to use an existing video file if available 
                existing_videos = []
                for vid_file in os.listdir('videos'):
                    if vid_file.endswith('.mp4'):
                        existing_videos.append(os.path.join('videos', vid_file))
                
                # If any videos exist, copy the first one
                if existing_videos:
                    import shutil
                    shutil.copy(existing_videos[0], final_path)
                    print(f"Copied {existing_videos[0]} to {final_path} for testing")
                else:
                    video_processing.error_message = f"Test file {final_path} not found and no existing videos to copy. Please ensure a test video exists."
                    video_processing.status = 'FAILED'
                    video_processing.save()
                    return
        else:
            # Download the video
            vid = download_youtube_video(video_processing.youtube_url)
            if not vid:
                video_processing.error_message = "Unable to download the video"
                video_processing.status = 'FAILED'
                video_processing.save()
                return
                
            vid = vid.replace(".webm", ".mp4")
            video_processing.original_video_path = vid
            video_processing.save()
            
            # Extract audio
            audio = extractAudio(vid)
            if not audio:
                video_processing.error_message = "No audio file found"
                video_processing.status = 'FAILED'
                video_processing.save()
                return
                
            # Transcribe audio
            transcriptions = transcribeAudio(audio)
            if len(transcriptions) == 0:
                video_processing.error_message = "No transcriptions found"
                video_processing.status = 'FAILED'
                video_processing.save()
                return
                
            trans_text = ""
            for text, start, end in transcriptions:
                trans_text += (f"{start} - {end}: {text}")
            
            # Get highlight timestamps
            start, stop = GetHighlight(trans_text)
            if start == 0 or stop == 0:
                video_processing.error_message = "Error in getting highlight"
                video_processing.status = 'FAILED'
                video_processing.save()
                return
                
            # Create output paths
            output = "media/Out.mp4"
            
            # Crop video to highlight section
            crop_video(vid, output, start, stop)
            
            # Crop to vertical
            cropped = "media/cropped.mp4"
            crop_to_vertical(output, cropped)
            
            # Combine videos
            final_path = f"media/final_{video_processing_id}.mp4"
            combine_videos(output, cropped, final_path)
        
        # Upload to Cloudinary
        upload_result = upload_to_cloudinary(final_path, f"user_{video_processing.username}")
        if upload_result:
            # Update VideoProcessing record with Cloudinary URL
            print("Cloudinary URL:", upload_result['url'])
            video_processing.cloudinary_url = upload_result['url']
            video_processing.cloudinary_public_id = upload_result['public_id']
            video_processing.final_video_path = final_path
            video_processing.status = 'COMPLETED'
            video_processing.save()
            
            # Update Supabase
            update_supabase(
                video_processing.username,
                video_processing.youtube_url,
                video_processing.cloudinary_url
            )
            return
        else:
            video_processing.error_message = "Failed to upload to Cloudinary"
            video_processing.status = 'FAILED'
            video_processing.save()
    
    except Exception as e:
        video_processing.status = 'FAILED'
        video_processing.error_message = str(e)
        video_processing.save()

def start_processing_video(video_processing_id):
    """
    Start a background thread to process the video
    """
    thread = threading.Thread(target=process_video_task, args=(video_processing_id,))
    thread.daemon = True
    thread.start()
    return thread 