# Supabase Storage RLS 설정 방법

## 방법 1: RLS 비활성화 (빠른 테스트용)

1. Supabase Dashboard에서 Storage 섹션으로 이동
2. 각 버킷 옆의 점 3개 메뉴 클릭
3. "Edit bucket" 선택
4. "Enable RLS" 체크 해제
5. Save

## 방법 2: RLS 정책 설정 (권장)

### SQL Editor에서 실행:

1. Supabase Dashboard 왼쪽 메뉴에서 "SQL Editor" 클릭
2. "New query" 클릭
3. 다음 SQL 실행:

```sql
-- 기존 정책 삭제 (있을 경우)
DROP POLICY IF EXISTS "Allow authenticated uploads" ON storage.objects;
DROP POLICY IF EXISTS "Allow public viewing" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated deletes" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated updates" ON storage.objects;

-- member-photos 버킷 정책
CREATE POLICY "member-photos insert" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'member-photos');

CREATE POLICY "member-photos select" ON storage.objects
FOR SELECT USING (bucket_id = 'member-photos');

CREATE POLICY "member-photos delete" ON storage.objects
FOR DELETE USING (bucket_id = 'member-photos');

CREATE POLICY "member-photos update" ON storage.objects
FOR UPDATE USING (bucket_id = 'member-photos');

-- bulletins 버킷 정책
CREATE POLICY "bulletins insert" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'bulletins');

CREATE POLICY "bulletins select" ON storage.objects
FOR SELECT USING (bucket_id = 'bulletins');

CREATE POLICY "bulletins delete" ON storage.objects
FOR DELETE USING (bucket_id = 'bulletins');

-- documents 버킷 정책
CREATE POLICY "documents insert" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'documents');

CREATE POLICY "documents select" ON storage.objects
FOR SELECT USING (bucket_id = 'documents');

CREATE POLICY "documents delete" ON storage.objects
FOR DELETE USING (bucket_id = 'documents');
```

## 방법 3: Anon 키를 위한 간단한 정책

```sql
-- 모든 작업을 허용하는 간단한 정책
CREATE POLICY "Allow all for anon" ON storage.objects
FOR ALL USING (true) WITH CHECK (true);
```

## 확인 방법

정책 설정 후:
1. 프론트엔드에서 다시 사진 업로드 시도
2. 에러가 계속 발생하면 브라우저 개발자 도구에서 네트워크 탭 확인
3. 응답 내용 확인