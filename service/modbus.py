import logging
from collections.abc import Generator

from config import settings
from pymodbus import ModbusException
from pymodbus.client import AsyncModbusTcpClient, ModbusBaseClient

logger = logging.getLogger(__name__)

START_HOLD = 0
LEN_HOLD = 4
START_INPUT = 1
LEN_INPUT = 34
SELECTORS = {0: "--------", 1: "ДТ-1", 2: "ДТ-2", 3: "АИ-9х", 4: "АИ-9х", 5: "РЕЗ."}


def convert_to_bin(num: int, zerofill: int) -> list[int]:
    return list(map(int, bin(num)[2:].zfill(zerofill)[::-1]))


def chunks(array: list, chunk: int) -> Generator[list]:
    for i in range(0, len(array), chunk):
        yield array[i : i + chunk]


def convert_values(client: ModbusBaseClient, data_chunks: Generator[list[int]]):
    return [
        client.convert_from_registers(
            chunk,
            data_type=client.DATATYPE.FLOAT32,
            word_order="little",
        )
        for chunk in data_chunks
    ]


def process_data(client: ModbusBaseClient, data: list):
    result = dict(
        selectors=[SELECTORS[i] for i in data[:4]],
        uzas=convert_to_bin(data[4], zerofill=4),
        # pumpworks=[f'{i} ч.' for i in data[5:10]],
        # temperatures=[f'{round(i)} °C' for i in convert_values(client, chunks(data[10:20], 2))],
        # pressures=[f'{i} МПа'  for i in convert_values(client, chunks(data[20:], 2))],
        pumpworks=data[5:10],
        temperatures=convert_values(client, chunks(data[10:20], 2)),
        pressures=convert_values(client, chunks(data[20:30], 2)),
        gas_sensors=convert_values(client, chunks(data[30:], 2)),
    )
    return result


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
            result = process_data(client, hold_regs.registers)
            return result
        except ModbusException as exc:
            logger.error(f"Ошибка протокола Modbus: {exc}")
            return

    # except Exception as e:
    #     logger.error(f"Общая ошибка при подключении: {e}, {type(e)}")
    #     return
