from datetime import datetime
from sqlalchemy.orm import sessionmaker
from service.modbus import poll_registers


async def save_data(db_pool: sessionmaker):
    data = await poll_registers()
    data = [*data["pumps"], *data["gas_sensors"]]
    dttm = datetime.now().replace(microsecond=0)

    for i in data:
        i.dttm = dttm

    async with db_pool() as session:
        session.add_all(data)
        await session.commit()
