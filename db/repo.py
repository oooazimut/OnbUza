from service.modbus import poll_registers


async def save_data():
    data = await poll_registers()

