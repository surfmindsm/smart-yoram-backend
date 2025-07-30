-- Supabase Storage RLS Policies for Smart Yoram

-- member-photos 버킷 정책
-- 1. 인증된 사용자만 업로드 가능
CREATE POLICY "Allow authenticated uploads" ON storage.objects
FOR INSERT TO authenticated
USING (bucket_id = 'member-photos');

-- 2. 모든 사용자가 조회 가능
CREATE POLICY "Allow public viewing" ON storage.objects
FOR SELECT TO public
USING (bucket_id = 'member-photos');

-- 3. 인증된 사용자가 삭제 가능
CREATE POLICY "Allow authenticated deletes" ON storage.objects
FOR DELETE TO authenticated
USING (bucket_id = 'member-photos');

-- 4. 인증된 사용자가 업데이트 가능
CREATE POLICY "Allow authenticated updates" ON storage.objects
FOR UPDATE TO authenticated
USING (bucket_id = 'member-photos');

-- bulletins 버킷 정책
-- 1. 인증된 사용자만 업로드 가능
CREATE POLICY "Allow authenticated uploads bulletins" ON storage.objects
FOR INSERT TO authenticated
USING (bucket_id = 'bulletins');

-- 2. 모든 사용자가 조회 가능
CREATE POLICY "Allow public viewing bulletins" ON storage.objects
FOR SELECT TO public
USING (bucket_id = 'bulletins');

-- 3. 인증된 사용자가 삭제 가능
CREATE POLICY "Allow authenticated deletes bulletins" ON storage.objects
FOR DELETE TO authenticated
USING (bucket_id = 'bulletins');

-- documents 버킷 정책
-- 1. 인증된 사용자만 업로드 가능
CREATE POLICY "Allow authenticated uploads documents" ON storage.objects
FOR INSERT TO authenticated
USING (bucket_id = 'documents');

-- 2. 모든 사용자가 조회 가능
CREATE POLICY "Allow public viewing documents" ON storage.objects
FOR SELECT TO public
USING (bucket_id = 'documents');

-- 3. 인증된 사용자가 삭제 가능
CREATE POLICY "Allow authenticated deletes documents" ON storage.objects
FOR DELETE TO authenticated
USING (bucket_id = 'documents');