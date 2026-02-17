from typing import Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.core.config import pwd_context
from app.models.register import User
from app.schemas.user_schema import UserCreate
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    User-specific repository – handles user creation with password hashing
    and uniqueness checks.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def create(self, user_data: UserCreate) -> User:
        # check existing by username or email
        stmt = select(User).where(
            or_(User.email == user_data.email, User.username == user_data.username)
        )
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with given email or username already exists",
            )

        # Hash password (bcrypt safe length = 72)
        password_hash = pwd_context.hash(user_data.password[:72])

        payload = user_data.model_dump()
        payload.pop("password", None)
        payload["password_hash"] = password_hash

        return await super().create(payload)

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username_and_password(
        self, username: str, password: str
    ) -> Optional[User]:
        user = await self.get_by_username(username)

        if user and pwd_context.verify(password, user.password_hash):
            return user

        return None
