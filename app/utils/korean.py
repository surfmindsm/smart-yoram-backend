"""Korean language utilities for initial consonant search."""

KOREAN_INITIAL_CONSONANTS = [
    'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 
    'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
]

def get_initial_consonant(char: str) -> str:
    """
    Extract initial consonant from Korean character.
    """
    if not char or not '가' <= char <= '힣':
        return char
    
    # Korean Unicode calculation
    code = ord(char) - ord('가')
    initial_index = code // (21 * 28)
    
    return KOREAN_INITIAL_CONSONANTS[initial_index]


def get_initial_consonants(text: str) -> str:
    """
    Extract initial consonants from Korean text.
    """
    result = []
    for char in text:
        if '가' <= char <= '힣':
            result.append(get_initial_consonant(char))
        else:
            result.append(char)
    
    return ''.join(result)


def match_initial_consonants(text: str, pattern: str) -> bool:
    """
    Check if text matches the initial consonant pattern.
    """
    text_initials = get_initial_consonants(text)
    
    # Check if pattern appears in the initial consonants
    pattern_index = 0
    for char in text_initials:
        if pattern_index < len(pattern) and char == pattern[pattern_index]:
            pattern_index += 1
            if pattern_index == len(pattern):
                return True
    
    return False


def is_korean_initial_consonant(char: str) -> bool:
    """
    Check if character is a Korean initial consonant.
    """
    return char in KOREAN_INITIAL_CONSONANTS


def is_korean_initial_search(query: str) -> bool:
    """
    Check if query contains only Korean initial consonants.
    """
    if not query:
        return False
    
    # Check if all characters are Korean initial consonants or spaces
    for char in query:
        if char != ' ' and not is_korean_initial_consonant(char):
            return False
    
    return True