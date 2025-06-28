from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from db.operations import get_db
from models.locations import Location
from schemas.pagination_schema import PaginatedRequest, PaginatedResponse
from schemas.responses_schema import Responses

router = APIRouter(
    prefix="/location",
    tags=["Location"]
)

@router.get("/list", response_model=Responses[PaginatedResponse[Location]])
async def locations_list(
    pagination: PaginatedRequest = Depends(PaginatedRequest),
    db: AsyncSession = Depends(get_db)
):
    # 分页数据
    page = pagination.page
    size = pagination.size
    offset = (page - 1) * size
    # 获取当前页数据
    query_location = (select(Location)
                  .offset(offset).limit(size))
    result = await db.execute(query_location)
    locations = result.scalars().all()
    # 获取总记录数
    query_total = (select(func.count())
                   .select_from(Location))
    count = await db.execute(query_total)
    total = count.scalar_one()
    # 计算总页数
    total_pages = (total + size - 1) // size
    paginated_response = PaginatedResponse[Location](
        items=locations,
        page=page,
        size=size,
        total=total,
        total_pages=total_pages
    )
    return Responses(data=paginated_response)