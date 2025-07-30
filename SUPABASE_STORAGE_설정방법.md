# Supabase Storage 설정 방법

## 1. Supabase 대시보드 접속
1. https://app.supabase.com 로 이동
2. 프로젝트 선택 (smart-yoram 프로젝트)

## 2. Storage 버킷 생성

### 왼쪽 메뉴에서 "Storage" 클릭

### 다음 3개의 버킷을 생성해야 합니다:
1. **member-photos** (교인 사진용)
2. **bulletins** (주보 파일용)
3. **documents** (기타 문서용)

### 각 버킷 생성 방법:
1. "New bucket" 버튼 클릭
2. 버킷 이름 입력 (위의 이름 그대로 사용)
3. "Public bucket" 체크 (파일을 URL로 접근 가능하게 함)
4. "Save" 클릭

## 3. 버킷 정책 설정 (선택사항)

각 버킷에 대해 다음 정책을 추가할 수 있습니다:

### member-photos 버킷 정책
```sql
-- 인증된 사용자만 업로드 가능
CREATE POLICY "Allow authenticated uploads" ON storage.objects
FOR INSERT TO authenticated
USING (bucket_id = 'member-photos');

-- 모든 사용자가 조회 가능
CREATE POLICY "Allow public viewing" ON storage.objects
FOR SELECT TO public
USING (bucket_id = 'member-photos');

-- 인증된 사용자가 자신의 교회 파일만 삭제 가능
CREATE POLICY "Allow authenticated deletes" ON storage.objects
FOR DELETE TO authenticated
USING (bucket_id = 'member-photos');
```

## 4. 설정 확인

1. 각 버킷이 생성되었는지 확인
2. Public 설정이 되어있는지 확인
3. 파일 크기 제한이 5MB로 설정되어 있는지 확인

## 5. 테스트

프론트엔드에서 다시 사진 업로드를 시도해보세요.

## 문제 해결

### "Bucket not found" 에러
- 버킷 이름이 정확한지 확인 (대소문자 구분)
- 버킷이 실제로 생성되었는지 확인

### "Unauthorized" 에러  
- .env 파일의 SUPABASE_ANON_KEY가 올바른지 확인
- 버킷이 Public으로 설정되어 있는지 확인

### 파일 업로드 실패
- 파일 크기가 5MB 이하인지 확인
- 파일 형식이 지원되는지 확인 (jpg, png, gif, webp)