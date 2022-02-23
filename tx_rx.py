import can
import time
import os
import array as arr
import struct
import threading

kite_mode_value_int = arr.array('i', [0x00, 0x01, 0x02, 0x03, 0x04, 0x05])
alarm_value_int = arr.array('q', [0x01, 0x02, 0x03])
count = 0

print('Bring up CAN0....')
# Bring up can0 interface at 200kbps
os.system("sudo ip link set can0 type can restart-ms 100")
os.system("sudo /sbin/ip link set can0 up type can bitrate 250000")
time.sleep(0.1)
print('Press CTL-C to exit')

try:
	bus = can.interface.Bus(channel='can0', bustype='socketcan_native')
	#bus = can.ThreadSafeBus(channel='can0', bustype='socketcan_native')
except OSError:
	print('Cannot find PiCAN board.')
	exit()

def periodic_send(bus,x,i,j):
	"""
	send a message every 200ms
	"""
	#print("starting to send a message every 200ms")
	power_consu = struct.pack('h',x)
	#q = k.to_bytes(2,'big',signed=True)
	kite_mode_value_byte = kite_mode_value_int[i].to_bytes(1, 'little')
	alarm_value_byte = alarm_value_int[j].to_bytes(1,'little')
	data_to_send =   power_consu  + kite_mode_value_byte + alarm_value_byte + b'\xff' + b'\xff' + b'\xff' + b'\x07'
	#data_to_send = [0xff,0xff,0xff,0xff,0xff,0xff,0xff, j]
	msg = can.Message(arbitration_id = 0xF80,data = data_to_send  ,extended_id=True)
	bus.send(msg)
	time.sleep(0.2)
	global count
	count += 1
	print(count)
def receive():
	"""
	Receives all messages and prints them to the console until Ctrl+C is pressed.
	"""
	message = bus.recv()   # Wait until a message is received.
	c = ' Time: {0:f}   ID: {1:x}   Dlc: {2:x} '.format(message.timestamp, message.arbitration_id, message.dlc)
	s='  Data:  '
	for i in range(message.dlc ):
		s +=  '{0:x} '.format(message.data[i])
	print(' {}'.format(c+s))
    

filters = [{"can_id": 0xF81, "can_mask": 0xFFF, "extended": True},
           {"can_id": 0x583, "can_mask": 0xFFF, "extended": True}]
bus.set_filters(filters)
x = 0
# Main loop
try:  
	while True:
		    for i in range(0,6):
		        for j in range(0,2):
		            periodic_send(bus,x,i,j)
		            receive()
		            x+=1
		    

except KeyboardInterrupt:
	#Catch keyboard interrupt
	os.system("sudo /sbin/ip link set can0 down")
	print('\n\rKeyboard interrtupt')	


