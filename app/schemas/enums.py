from enum import Enum


class Gender(str, Enum):
    MALE = "M"
    FEMALE = "F"
    
    @classmethod
    def from_korean(cls, value: str) -> "Gender":
        """Convert Korean gender label to enum value"""
        mapping = {
            "남": cls.MALE,
            "남자": cls.MALE,
            "남성": cls.MALE,
            "여": cls.FEMALE,
            "여자": cls.FEMALE,
            "여성": cls.FEMALE,
        }
        return mapping.get(value, None)
    
    def to_korean(self) -> str:
        """Convert enum value to Korean gender label"""
        mapping = {
            self.MALE: "남",
            self.FEMALE: "여",
        }
        return mapping.get(self.value, "")