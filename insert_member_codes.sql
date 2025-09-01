-- codes 테이블에 교인 관리용 기초 드롭다운 데이터 생성
-- church_id = 0 (시스템 기본값)

-- 교인구분 코드
INSERT INTO codes (church_id, type, code, label) VALUES 
(0, 'member_type', 'FULL_MEMBER', '정교인'),
(0, 'member_type', 'CONFIRMED_MEMBER', '입교인'),
(0, 'member_type', 'BAPTIZED_MEMBER', '세례교인'),
(0, 'member_type', 'ASSOCIATE_MEMBER', '준회원'),
(0, 'member_type', 'VISITING_MEMBER', '심방교인');

-- 구역 코드
INSERT INTO codes (church_id, type, code, label) VALUES 
(0, 'district', 'DISTRICT_1', '1구역'),
(0, 'district', 'DISTRICT_2', '2구역'),
(0, 'district', 'DISTRICT_3', '3구역'),
(0, 'district', 'DISTRICT_4', '4구역'),
(0, 'district', 'DISTRICT_5', '5구역'),
(0, 'district', 'DISTRICT_6', '6구역'),
(0, 'district', 'DISTRICT_7', '7구역'),
(0, 'district', 'DISTRICT_8', '8구역');

-- 부구역 코드
INSERT INTO codes (church_id, type, code, label) VALUES 
(0, 'sub_district', 'SUB_1_1', '1-1구역'),
(0, 'sub_district', 'SUB_1_2', '1-2구역'),
(0, 'sub_district', 'SUB_2_1', '2-1구역'),
(0, 'sub_district', 'SUB_2_2', '2-2구역'),
(0, 'sub_district', 'SUB_3_1', '3-1구역'),
(0, 'sub_district', 'SUB_3_2', '3-2구역'),
(0, 'sub_district', 'SUB_4_1', '4-1구역'),
(0, 'sub_district', 'SUB_4_2', '4-2구역');

-- 교회학교/부서 코드
INSERT INTO codes (church_id, type, code, label) VALUES 
(0, 'church_school', 'ADULT_SCHOOL', '장년부'),
(0, 'church_school', 'YOUTH_SCHOOL', '청년부'),
(0, 'church_school', 'STUDENT_SCHOOL', '학생부'),
(0, 'church_school', 'CHILDREN_SCHOOL', '아동부'),
(0, 'church_school', 'KINDERGARTEN', '유치부'),
(0, 'church_school', 'SENIOR_SCHOOL', '경로부'),
(0, 'church_school', 'WOMEN_SCHOOL', '여전도회'),
(0, 'church_school', 'MEN_SCHOOL', '남전도회');

-- 직업 분류 코드
INSERT INTO codes (church_id, type, code, label) VALUES 
(0, 'job_category', 'OFFICE_WORKER', '사무직'),
(0, 'job_category', 'TEACHER', '교사'),
(0, 'job_category', 'MEDICAL', '의료진'),
(0, 'job_category', 'BUSINESS_OWNER', '사업가'),
(0, 'job_category', 'STUDENT', '학생'),
(0, 'job_category', 'HOUSEWIFE', '주부'),
(0, 'job_category', 'RETIRED', '은퇴'),
(0, 'job_category', 'ENGINEER', '엔지니어'),
(0, 'job_category', 'CIVIL_SERVANT', '공무원'),
(0, 'job_category', 'FREELANCER', '프리랜서'),
(0, 'job_category', 'FARMER', '농업'),
(0, 'job_category', 'OTHER', '기타');

-- 신급 코드
INSERT INTO codes (church_id, type, code, label) VALUES 
(0, 'spiritual_grade', 'GRADE_A', '갑급'),
(0, 'spiritual_grade', 'GRADE_B', '을급'),
(0, 'spiritual_grade', 'GRADE_C', '병급'),
(0, 'spiritual_grade', 'GRADE_D', '정급');

-- 나이그룹 코드
INSERT INTO codes (church_id, type, code, label) VALUES 
(0, 'age_group', 'ADULT', '성인'),
(0, 'age_group', 'YOUTH', '청소년'),
(0, 'age_group', 'CHILD', '아동'),
(0, 'age_group', 'SENIOR', '경로');

-- 직분 코드
INSERT INTO codes (church_id, type, code, label) VALUES 
(0, 'position', 'PASTOR', '목사'),
(0, 'position', 'ELDER', '장로'),
(0, 'position', 'DEACON', '안수집사'),
(0, 'position', 'KWONSA', '권사'),
(0, 'position', 'JIPSA', '집사'),
(0, 'position', 'MEMBER', '교인'),
(0, 'position', 'YOUTH_JIPSA', '청년집사'),
(0, 'position', 'STUDENT_JIPSA', '학생집사');

-- 연락처 타입 코드
INSERT INTO codes (church_id, type, code, label) VALUES 
(0, 'contact_type', 'MOBILE', '핸드폰'),
(0, 'contact_type', 'HOME', '집전화'),
(0, 'contact_type', 'WORK', '직장전화'),
(0, 'contact_type', 'EVANGELISM', '전도폰'),
(0, 'contact_type', 'FELLOWSHIP', '친목폰'),
(0, 'contact_type', 'FAX', '팩스');

-- 차량 타입 코드
INSERT INTO codes (church_id, type, code, label) VALUES 
(0, 'vehicle_type', 'SEDAN', '승용차'),
(0, 'vehicle_type', 'SUV', 'SUV'),
(0, 'vehicle_type', 'VAN', '승합차'),
(0, 'vehicle_type', 'TRUCK', '트럭'),
(0, 'vehicle_type', 'MOTORCYCLE', '오토바이'),
(0, 'vehicle_type', 'OTHER', '기타');

-- 등록배경 코드
INSERT INTO codes (church_id, type, code, label) VALUES 
(0, 'registration_background', 'INVITATION', '초청'),
(0, 'registration_background', 'EVANGELISM', '전도'),
(0, 'registration_background', 'FAMILY', '가족소개'),
(0, 'registration_background', 'FRIEND', '지인소개'),
(0, 'registration_background', 'TRANSFER', '이사'),
(0, 'registration_background', 'WEDDING', '결혼'),
(0, 'registration_background', 'FUNERAL', '장례'),
(0, 'registration_background', 'SELF_VISIT', '자발적방문'),
(0, 'registration_background', 'OTHER', '기타');

-- 교회학교 연도 (예시)
INSERT INTO codes (church_id, type, code, label) VALUES 
(0, 'school_year', '2020', '2020년'),
(0, 'school_year', '2021', '2021년'),
(0, 'school_year', '2022', '2022년'),
(0, 'school_year', '2023', '2023년'),
(0, 'school_year', '2024', '2024년'),
(0, 'school_year', '2025', '2025년');