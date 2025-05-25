from pymodbus.client import ModbusTcpClient


client = ModbusTcpClient(host='kitvideovpn.ru', port=13753)
client.connect()
print(client.connected)
data = client.read_input_registers(0, count=34, slave=255)
print(data.registers)
client.close()
