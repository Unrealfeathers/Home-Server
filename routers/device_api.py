from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import select

from db.operations import get_db
from models.data import EnvironmentData
from models.devices import Device
from models.users import User
from schemas.device_schema import DeviceAdd, DeviceUpdate, LTHData, DeviceUpload, DeviceStatusUpdate, DeviceSearch, \
    DeviceList, DeviceStatusList
from schemas.pagination_schema import PaginatedResponse, PaginatedRequest
from schemas.responses_schema import Responses
from utils.security import get_current_user

router = APIRouter(
    prefix="/device",
    tags=["Device"]
)


@router.put("/status", response_model=Responses)
async def status(
        update_status: DeviceStatusUpdate,
        db: AsyncSession = Depends(get_db)
):
    query = select(Device).where(Device.serial_number == update_status.serial_number)
    device = (await db.scalars(query)).first()
    if not device:
        return Responses(status_code=1, message="Device not found.")
    device.firmware_version = update_status.firmware_version
    device.last_online = datetime.now()
    device.is_online = update_status.is_online
    db.add(device)
    await db.commit()
    await db.refresh(device)
    return Responses()


@router.post('/upload', response_model=Responses)
async def upload(
        upload_data: DeviceUpload[LTHData],
        db: AsyncSession = Depends(get_db)
):
    query = select(Device).where(Device.serial_number == upload_data.serial_number)
    device = (await db.scalars(query)).first()
    envir_data = EnvironmentData(
        device_id=device.id,
        timestamp=upload_data.timestamp,
        temperature=upload_data.message.temp,
        humidity=upload_data.message.humi,
        illuminance=upload_data.message.lux,
        location_id=device.location_id,
    )
    db.add(envir_data)
    await db.commit()
    return Responses()


@router.post("/add", response_model=Responses)
async def add(
        device_add: DeviceAdd,
        db: AsyncSession = Depends(get_db),
):
    device = Device(
        name=device_add.name,
        type_id=device_add.type_id,
        serial_number=device_add.serial_number,
        mac_address=device_add.mac_address,
        firmware_version=device_add.firmware_version,
        created_at=datetime.now(),
        last_online=datetime.now(),
        location_id=device_add.location_id,
    )
    db.add(device)
    await db.commit()
    return Responses(message="Device added.")


@router.delete("/delete", response_model=Responses)
async def delete(
        device_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        return Responses(status_code=1, message="Not authorized to delete device.")
    query = select(Device).where(Device.id == device_id)
    device = (await db.scalars(query)).first()
    if not device:
        return Responses(status_code=1, message="Device not found.")
    await db.delete(device)
    await db.commit()
    return Responses(message="Device deleted.")


@router.get("/find", response_model=Responses[Device])
async def find(
        device_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        return Responses(status_code=1, message="Not authorized to find device.")
    query = select(Device).where(Device.id == device_id)
    device = (await db.scalars(query)).first()
    if not device:
        return Responses(status_code=1, message="Device not found.")
    return Responses(data=device)


@router.patch("/update", response_model=Responses)
async def update(
        device_update: DeviceUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        return Responses(status_code=1, message="Not authorized to update device.")
    query = select(Device).where(Device.id == device_update.id)
    device = (await db.scalars(query)).first()
    if not device:
        return Responses(status_code=1, message="Device not found.")
    device.name = device_update.name
    device.location_id = device_update.location_id
    db.add(device)
    await db.commit()
    await db.refresh(device)
    return Responses(message="Device updated.")


@router.get("/list", response_model=Responses[PaginatedResponse[DeviceList]])
async def devices_list(
        location_id: int | None = None,
        device_search: DeviceSearch = Depends(DeviceSearch),
        pagination: PaginatedRequest = Depends(PaginatedRequest),
        db: AsyncSession = Depends(get_db),
):
    # 分页数据
    page = pagination.page
    size = pagination.size
    offset = (page - 1) * size
    # 动态构建过滤条件列表
    filters = []
    if device_search.type_id is not None:
        filters.append(Device.type_id == device_search.type_id)
    if device_search.location_id is not None:
        filters.append(Device.location_id == device_search.location_id)
    if location_id is not None:
        filters.append(Device.location_id == location_id)
    if device_search.is_online is not None:
        filters.append(Device.is_online == device_search.is_online)
    # 获取当前页数据
    query_device = (select(Device)
                    .options(selectinload(Device.device_type),selectinload(Device.location))
                    .where(and_(*filters))
                    .offset(offset).limit(size))
    result = await db.execute(query_device)
    devices = result.scalars().all()
    items: list[DeviceList] = []
    for device in devices:
        item = DeviceList(
            id=device.id,
            name=device.name,
            type_name=device.device_type.name,
            location_name=device.location.name,
            mac_address=device.mac_address,
            serial_number=device.serial_number,
            firmware_version=device.firmware_version,
            created_at=device.created_at,
            is_online=device.is_online,
            last_online=device.last_online,
        )
        items.append(item)
    # 获取总记录数
    query_total = (select(func.count())
                   .select_from(Device)
                   .where(and_(*filters)))
    count = await db.execute(query_total)
    total = count.scalar_one()
    # 计算总页数
    total_pages = (total + size - 1) // size
    paginated_response = PaginatedResponse[DeviceList](
        items=items,
        page=page,
        size=size,
        total=total,
        total_pages=total_pages
    )
    return Responses(data=paginated_response)

@router.get("/status", response_model=Responses[PaginatedResponse[DeviceStatusList]])
async def devices_status_list(
        location_id: int,
        pagination: PaginatedRequest = Depends(PaginatedRequest),
        db: AsyncSession = Depends(get_db),
):
    # 分页数据
    page = pagination.page
    size = pagination.size
    offset = (page - 1) * size
    # 动态构建过滤条件列表
    filters = []
    if location_id is not None:
        filters.append(Device.location_id == location_id)
    # 获取当前页数据
    query_device = (select(Device)
                    .options(selectinload(Device.device_type),selectinload(Device.location))
                    .where(and_(*filters))
                    .offset(offset).limit(size))
    result = await db.execute(query_device)
    devices = result.scalars().all()
    items: list[DeviceStatusList] = []
    for device in devices:
        item = DeviceStatusList(
            id=device.id,
            name=device.name,
            type_name=device.device_type.name,
            location_name=device.location.name,
            mac_address=device.mac_address,
            serial_number=device.serial_number,
            firmware_version=device.firmware_version,
            created_at=device.created_at,
            is_online=device.is_online,
            last_online=device.last_online,
            status=device.status,
            operation=device.device_type.capitalize,
        )
        items.append(item)
    # 获取总记录数
    query_total = (select(func.count())
                   .select_from(Device)
                   .where(and_(*filters)))
    count = await db.execute(query_total)
    total = count.scalar_one()
    # 计算总页数
    total_pages = (total + size - 1) // size
    paginated_response = PaginatedResponse[DeviceStatusList](
        items=items,
        page=page,
        size=size,
        total=total,
        total_pages=total_pages
    )
    return Responses(data=paginated_response)
