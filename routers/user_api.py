from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from fastapi.params import Query
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from config import settings
from db.operations import get_db
from models.users import User
from schemas.pagination_schema import PaginatedResponse, PaginatedRequest
from schemas.responses_schema import Responses, Token
from schemas.user_schema import UserRegister, UserLogin, UserAdd, UserInfo, UserPasswordUpdate, UserUpdate, UserSearch, \
    UserList
from utils.security import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(
    prefix="/user",
    tags=["User"]
)


@router.post("/register", response_model=Responses)
async def register(user_create: UserRegister, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.username == user_create.username)
    existing_user = (await db.scalars(query)).first()
    if existing_user:
        return Responses(status_code=1, message="Username already registered.")
    hashed_password = get_password_hash(user_create.password)
    db_user = User(
        username=user_create.username,
        password_hash=hashed_password,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return Responses(message="User registered.")


@router.post("/login", response_model=Responses[Token])
async def login(user_login: UserLogin, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.username == user_login.username)
    user = (await db.scalars(query)).first()
    if not user or not verify_password(user_login.password, user.password_hash):
        return Responses(status_code=1, message="Incorrect username or password.")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    token = {
        "access_token": access_token,
        "token_type": "bearer"
    }
    user.last_login = datetime.now()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return Responses(message="Login successful.", data=token)


@router.get("/info", response_model=Responses[UserInfo])
async def get_info(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    query = select(User).where(User.username == current_user.username)
    user = (await db.scalars(query)).first()
    if not user:
        return Responses(status_code=1, message="User not found.")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return Responses(data=user)


@router.patch("/update_info", response_model=Responses)
async def update_info(
        user_update: UserInfo,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    query = select(User).where(User.id == current_user.id)
    user = (await db.scalars(query)).first()
    if not user:
        return Responses(status_code=1, message="User not found.")
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == 'role':
            pass
        else:
            setattr(user, key, value)
    user.updated_at = datetime.now()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return Responses(message="User updated.")


@router.patch("/password", response_model=Responses)
async def update_password(
        passwd_update: UserPasswordUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if not verify_password(passwd_update.password, current_user.password_hash):
        return Responses(status_code=1, message="Password error.")
    if passwd_update.new_password != passwd_update.re_password:
        return Responses(status_code=1, message="RePassword error.")
    query = select(User).where(User.id == current_user.id)
    user = (await db.scalars(query)).first()
    user.password_hash = get_password_hash(passwd_update.new_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return Responses(message="Password updated.")


@router.post("/add", response_model=Responses)
async def add(
        user_add: UserAdd,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        return Responses(status_code=1, message="Not authorized to add user.")
    query = select(User).where(User.username == user_add.username)
    user = (await db.scalars(query)).first()
    if user:
        return Responses(status_code=1, message="User name had existed.")
    user = User()
    for key, value in user_add.model_dump(exclude_unset=True).items():
        if key != 'password':
            setattr(user, key, value)
        elif key == 'password':
            setattr(user, 'password_hash', get_password_hash(value))
    user.created_at = datetime.now()
    user.updated_at = datetime.now()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return Responses(message="User updated.")


@router.delete("/delete", response_model=Responses)
async def delete(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        return Responses(status_code=1, message="Not authorized to delete user.")
    query = select(User).where(User.id == user_id)
    user = (await db.scalars(query)).first()
    if not user:
        return Responses(status_code=1, message="User not found.")
    await db.delete(user)
    await db.commit()
    return Responses(message="User deleted.")


@router.get("/find", response_model=Responses[User])
async def find(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        return Responses(status_code=1, message="Not authorized to find user.")
    query = select(User).where(User.id == user_id)
    user = (await db.scalars(query)).first()
    if not user:
        return Responses(status_code=1, message="User not found.")
    return Responses(data=user)


@router.patch("/update", response_model=Responses)
async def update(
        user_update: UserUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        return Responses(status_code=1, message="Not authorized to update user.")
    query = select(User).where(User.id == user_update.id)
    user = (await db.scalars(query)).first()
    if not user:
        return Responses(status_code=1, message="User not found.")
    user.username = user_update.username
    user.email = user_update.email
    user.phone = user_update.phone
    user.role = user_update.role
    user.updated_at = datetime.now()
    db.add(user)
    await db.commit()
    return Responses(message="User updated.")


@router.get("/list", response_model=Responses[PaginatedResponse[UserList]])
async def users_list(
        user_search: UserSearch = Depends(UserSearch),
        pagination: PaginatedRequest = Depends(PaginatedRequest),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        return Responses(status_code=1, message="Permission denied.")
    # 分页数据
    page = pagination.page
    size = pagination.size
    offset = (page - 1) * size
    # 动态构建过滤条件列表
    filters = []
    if user_search.username is not None:
        filters.append(User.username == user_search.username)
    if user_search.role is not None:
        filters.append(User.role == user_search.role)
    # 获取当前页数据
    query_user = (select(User)
               .where(and_(*filters))
               .offset(offset).limit(size))
    result = await db.execute(query_user)
    users = result.scalars().all()
    items: list[UserList] = []
    for user in users:
        item = UserList(
            id=user.id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            role=user.role,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        items.append(item)
    # 获取总记录数
    query_total = (select(func.count())
               .select_from(User)
               .where(and_(*filters)))
    count = await db.execute(query_total)
    total = count.scalar_one()
    # 计算总页数
    total_pages = (total + size - 1) // size
    paginated_response = PaginatedResponse[UserList](
        items=items,
        page=page,
        size=size,
        total=total,
        total_pages=total_pages
    )
    return Responses(data=paginated_response)
