from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class FamilyRelationshipBase(BaseModel):
    member_id: int
    related_member_id: int
    relationship_type: str  # 부모, 자녀, 배우자, 형제, 자매, 조부모, 손자녀


class FamilyRelationshipCreate(FamilyRelationshipBase):
    pass


class FamilyRelationshipUpdate(BaseModel):
    relationship_type: Optional[str] = None


class FamilyRelationshipInDBBase(FamilyRelationshipBase):
    id: int
    church_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class FamilyRelationship(FamilyRelationshipInDBBase):
    pass


class FamilyRelationshipInDB(FamilyRelationshipInDBBase):
    pass


class FamilyTreeMember(BaseModel):
    id: int
    name: str
    profile_photo_url: Optional[str] = None
    relationship_type: Optional[str] = None
    date_of_birth: Optional[str] = None
    phone_number: Optional[str] = None

    class Config:
        from_attributes = True


class FamilyTree(BaseModel):
    root_member: FamilyTreeMember
    family_members: list[FamilyTreeMember]
