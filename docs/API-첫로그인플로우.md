# 첫 로그인 플로우 API 문서

## 개요
교인이 처음 가입할 때 임시 비밀번호를 제공받고, 첫 로그인 시 비밀번호 변경과 QR 코드 생성을 완료해야 하는 플로우입니다.

## 플로우 순서

### 1. 관리자가 교인 계정 생성
관리자나 교역자가 교인의 계정을 생성합니다.

**Endpoint:** `POST /api/v1/members/{member_id}/create-account`

**권한:** admin, minister

**Response:**
```json
{
    "member_id": 123,
    "member_name": "홍길동",
    "user_id": 456,
    "email": "hong@example.com",
    "username": "hong@example.com",
    "temporary_password": "Temp123!@#",
    "is_first": true,
    "message": "Account created successfully. Please share the temporary password with the member."
}
```

### 2. 교인이 임시 비밀번호로 로그인
교인이 받은 임시 비밀번호로 첫 로그인을 시도합니다.

**Endpoint:** `POST /api/v1/auth/login/access-token`

**Request:**
```json
{
    "username": "hong@example.com",
    "password": "Temp123!@#"
}
```

**Response:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "user": {
        "id": 456,
        "email": "hong@example.com",
        "username": "hong@example.com",
        "full_name": "홍길동",
        "church_id": 1,
        "role": "member",
        "is_active": true,
        "is_superuser": false,
        "is_first": true  // 첫 로그인 여부
    }
}
```

### 3. 첫 로그인 상태 확인
앱에서 사용자가 첫 로그인인지 확인합니다.

**Endpoint:** `GET /api/v1/auth/check-first-time`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
    "is_first": true,
    "user_id": 456,
    "email": "hong@example.com"
}
```

### 4. 첫 로그인 설정 완료
비밀번호 변경과 QR 코드 생성을 한 번에 처리합니다.

**Endpoint:** `POST /api/v1/auth/complete-first-time-setup`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request:**
```json
{
    "new_password": "MyNewPassword123!"
}
```

**Response:**
```json
{
    "id": 456,
    "email": "hong@example.com",
    "username": "hong@example.com",
    "full_name": "홍길동",
    "church_id": 1,
    "role": "member",
    "is_active": true,
    "is_superuser": false,
    "is_first": false  // 이제 false로 변경됨
}
```

**동작:**
1. 임시 비밀번호를 새 비밀번호로 변경
2. 교인의 QR 코드 생성
3. `is_first` 플래그를 false로 변경

### 5. 일반 비밀번호 변경 (첫 로그인 아닌 경우)
일반적인 비밀번호 변경은 별도 엔드포인트를 사용합니다.

**Endpoint:** `POST /api/v1/auth/change-password`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request:**
```json
{
    "current_password": "MyCurrentPassword123!",
    "new_password": "MyNewPassword456!"
}
```

**Response:**
```json
{
    "msg": "Password updated successfully"
}
```

## 에러 처리

### 첫 로그인 설정 중복 시도
```json
{
    "detail": "First-time setup already completed"
}
```

### 잘못된 현재 비밀번호
```json
{
    "detail": "Incorrect password"
}
```

### 계정이 이미 존재하는 경우
```json
{
    "detail": "Member already has an account with email: hong@example.com"
}
```

## 앱 구현 가이드

### Flutter 예시 코드

```dart
// 로그인 후 첫 로그인 체크
Future<void> checkFirstTimeLogin() async {
  final response = await api.get('/auth/check-first-time');
  
  if (response['is_first'] == true) {
    // 첫 로그인 화면으로 이동
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => FirstTimeSetupScreen()),
    );
  } else {
    // 메인 화면으로 이동
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => MainScreen()),
    );
  }
}

// 첫 로그인 설정 완료
Future<void> completeFirstTimeSetup(String newPassword) async {
  try {
    final response = await api.post(
      '/auth/complete-first-time-setup',
      data: {'new_password': newPassword},
    );
    
    // 성공 시 메인 화면으로 이동
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => MainScreen()),
    );
  } catch (e) {
    // 에러 처리
    showErrorDialog(e.message);
  }
}
```

## 보안 고려사항

1. **임시 비밀번호 생성**
   - 최소 8자 이상
   - 대소문자, 숫자, 특수문자 포함
   - 무작위 생성

2. **비밀번호 전달**
   - SMS 또는 이메일로 안전하게 전달
   - 관리자 화면에서 한 번만 표시

3. **세션 관리**
   - 첫 로그인 완료 전까지는 제한된 기능만 접근 가능
   - 일정 시간 내에 첫 로그인 설정을 완료하지 않으면 세션 만료

4. **QR 코드 보안**
   - 교인별 고유 QR 코드 생성
   - QR 코드 재생성 기능 제공