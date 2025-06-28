from fastapi import APIRouter, Depends
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select, desc

from db.operations import get_db
from models.data import EnvironmentData
from models.users import User
from schemas.data_schema import DataList
from schemas.pagination_schema import PaginatedResponse, PaginatedRequest
from schemas.responses_schema import Responses
from utils.security import get_current_user

router = APIRouter(
    prefix="/data",
    tags=["Data"]
)


@router.get("/new", response_model=Responses[DataList])
async def get_new_data(
        device_id: int | None = None,
        db: AsyncSession = Depends(get_db)
):
    # 动态构建过滤条件列表
    filters = []
    if device_id is not None:
        filters.append(EnvironmentData.device_id == device_id)
        # 获取当前页数据
        query_data = (select(EnvironmentData)
                      .options(selectinload(EnvironmentData.device_name_fk),
                               selectinload(EnvironmentData.location_name_fk))
                      .where(and_(*filters))
                      .order_by(desc(EnvironmentData.timestamp), desc(EnvironmentData.id)))
        result = await db.execute(query_data)
        data = result.scalars().first()
        item = DataList(
            id=data.id,
            device_name=data.device_name_fk.name,
            timestamp=data.timestamp,
            temperature=data.temperature,
            humidity=data.humidity,
            illuminance=data.illuminance,
            location_name=data.location_name_fk.name,
        )
        return Responses(data=item)


@router.delete("/delete", response_model=Responses)
async def delete(
        data_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        return Responses(status_code=1, message="Not authorized to delete data.")
    query_data = select(EnvironmentData).where(EnvironmentData.id == data_id)
    data = (await db.scalars(query_data)).first()
    if not data:
        return Responses(status_code=1, message="Data not found.")
    await db.delete(data)
    await db.commit()
    return Responses(message="Data deleted.")


@router.get("/list", response_model=Responses[PaginatedResponse[DataList]])
async def data_list(
        device_id: int | None = None,
        location_id: int | None = None,
        pagination: PaginatedRequest = Depends(PaginatedRequest),
        db: AsyncSession = Depends(get_db)
):
    # 分页数据
    page = pagination.page
    size = pagination.size
    offset = (page - 1) * size
    # 动态构建过滤条件列表
    filters = []
    if location_id is not None:
        filters.append(EnvironmentData.location_id == location_id)
    if device_id is not None:
        filters.append(EnvironmentData.device_id == device_id)
    # 获取当前页数据
    query_data = (select(EnvironmentData)
                  .options(selectinload(EnvironmentData.device_name_fk), selectinload(EnvironmentData.location_name_fk))
                  .where(and_(*filters))
                  .order_by(desc(EnvironmentData.timestamp),desc(EnvironmentData.id))
                  .offset(offset).limit(size))
    result = await db.execute(query_data)
    datas = result.scalars().all()
    items: list[DataList] = []
    for data in datas:
        item = DataList(
            id=data.id,
            device_name=data.device_name_fk.name,
            timestamp=data.timestamp,
            temperature=data.temperature,
            humidity=data.humidity,
            illuminance=data.illuminance,
            location_name=data.location_name_fk.name,
        )
        items.append(item)
    # 获取总记录数
    query_total = (select(func.count())
               .select_from(EnvironmentData)
               .where(and_(*filters)))
    count = await db.execute(query_total)
    total = count.scalar_one()
    # 计算总页数
    total_pages = (total + size - 1) // size
    paginated_response = PaginatedResponse[DataList](
        items=items,
        page=page,
        size=size,
        total=total,
        total_pages=total_pages
    )
    return Responses(data=paginated_response)
