# from asyncio import subprocess
import subprocess
import os
from django.conf import settings
from django.core.files.storage import default_storage
from PIL import Image  # For image manipulation (requires Pillow: pip install Pillow)

class MediaHandler:
    upload_to = 'media/'  # Default upload directory for media files
    @staticmethod
    def get_media_url(file_path):
        """
        Returns the full URL for a given media file path.
        Handles both local and potentially cloud storage URLs.
        """
        if file_path:
            return default_storage.url(file_path)
        return None

    @staticmethod
    def delete_media_file(file_path):
        """
        Deletes a media file from storage if it exists.
        """
        if file_path and default_storage.exists(file_path):
            default_storage.delete(file_path)
            return True
        return False

    @staticmethod
    def resize_image(image_file, size=(300, 300), quality=85):
        """
        Resizes an image file to the specified dimensions and quality.
        Returns the path to the resized image (or None if an error occurs).
        """
        try:
            img = Image.open(image_file)
            img.thumbnail(size, Image.Resampling.LANCZOS)  # Use a high-quality resampling filter

            name, ext = os.path.splitext(image_file.name)
            resized_name = f"{name}_resized{ext.lower()}"
            resized_path = os.path.join(os.path.dirname(image_file.name), resized_name)

            # Save the resized image to the default storage
            with default_storage.open(resized_path, 'wb') as f:
                img.save(f, format=img.format, quality=quality, optimize=True)

            return resized_path

        except Exception as e:
            print(f"Error resizing image {image_file.name}: {e}")
            return None

    @staticmethod
    def get_file_extension(file_path):
        """
        Extracts and returns the lowercase extension of a file.
        """
        if file_path:
            _, ext = os.path.splitext(file_path)
            return ext.lower().lstrip('.')
        return None

    @staticmethod
    def is_image(file_path):
        """
        Checks if a file path likely belongs to an image based on its extension.
        """
        image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
        ext = MediaHandler.get_file_extension(file_path)
        return ext in image_extensions

    @staticmethod
    def is_video(file_path):
        """
        Checks if a file path likely belongs to a video based on its extension.
        """
        video_extensions = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'ogv'}
        ext = MediaHandler.get_file_extension(file_path)
        return ext in video_extensions

    @staticmethod
    def is_audio(file_path):
        """
        Checks if a file path likely belongs to an audio file based on its extension.
        """
        audio_extensions = {'mp3', 'wav', 'ogg', 'flac', 'aac'}
        ext = MediaHandler.get_file_extension(file_path)
        return ext in audio_extensions
    
    @staticmethod
    def is_document(file_path):
        """
        Checks if a file path likely belongs to a document based on its extension.
        """
        document_extensions = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt'}
        ext = MediaHandler.get_file_extension(file_path)
        return ext in document_extensions

    @staticmethod
    def optimize_video(video_file, output_format='mp4', resolution=None, bitrate=None):
        """
        Optimizes a video file using ffmpeg.
        Requires ffmpeg to be installed on the system.

        Returns:
            The relative path to the optimized video file in storage, or None if an error occurs.
        """
        if not MediaHandler.is_video(video_file.name):
            print(f"Error: {video_file.name} is not a recognized video format.")
            return None

        try:
            # Get absolute input path
            if hasattr(video_file, "temporary_file_path"):
                input_path = video_file.temporary_file_path()
            elif hasattr(video_file, "path") and os.path.exists(video_file.path):
                input_path = video_file.path
            else:
                # Ensure file is saved locally before optimization
                with default_storage.open(video_file.name, "wb+") as f:
                    for chunk in video_file.chunks():
                        f.write(chunk)
                input_path = default_storage.path(video_file.name)

            # Build clean relative + full paths
            base, ext = os.path.splitext(os.path.basename(video_file.name))
            dir_name = os.path.dirname(video_file.name)
            optimized_name = f"{base}_optimized.{output_format.lower()}"
            optimized_path_relative = os.path.join(dir_name, optimized_name)
            optimized_path_full = default_storage.path(optimized_path_relative)

            # Build ffmpeg command
            command = ['ffmpeg', '-y', '-i', input_path]  # -y to overwrite if exists
            if resolution:
                command.extend(['-vf', f'scale={resolution}'])
            if bitrate:
                command.extend(['-b:v', bitrate])
            command.extend(['-c:v', 'libx264', '-preset', 'fast', '-c:a', 'aac', optimized_path_full])

            print("Running ffmpeg:", " ".join(command))

            # Run ffmpeg
            process = subprocess.run(command, capture_output=True, text=True, check=True)
            print("Video optimization successful:", process.stdout)

            # Save optimized file back to storage
            with open(optimized_path_full, 'rb') as f:
                optimized_file = default_storage.save(optimized_path_relative, f)

            # Cleanup temp file
            if os.path.exists(optimized_path_full):
                os.remove(optimized_path_full)

            return optimized_file

        except FileNotFoundError:
            print("Error: ffmpeg not found. Please ensure it is installed and in your system's PATH.")
            return None
        except subprocess.CalledProcessError as e:
            print(f"Error optimizing video {video_file.name}: {e.stderr}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during video optimization: {e}")
            return None
            
