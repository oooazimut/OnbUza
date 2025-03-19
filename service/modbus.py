import logging

from config import settings
from pymodbus import ModbusException
from pymodbus.client import AsyncModbusTcpClient, ModbusBaseClient

logger = logging.getLogger(__name__)

def process_data(client: ModbusBaseClient, data: list):
    result = dict()
    result["water_level"] = 100 if 200 > data[0] > 100 else data[0]
    pressure = data[2:4]
    pressure.reverse()
    result["pressure"] = client.convert_from_registers(
        pressure,
        data_type=client.DATATYPE.FLOAT32,
    )
    result["pump_condition"] = data[-1]
    return result


async def poll_registers(address, count) -> dict | None:
    try:
        async with AsyncModbusTcpClient(
            settings.modbus.host,
            port=settings.modbus.port,
            timeout=3,
            retries=1,
            reconnect_delay=0.5,
            reconnect_delay_max=0.5,
        ) as client:
            if not client.connected:
                logger.error("Нет соединения с ПР-103")
                return

            try:
                data = await client.read_holding_registers(address, count=count)
                if data.isError():
                    logger.error(f"Чтение регистров завершилось ошибкой: {data}")
                    return
                return process_data(client, data.registers)
            except ModbusException as exc:
                logger.error(f"Ошибка протокола Modbus: {exc}")
                return

    except Exception as e:
        logger.error(f"Общая ошибка при подключении: {e}")
        return
