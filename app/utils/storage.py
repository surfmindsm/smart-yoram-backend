"""Supabase Storage utilities for file management."""
import os
import uuid
from typing import Optional, Tuple
from datetime import datetime
from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Supabase client
supabase: Client = create_client(
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_ANON_KEY
)

# Storage buckets
MEMBER_PHOTOS_BUCKET = "member-photos"
BULLETINS_BUCKET = "bulletins"
DOCUMENTS_BUCKET = "documents"

# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".xlsx", ".xls"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def ensure_buckets_exist():
    """Ensure all required storage buckets exist."""
    buckets = [MEMBER_PHOTOS_BUCKET, BULLETINS_BUCKET, DOCUMENTS_BUCKET]
    
    try:
        existing_buckets = supabase.storage.list_buckets()
        existing_names = [b.get('name') for b in existing_buckets]
        
        for bucket_name in buckets:
            if bucket_name not in existing_names:
                # Try to create bucket - this requires service key, not anon key
                try:
                    supabase.storage.create_bucket(bucket_name)
                    logger.info(f"Created storage bucket: {bucket_name}")
                except Exception as create_error:
                    # RLS policy prevents bucket creation with anon key, but that's OK
                    logger.debug(f"Bucket {bucket_name} creation skipped (likely already exists or RLS policy): {create_error}")
    except Exception as e:
        logger.error(f"Error ensuring buckets exist: {e}")


def generate_unique_filename(original_filename: str, prefix: str = "") -> str:
    """Generate a unique filename with timestamp and UUID."""
    file_ext = os.path.splitext(original_filename)[1].lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    
    if prefix:
        return f"{prefix}_{timestamp}_{unique_id}{file_ext}"
    return f"{timestamp}_{unique_id}{file_ext}"


def validate_image_file(filename: str, file_size: int) -> Tuple[bool, Optional[str]]:
    """Validate image file type and size."""
    file_ext = os.path.splitext(filename)[1].lower()
    
    if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
        return False, f"File type not allowed. Allowed types: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
    
    if file_size > MAX_FILE_SIZE:
        return False, f"File size too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
    
    return True, None


def upload_member_photo(
    file_content: bytes,
    filename: str,
    church_id: int,
    member_id: int
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Upload member photo to Supabase Storage.
    
    Returns: (success, file_url, error_message)
    """
    try:
        # Validate file
        is_valid, error_msg = validate_image_file(filename, len(file_content))
        if not is_valid:
            return False, None, error_msg
        
        # Generate unique filename with path
        unique_filename = generate_unique_filename(
            filename, 
            f"{church_id}/{member_id}"
        )
        
        # Upload to Supabase Storage
        response = supabase.storage.from_(MEMBER_PHOTOS_BUCKET).upload(
            path=unique_filename,
            file=file_content,
            file_options={"content-type": "image/jpeg"}  # You might want to detect this
        )
        
        # Get public URL
        public_url = supabase.storage.from_(MEMBER_PHOTOS_BUCKET).get_public_url(unique_filename)
        
        # Remove trailing '?' if present
        if public_url.endswith('?'):
            public_url = public_url[:-1]
        
        return True, public_url, None
        
    except Exception as e:
        logger.error(f"Error uploading member photo: {e}")
        return False, None, str(e)


def delete_member_photo(photo_url: str) -> Tuple[bool, Optional[str]]:
    """
    Delete member photo from Supabase Storage.
    
    Returns: (success, error_message)
    """
    try:
        # Extract file path from URL
        # URL format: https://xxx.supabase.co/storage/v1/object/public/member-photos/path/to/file.jpg
        if "/storage/v1/object/public/" in photo_url:
            parts = photo_url.split("/storage/v1/object/public/")
            if len(parts) > 1:
                bucket_and_path = parts[1]
                if bucket_and_path.startswith(f"{MEMBER_PHOTOS_BUCKET}/"):
                    file_path = bucket_and_path.replace(f"{MEMBER_PHOTOS_BUCKET}/", "")
                    
                    # Delete from Supabase Storage
                    response = supabase.storage.from_(MEMBER_PHOTOS_BUCKET).remove([file_path])
                    return True, None
        
        return False, "Invalid photo URL"
        
    except Exception as e:
        logger.error(f"Error deleting member photo: {e}")
        return False, str(e)


def upload_bulletin(
    file_content: bytes,
    filename: str,
    church_id: int,
    bulletin_date: str
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Upload bulletin file to Supabase Storage.
    
    Returns: (success, file_url, error_message)
    """
    try:
        # Validate file type
        file_ext = os.path.splitext(filename)[1].lower()
        allowed_extensions = ALLOWED_IMAGE_EXTENSIONS.union(ALLOWED_DOCUMENT_EXTENSIONS)
        
        if file_ext not in allowed_extensions:
            return False, None, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        
        if len(file_content) > MAX_FILE_SIZE:
            return False, None, f"File size too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        
        # Generate unique filename with path
        unique_filename = generate_unique_filename(
            filename,
            f"{church_id}/{bulletin_date}"
        )
        
        # Upload to Supabase Storage
        response = supabase.storage.from_(BULLETINS_BUCKET).upload(
            path=unique_filename,
            file=file_content
        )
        
        # Get public URL
        public_url = supabase.storage.from_(BULLETINS_BUCKET).get_public_url(unique_filename)
        
        return True, public_url, None
        
    except Exception as e:
        logger.error(f"Error uploading bulletin: {e}")
        return False, None, str(e)


def get_file_url(bucket: str, file_path: str) -> str:
    """Get public URL for a file in storage."""
    return supabase.storage.from_(bucket).get_public_url(file_path)


# Initialize buckets when module is imported
# Note: This may fail due to RLS policies, but that's okay
try:
    ensure_buckets_exist()
except Exception as e:
    logger.warning(f"Could not ensure buckets exist (likely due to RLS policies): {e}")