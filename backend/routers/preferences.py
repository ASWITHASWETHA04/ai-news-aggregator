"""
Preferences router: /preferences
Allows authenticated users to get/update their news category preferences.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from models import PreferencesUpdate, PreferencesResponse, VALID_CATEGORIES
from auth_utils import get_current_user
from database import get_db

router = APIRouter()


@router.get("/", response_model=PreferencesResponse)
async def get_preferences(current_user: dict = Depends(get_current_user)):
    """Return the current user's preferences."""
    return PreferencesResponse(categories=current_user.get("preferences", []))


@router.put("/", response_model=PreferencesResponse)
async def update_preferences(
    payload: PreferencesUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update the current user's category preferences."""
    db = get_db()

    # Validate categories
    invalid = [c for c in payload.categories if c not in VALID_CATEGORIES]
    if invalid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid categories: {invalid}. Valid: {VALID_CATEGORIES}",
        )

    await db.users.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$set": {"preferences": payload.categories}},
    )

    return PreferencesResponse(categories=payload.categories)
