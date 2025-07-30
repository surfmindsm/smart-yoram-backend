# Supabase Storage Setup Guide

This guide explains how to set up Supabase Storage for the Smart Yoram backend.

## Required Storage Buckets

The application requires the following storage buckets to be created in your Supabase project:

1. **member-photos** - For storing member profile photos
2. **bulletins** - For storing bulletin files (PDF, images)
3. **documents** - For storing other church documents

## Setup Instructions

1. **Log in to Supabase Dashboard**
   - Go to your project at https://app.supabase.com
   - Navigate to the Storage section in the sidebar

2. **Create Required Buckets**
   
   For each bucket (member-photos, bulletins, documents):
   
   a. Click "New bucket"
   b. Enter the bucket name exactly as listed above
   c. Set the bucket to "Public" if you want files to be accessible via URL
   d. Click "Save"

3. **Configure Bucket Policies (Optional)**
   
   If you want to restrict access, you can add RLS policies:
   
   ```sql
   -- Example: Allow authenticated users to upload
   CREATE POLICY "Allow authenticated uploads" ON storage.objects
   FOR INSERT TO authenticated
   USING (bucket_id = 'member-photos');
   
   -- Example: Allow public to view
   CREATE POLICY "Allow public viewing" ON storage.objects
   FOR SELECT TO public
   USING (bucket_id = 'member-photos');
   ```

4. **Update Environment Variables**
   
   Ensure your `.env` file has the correct Supabase configuration:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   ```

## File Size Limits

The application enforces a 5MB file size limit. You can adjust this in:
- Backend: `app/utils/storage.py` - `MAX_FILE_SIZE` variable
- Supabase: Dashboard > Storage > Bucket settings

## Supported File Types

- **Member Photos**: .jpg, .jpeg, .png, .gif, .webp
- **Bulletins**: All image types + .pdf, .doc, .docx
- **Documents**: .pdf, .doc, .docx, .xlsx, .xls

## Testing

After setup, you can test the storage functionality:

```bash
python test_storage.py
```

This will:
1. Upload a test member photo
2. Upload a test bulletin file
3. Test photo deletion

## Troubleshooting

1. **"Bucket not found" error**
   - Ensure buckets are created with exact names (case-sensitive)
   - Check that your Supabase URL and anon key are correct

2. **"Unauthorized" error**
   - Check RLS policies if enabled
   - Ensure the anon key has proper permissions

3. **File upload fails**
   - Check file size (must be under 5MB)
   - Verify file type is supported
   - Check network connectivity to Supabase