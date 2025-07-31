# Gender Validation Implementation

## Overview
Gender values are now validated to ensure only 'M' (Male) and 'F' (Female) are stored in the database.

## Changes Made

### 1. Created Gender Enum (`app/schemas/enums.py`)
- Defines valid gender values: M and F
- Provides Korean to English conversion methods
- Supports multiple Korean variants: 남, 남자, 남성, 여, 여자, 여성

### 2. Updated Member Schema (`app/schemas/member.py`)
- Added field validator for gender field
- Automatically converts Korean labels to M/F
- Validates and normalizes gender input
- Raises ValueError for invalid inputs

### 3. Updated Excel Import/Export (`app/api/api_v1/endpoints/excel.py`)
- Import: Accepts Korean gender labels and converts to M/F
- Export: Converts M/F back to Korean labels (남/여)

## Usage Examples

### Valid Gender Values
- English: 'M', 'F', 'm', 'f' (case-insensitive)
- Korean: '남', '여', '남자', '여자', '남성', '여성'

### API Examples

```python
# Creating a member with English gender
{
    "name": "홍길동",
    "phone": "010-1234-5678",
    "gender": "M"
}

# Creating a member with Korean gender
{
    "name": "김영희",
    "phone": "010-2345-6789", 
    "gender": "여"
}
```

### Excel Import
The Excel file should use Korean labels:
- 성별 column: 남, 여

### Database Storage
All gender values are stored as:
- 'M' for male
- 'F' for female

## Testing
Run the test script to verify gender validation:
```bash
python test_gender_validation.py
```

## Error Handling
Invalid gender values will result in:
```
ValueError: Gender must be M or F (or 남/여 in Korean)
```