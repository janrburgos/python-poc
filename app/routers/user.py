from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.get("/", response_model=list[UserResponse])
def read_users(offset: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Retrieve a list of users with optional pagination.

        Args:
            offset (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 10.

        Returns:
            list[UserResponse]: A list of user records.
    """
    return db.query(User).offset(offset).limit(limit).all()


@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a user by their unique ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            UserResponse: The requested user record.

        Raises:
            HTTPException: If the user is not found (404).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/search", response_model=UserResponse)
def get_user_by_username_or_email(
    username: str = Query(None), email: str = Query(None), db: Session = Depends(get_db)
):
    """
    Search for a user by username or email.

        Args:
            username (str, optional): The username of the user.
            email (str, optional): The email of the user.

        Returns:
            UserResponse: The user matching the given username or email.

        Raises:
            HTTPException: If neither `username` nor `email` is provided (400).
            HTTPException: If no matching user is found (404).
    """
    if not username and not email:
        raise HTTPException(
            status_code=400,
            detail="Provide either 'username' or 'email' as a query parameter",
        )

    user = (
        db.query(User)
        .filter(or_(User.username == username, User.email == email))
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user with a unique username and email.

        Args:
            user (UserCreate): User data containing username and email.

        Returns:
            UserResponse: The created user record.

        Raises:
            HTTPException: If a user with the same username or email already exists (400).
    """
    existing_user = (
        db.query(User)
        .filter(or_(User.username == user.username, User.email == user.email))
        .first()
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Username/Email already exists")

    new_user = User(username=user.username, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.patch("/{user_id}", response_model=UserResponse)
def partial_update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """
    Partially update a user's attributes (username and/or email).

        Args:
            user_id (int): The ID of the user to update.
            user (UserUpdate): The fields to update.

        Returns:
            UserResponse: The updated user record.

        Raises:
            HTTPException: If the user is not found (404).
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.username is not None:
        db_user.username = user.username
    if user.email is not None:
        db_user.email = user.email

    db.commit()
    db.refresh(db_user)
    return db_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    """
    Fully update a user's details.

    Args:
        user_id (int): The ID of the user to update.
        user (UserCreate): The new user data.

    Returns:
        UserResponse: The updated user record.

    Raises:
        HTTPException: If the user is not found (404).
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.username = user.username
    db_user.email = user.email
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user by their ID.

    Args:
        user_id (int): The ID of the user to delete.

    Returns:
        dict: A message confirming successful deletion.

    Raises:
        HTTPException: If the user is not found (404).
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}
