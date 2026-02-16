# from datetime import timedelta

# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm

# from src.core.database import async_session_factory
# from src.crud.baseregister import UserRepository
# from src.core.security import verify_password, create_access_token
# from src.schemas.token import Token
# from src.core.config import ACCESS_TOKEN_EXPIRE_MINUTES


# router = APIRouter(prefix="/login", tags=["login"])

# async def authenticate_user(repo: UserRepository, username: str, password: str):
#     user = await repo.get_by_username_and_password(username, password)
#     return user

# @router.post("/", response_model=Token)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
#     """
#     User login to obtain JWT token
#     """
#     async with async_session_factory() as session:
#         repo = UserRepository(session)
#         user = await authenticate_user(repo, form_data.username, form_data.password)
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Incorrect username or password",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#         access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#         access_token = create_access_token(
#             data={"sub": user.username}, expires_delta=access_token_expires
#         )
#         return {"access_token": access_token, "token_type": "bearer"}

# ------------------------------------------------------------------
# src/api/login.py   (or src/routers/login.py)
# src/api/auth.py    (or src/routers/login.py – adjust filename as needed)

from datetime import timedelta
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import db_factory
from app.crud.baseregister import UserRepository
from app.core.security import verify_password, create_access_token
from app.schemas.token import Token
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/login", tags=["login"])


# =============================================================================
# Dependency – choose database via query parameter ?db=
# =============================================================================
async def get_chosen_db(
    db: str = Query(
        default="local",
        description="Database to authenticate against: 'local' (PostgreSQL) or 'supabase'"
    )
) -> AsyncSession:
    """
    Returns AsyncSession connected to the chosen database.
    """
    choice = db.lower().strip()
    if choice not in ("local", "supabase"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid database choice. Allowed values: 'local' or 'supabase'"
        )

    async for session in db_factory.get_session(choice):
        yield session


# =============================================================================
# Helper function – verify credentials
# =============================================================================
async def authenticate_user(
    repo: UserRepository,
    username: str,
    password: str
):
    """
    Check if user exists and password matches.
    Returns user object if successful, None otherwise.
    """
    # Assuming your repository has a method that finds user by username
    user = await repo.get_by_username(username)
    if not user:
        return None

    # Verify plain password against stored hash
    if not verify_password(password, user.password_hash):
        return None

    return user


# =============================================================================
# Main login endpoint
# =============================================================================
@router.post(
    "/",
    response_model=Token,
    summary="Login and get JWT access token",
    description=(
        "Authenticate user and return JWT bearer token.\n"
        "Use query parameter ?db=supabase to login against Supabase database."
    )
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_chosen_db)
):
    """
    User login endpoint – obtain access token

    Form fields:
    - username (can be email or username)
    - password

    Query parameters:
    - db: "local" (default) or "supabase"
    """
    repo = UserRepository(db)

    user = await authenticate_user(
        repo=repo,
        username=form_data.username,
        password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer"
    )