import socket
import os
import struct

def recvall(c, n):
	data = bytearray()
	while len(data) < n:
		packet = c.recv(n-len(data))
		if not packet:
			return None
		data.extend(packet)
	return bytes(data)
def send_msg(c, data):
	c.sendall(struct.pack('>I', len(data)) + data)
def recv_msg(c):
	raw_len = recvall(c, 4)
	if not raw_len:
		return None
	msg_len = struct.unpack('>I', raw_len)[0]
	return recvall(c, msg_len)

HOST = "192.168.1.148"
PORT = 2012
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.connect((HOST, PORT))
	inf_type_flag = 2
	while True:
		data = recv_msg(s)
		if data:
			print("data received")
			if inf_type_flag == 2:
				# req images
				inf_type_flag = 0
				send_msg(s, "images".encode('utf-8'))
				print("requesting images")
			elif inf_type_flag == 0:
				print("writing image")
				open(f"taken_images/IMG{len(os.listdir('taken_images'))}.jpg", "wb").write(data)
				print("image written")
				inf_type_flag = 1
				# now, recv info
				send_msg(s, "info".encode('utf-8'))
				print("requesting info")
			else:
				# info now recvd, stop process
				print("writing info")
				open("info.txt", "a").write(data.decode('utf-8'))
				print("info appended")
				send_msg(s, "end".encode('utf-8'))
				print("ending process")
				inf_type_flag = 2
