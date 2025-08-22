from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
import asyncio

from app import models, schemas
from app.api import deps
from app.utils.korean import is_korean_initial_search, match_initial_consonants
from app.utils.password import generate_temporary_password
from app.utils.encryption import encrypt_password, decrypt_password
from app.utils.email import send_temporary_password_email
from app.utils.sms import send_temporary_password_sms
from app.core.security import get_password_hash
from app.services.geocoding import geocoding_service

router = APIRouter()


@router.get("/", response_model=List[schemas.Member])
def read_members(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search by name or phone"),
    member_status: Optional[str] = Query(None, description="Filter by member status"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    if current_user.church_id:
        query = db.query(models.Member).filter(
            models.Member.church_id == current_user.church_id
        )
    elif current_user.is_superuser:
        query = db.query(models.Member)
    else:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Apply search filter
    if search:
        if is_korean_initial_search(search):
            # Korean initial consonant search
            all_members = query.all()
            filtered_members = [
                member
                for member in all_members
                if match_initial_consonants(member.name, search.replace(" ", ""))
            ]
            return filtered_members[skip : skip + limit]
        else:
            # Regular search
            query = query.filter(
                or_(
                    models.Member.name.contains(search),
                    models.Member.phone.contains(search),
                )
            )

    # Apply status filter
    if member_status:
        query = query.filter(models.Member.member_status == member_status)

    members = query.offset(skip).limit(limit).all()
    return members


@router.post("/", response_model=schemas.Member)
def create_member(
    *,
    db: Session = Depends(deps.get_db),
    member_in: schemas.MemberCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    # Use the current user's church_id
    church_id = current_user.church_id
    print(f"Current user: {current_user.username}, Church ID: {church_id}")

    if not church_id:
        raise HTTPException(status_code=400, detail="User has no church assigned")

    # Override church_id with current user's church_id
    member_dict = member_in.dict()
    print(f"Original member data: {member_dict}")
    member_dict["church_id"] = church_id
    print(f"Updated church_id to: {church_id}")

    # Check if email is provided
    if not member_in.email:
        print(f"Error: Email not provided for member {member_in.name}")
        raise HTTPException(
            status_code=400, detail="Email is required for member registration"
        )

    # Check if user with this email already exists
    existing_user = (
        db.query(models.User).filter(models.User.email == member_in.email).first()
    )
    if existing_user:
        print(
            f"User with email {member_in.email} already exists (User ID: {existing_user.id})"
        )
        # Check if this user is already linked to another member
        existing_member = (
            db.query(models.Member)
            .filter(
                models.Member.user_id == existing_user.id,
                models.Member.id != member_in.id if hasattr(member_in, "id") else True,
            )
            .first()
        )
        if existing_member:
            raise HTTPException(
                status_code=400,
                detail=f"이 이메일은 이미 다른 교인({existing_member.name})이 사용 중입니다.",
            )
        # If not linked to any member, we can use this user
        print(f"Linking existing user {existing_user.id} to new member")

    # Create member with overridden church_id
    member = models.Member(**member_dict)
    
    # Geocode address if provided
    if member.address:
        try:
            coords = asyncio.run(geocoding_service.get_coordinates(member.address))
            if coords:
                member.latitude, member.longitude = coords
                print(f"Geocoded address '{member.address}' to ({member.latitude}, {member.longitude})")
        except Exception as e:
            print(f"Geocoding failed for address '{member.address}': {e}")
    
    db.add(member)
    db.flush()  # Flush to get member.id without committing

    # Handle user account
    if existing_user:
        # Use existing user
        member.user_id = existing_user.id
        user = existing_user
        # Get the password if it exists
        if existing_user.encrypted_password:
            from app.utils.encryption import decrypt_password

            temp_password = decrypt_password(existing_user.encrypted_password)
        else:
            temp_password = None
    else:
        # Generate temporary password
        temp_password = generate_temporary_password()

        # Create user account for member
        user = models.User(
            email=member_in.email,
            username=member_in.email,  # Use email as username
            hashed_password=get_password_hash(temp_password),
            encrypted_password=encrypt_password(temp_password),
            full_name=member_in.name,
            phone=member_in.phone,
            church_id=church_id,
            role="member",
            is_active=True,
        )
        db.add(user)
        db.flush()

        # Link member to user
        member.user_id = user.id

    # Try to send temporary password via email and SMS
    church = (
        db.query(models.Church).filter(models.Church.id == member.church_id).first()
    )
    church_name = church.name if church else "교회"

    # Try email first
    email_sent = False
    try:
        email_sent = send_temporary_password_email(
            to_email=member.email,
            member_name=member.name,
            church_name=church_name,
            temp_password=temp_password,
        )

        if email_sent:
            print(f"Temporary password sent to {member.email}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

    # Try SMS if phone number is available
    sms_sent = False
    if member.phone:
        try:
            sms_sent = send_temporary_password_sms(
                phone_number=member.phone,
                member_name=member.name,
                church_name=church_name,
                temp_password=temp_password,
            )

            if sms_sent:
                print(f"Temporary password sent to {member.phone}")
        except Exception as e:
            print(f"Failed to send SMS: {str(e)}")

    # Log the result
    print(f"Created user for member {member.name} (email: {member.email})")
    if not email_sent and not sms_sent:
        print(f"Warning: Could not send temporary password via email or SMS")
        print(f"Temporary password: {temp_password}")  # Log for manual delivery

    db.commit()
    db.refresh(member)

    return member


@router.get("/{member_id}", response_model=schemas.Member)
def read_member(
    *,
    db: Session = Depends(deps.get_db),
    member_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if not current_user.is_superuser and member.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return member


@router.put("/{member_id}", response_model=schemas.Member)
def update_member(
    *,
    db: Session = Depends(deps.get_db),
    member_id: int,
    member_in: schemas.MemberUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if not current_user.is_superuser and member.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_data = member_in.dict(exclude_unset=True)
    
    # Check if address is being updated
    address_changed = 'address' in update_data and update_data['address'] != member.address
    
    for field, value in update_data.items():
        setattr(member, field, value)
    
    # Geocode new address if changed
    if address_changed and member.address:
        try:
            coords = asyncio.run(geocoding_service.get_coordinates(member.address))
            if coords:
                member.latitude, member.longitude = coords
                print(f"Geocoded updated address '{member.address}' to ({member.latitude}, {member.longitude})")
        except Exception as e:
            print(f"Geocoding failed for address '{member.address}': {e}")

    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.delete("/{member_id}")
def delete_member(
    *,
    db: Session = Depends(deps.get_db),
    member_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if not current_user.is_superuser and member.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db.delete(member)
    db.commit()
    return {"message": "Member deleted successfully"}


@router.get("/{member_id}/password", response_model=dict)
def get_member_password(
    *,
    db: Session = Depends(deps.get_db),
    member_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get decrypted password for a member (admin only).
    """
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if not member.user_id:
        raise HTTPException(status_code=404, detail="Member has no user account")

    user = db.query(models.User).filter(models.User.id == member.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User account not found")

    if not user.encrypted_password:
        raise HTTPException(status_code=404, detail="Password not available")

    decrypted_password = decrypt_password(user.encrypted_password)
    if not decrypted_password:
        raise HTTPException(status_code=500, detail="Failed to decrypt password")

    return {
        "member_id": member_id,
        "member_name": member.name,
        "email": user.email,
        "password": decrypted_password,
    }


@router.post("/{member_id}/create-account")
def create_member_account(
    *,
    db: Session = Depends(deps.get_db),
    member_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create user account for a member with temporary password.
    Returns the temporary password and account details.
    Only church admins or ministers can create accounts.
    """
    # Check permissions
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(
            status_code=403,
            detail="Only church admins and ministers can create member accounts",
        )

    # Get member
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    # Check church permission
    if not current_user.is_superuser and member.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Check if already has account
    if member.user_id:
        user = db.query(models.User).filter(models.User.id == member.user_id).first()
        if user:
            raise HTTPException(
                status_code=400,
                detail=f"Member already has an account with email: {user.email}",
            )

    # Check if email is required
    if not member.email:
        raise HTTPException(
            status_code=400,
            detail="Member must have an email address to create an account",
        )

    # Check if user with this email already exists
    existing_user = (
        db.query(models.User).filter(models.User.email == member.email).first()
    )
    if existing_user:
        raise HTTPException(
            status_code=400, detail=f"User with email {member.email} already exists"
        )

    # Generate temporary password
    temp_password = generate_temporary_password()

    # Create user account
    user = models.User(
        email=member.email,
        username=member.email,  # Use email as username
        hashed_password=get_password_hash(temp_password),
        encrypted_password=encrypt_password(temp_password),
        full_name=member.name,
        phone=member.phone,
        church_id=member.church_id,
        role="member",
        is_active=True,
        is_first=True,  # Mark as first-time user
    )

    db.add(user)
    db.flush()  # Get user ID

    # Link member to user
    member.user_id = user.id
    member.invitation_sent = True
    member.invitation_sent_at = datetime.utcnow()

    db.commit()
    db.refresh(user)
    db.refresh(member)

    # TODO: Send email/SMS with temporary password
    # For now, just return the details

    return {
        "member_id": member.id,
        "member_name": member.name,
        "user_id": user.id,
        "email": user.email,
        "username": user.username,
        "temporary_password": temp_password,
        "is_first": user.is_first,
        "message": "Account created successfully. Please share the temporary password with the member.",
    }
