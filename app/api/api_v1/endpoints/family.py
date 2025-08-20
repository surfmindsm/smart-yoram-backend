from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app import models, schemas
from app.api import deps

router = APIRouter()


@router.post("/relationships", response_model=schemas.FamilyRelationship)
def create_family_relationship(
    *,
    db: Session = Depends(deps.get_db),
    relationship_in: schemas.FamilyRelationshipCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new family relationship.
    """
    # Verify both members exist and belong to the same church
    member = (
        db.query(models.Member)
        .filter(
            models.Member.id == relationship_in.member_id,
            models.Member.church_id == current_user.church_id,
        )
        .first()
    )

    related_member = (
        db.query(models.Member)
        .filter(
            models.Member.id == relationship_in.related_member_id,
            models.Member.church_id == current_user.church_id,
        )
        .first()
    )

    if not member or not related_member:
        raise HTTPException(status_code=404, detail="One or both members not found")

    if member.id == related_member.id:
        raise HTTPException(
            status_code=400, detail="Cannot create relationship with self"
        )

    # Check if relationship already exists
    existing = (
        db.query(models.FamilyRelationship)
        .filter(
            models.FamilyRelationship.member_id == relationship_in.member_id,
            models.FamilyRelationship.related_member_id
            == relationship_in.related_member_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Relationship already exists")

    # Create the relationship
    relationship = models.FamilyRelationship(
        church_id=current_user.church_id, **relationship_in.dict()
    )
    db.add(relationship)

    # Create reverse relationship based on type
    reverse_type = get_reverse_relationship_type(relationship_in.relationship_type)
    if reverse_type:
        reverse_relationship = models.FamilyRelationship(
            church_id=current_user.church_id,
            member_id=relationship_in.related_member_id,
            related_member_id=relationship_in.member_id,
            relationship_type=reverse_type,
        )
        db.add(reverse_relationship)

    db.commit()
    db.refresh(relationship)

    return relationship


@router.get(
    "/relationships/{member_id}", response_model=List[schemas.FamilyRelationship]
)
def get_member_relationships(
    *,
    db: Session = Depends(deps.get_db),
    member_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all family relationships for a member.
    """
    member = (
        db.query(models.Member)
        .filter(
            models.Member.id == member_id,
            models.Member.church_id == current_user.church_id,
        )
        .first()
    )

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    relationships = (
        db.query(models.FamilyRelationship)
        .filter(models.FamilyRelationship.member_id == member_id)
        .all()
    )

    return relationships


@router.get("/tree/{member_id}", response_model=schemas.FamilyTree)
def get_family_tree(
    *,
    db: Session = Depends(deps.get_db),
    member_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get complete family tree for a member.
    """
    root_member = (
        db.query(models.Member)
        .filter(
            models.Member.id == member_id,
            models.Member.church_id == current_user.church_id,
        )
        .first()
    )

    if not root_member:
        raise HTTPException(status_code=404, detail="Member not found")

    # Get all family members (both directions)
    family_relationships = (
        db.query(models.FamilyRelationship)
        .filter(
            or_(
                models.FamilyRelationship.member_id == member_id,
                models.FamilyRelationship.related_member_id == member_id,
            )
        )
        .all()
    )

    # Collect all related member IDs
    related_member_ids = set()
    relationship_map = {}

    for rel in family_relationships:
        if rel.member_id == member_id:
            related_member_ids.add(rel.related_member_id)
            relationship_map[rel.related_member_id] = rel.relationship_type
        else:
            related_member_ids.add(rel.member_id)
            # Get reverse relationship type
            reverse_rel = (
                db.query(models.FamilyRelationship)
                .filter(
                    models.FamilyRelationship.member_id == rel.related_member_id,
                    models.FamilyRelationship.related_member_id == member_id,
                )
                .first()
            )
            if reverse_rel:
                relationship_map[rel.member_id] = reverse_rel.relationship_type

    # Get all related members
    family_members_data = []
    if related_member_ids:
        family_members = (
            db.query(models.Member)
            .filter(models.Member.id.in_(related_member_ids))
            .all()
        )

        for member in family_members:
            family_members_data.append(
                schemas.FamilyTreeMember(
                    id=member.id,
                    name=member.name,
                    profile_photo_url=member.profile_photo_url,
                    relationship_type=relationship_map.get(member.id),
                    date_of_birth=(
                        member.birthdate.isoformat() if member.birthdate else None
                    ),
                    phone_number=member.phone,
                )
            )

    # Create root member
    root_member_data = schemas.FamilyTreeMember(
        id=root_member.id,
        name=root_member.name,
        profile_photo_url=root_member.profile_photo_url,
        relationship_type="본인",
        date_of_birth=(
            root_member.birthdate.isoformat() if root_member.birthdate else None
        ),
        phone_number=root_member.phone,
    )

    return schemas.FamilyTree(
        root_member=root_member_data, family_members=family_members_data
    )


@router.delete("/relationships/{relationship_id}")
def delete_family_relationship(
    *,
    db: Session = Depends(deps.get_db),
    relationship_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a family relationship.
    """
    relationship = (
        db.query(models.FamilyRelationship)
        .filter(
            models.FamilyRelationship.id == relationship_id,
            models.FamilyRelationship.church_id == current_user.church_id,
        )
        .first()
    )

    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")

    # Find and delete reverse relationship
    reverse_relationship = (
        db.query(models.FamilyRelationship)
        .filter(
            models.FamilyRelationship.member_id == relationship.related_member_id,
            models.FamilyRelationship.related_member_id == relationship.member_id,
        )
        .first()
    )

    if reverse_relationship:
        db.delete(reverse_relationship)

    db.delete(relationship)
    db.commit()

    return {"message": "Family relationship deleted successfully"}


def get_reverse_relationship_type(relationship_type: str) -> str:
    """
    Get the reverse relationship type.
    """
    reverse_map = {
        "부모": "자녀",
        "자녀": "부모",
        "배우자": "배우자",
        "형제": "형제",
        "자매": "자매",
        "조부모": "손자녀",
        "손자녀": "조부모",
        "삼촌": "조카",
        "조카": "삼촌",
        "이모": "조카",
        "고모": "조카",
    }

    return reverse_map.get(relationship_type, "가족")
