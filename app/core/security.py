# from datetime import datetime, timedelta
# from typing import Optional

# from jose import jwt, JWTError
# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials

# from src.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, oauth2_scheme, pwd_context, http_bearer
# from src.crud.baseregister import UserRepository
# from src.core.database import async_session_factory
# from src.schemas.token import TokenData


# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     try:
#         return pwd_context.verify(plain_password, hashed_password)
#     except Exception:
#         return False


# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


# async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(http_bearer)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         token = credentials.credentials
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credentials_exception

#     async with async_session_factory() as session:
#         repo = UserRepository(session)
#         user = await repo.get_by_username(token_data.username)
#         if user is None:
#             raise credentials_exception
#         return user


#--------------------------------------------------------------------------

# src/core/security.py

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError

from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    pwd_context,
)
from app.core.database import get_chosen_db     # ← the key change!
from app.crud.baseregister import UserRepository
from app.schemas.token import TokenData

# src/core/security.py

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError

from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, pwd_context
from app.core.database import get_chosen_db
from app.crud.baseregister import UserRepository
from app.schemas.token import TokenData
from sqlalchemy.ext.asyncio import AsyncSession

# Password hashing context (you already have this)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ────────────────────────────────────────────────
# Updated dependency – now uses the same DB choice as the request
# ────────────────────────────────────────────────
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: AsyncSession = Depends(get_chosen_db)   # ← reuses the ?db=... from request
):
    """
    Get the currently authenticated user.
    
    - Uses the same database as the current request (?db=supabase or local)
    - Validates JWT and checks that the user exists in the chosen database
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        token_data = TokenData(username=username)

    except JWTError as e:
        raise credentials_exception from e

    # Use the same DB session as the endpoint that called us
    repo = UserRepository(db)
    user = await repo.get_by_username(token_data.username)

    if user is None:
        raise credentials_exception

    return user