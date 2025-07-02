import logging
from collections.abc import Generator

from config import PUMPS, settings
from db.models import Gas_Sensor, Pump
from pymodbus import ModbusException
from pymodbus.client import AsyncModbusTcpClient, ModbusBaseClient

logger = logging.getLogger(__name__)

START_HOLD = 0
LEN_HOLD = 4
START_INPUT = 1
LEN_INPUT = 34
# SELECTORS = {0: "--------", 1: "ДТ-1", 2: "ДТ-2", 3: "АИ-9х", 4: "АИ-9х", 5: "РЕЗ."}
SELECTORS = {0: "--------"}
SELECTORS.update(dict(zip(range(1, 6), PUMPS)))


def convert_to_bin(num: int, zerofill: int) -> list[int]:
    return list(map(int, bin(num)[2:].zfill(zerofill)[::-1]))


def chunks(array: list, chunk: int) -> Generator[list]:
    for i in range(0, len(array), chunk):
        yield array[i : i + chunk]


def convert_values(client: ModbusBaseClient, data_chunks: Generator[list[int]]):
    result = [
        client.convert_from_registers(
            chunk,
            data_type=client.DATATYPE.FLOAT32,
            word_order="little",
        )
        for chunk in data_chunks
    ]
    return result


def process_data(client: ModbusBaseClient, data: list):
    selectors = [SELECTORS[i] for i in data[:4]]
    uzas = convert_to_bin(data[4], zerofill=4)
    pumpworks = data[5:10]
    temperatures = convert_values(client, chunks(data[10:20], 2))
    pressures = convert_values(client, chunks(data[20:30], 2))
    gas_sensors = [
        Gas_Sensor(name=nm, value=vl)
        for nm, vl in enumerate(convert_values(client, chunks(data[30:], 2)), start=1)
    ]
    pumps = [
        Pump(name=i[0], pressure=round(i[1], 1), temperature=round(i[2], 1), work=i[3])
        for i in zip(PUMPS, pressures, temperatures, pumpworks)
    ]
    return dict(
        selectors=selectors,
        pumps=pumps,
        gas_sensors=gas_sensors,
        uzas=uzas,
    )


async def poll_registers() -> dict | None:
    # try:
    async with AsyncModbusTcpClient(
        settings.modbus.host,
        port=settings.modbus.port,
        timeout=3,
        retries=1,
        reconnect_delay=0.5,
        reconnect_delay_max=0.5,
    ) as client:
        if not client.connected:
            logger.error("Нет соединения с ПЛК!")
            return

        try:
            hold_regs = await client.read_holding_registers(
                START_HOLD,
                count=LEN_HOLD,
            )
            input_regs = await client.read_input_registers(
                START_INPUT,
                count=LEN_INPUT,
            )
            if hold_regs.isError() or input_regs.isError():
                logger.error(
                    f"Чтение регистров завершилось ошибкой: {hold_regs, input_regs}"
                )
                return
            hold_regs.registers.extend(input_regs.registers)
            return process_data(client, hold_regs.registers)

        except ModbusException as exc:
            logger.error(f"Ошибка протокола Modbus: {exc}")
            return

    # except Exception as e:
    #     logger.error(f"Общая ошибка при подключении: {e}, {type(e)}")
    #     return
