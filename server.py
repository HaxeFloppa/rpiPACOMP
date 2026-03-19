import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import img_ds
import socket
import random
from time import sleep
import os
from picamzero import Camera
import sys
import subprocess
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

cam = Camera()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", 2012))
print("listening on port 2012")
s.listen()
if sys.argv[1] == "debug":
	client = subprocess.Popen(["python", "client/client.py"], stdout=subprocess.PIPE, text=True)
	print("debug activated. client running locally.")
else:
	print("standard mode. expecting client to be ran separately.")
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(44944, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)
    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = torch.flatten(x, 1) # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
transform = transforms.Compose([
	transforms.ToPILImage(),      # Convert numpy array to PIL Image
	transforms.Lambda(lambda img: img.convert('RGB')),
	transforms.Resize((224, 224)), # Resize to model's expected size
	transforms.ToTensor(),         # Converts to float32 and scales to [0, 1]
	transforms.Normalize(mean=[0.5, 0.5, 0.5],std=[0.5, 0.5, 0.5]) # normalise untrained model
])
batch_size = 4
classes = ('eafi', 'natan')
while True:
	print("making image")
	img_name = f"taken_images/imgs/IMG{str(len(os.listdir('taken_images/imgs')))}.jpg"
	cam.start_preview()
	cam.take_photo(img_name)
	cam.stop_preview()
	print("image taken")
	image_check = input("check images taken? (y/n, default to n)")
	if image_check == 'y':
		print(os.listdir("taken_images/imgs"))
	else:
		pass
	img_ds.setup_csv("classes", "classes/images.csv")
	img_ds.setup_csv("taken_images", "taken_images/images.csv")
	trainset = img_ds.Dataset(csv_file="classes/images.csv", root_dir="classes", transform=transform)
	trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch_size, shuffle=True, num_workers=0)
	testset = img_ds.Dataset(csv_file="taken_images/images.csv", root_dir="taken_images", transform=transform)
	testloader = torch.utils.data.DataLoader(testset, batch_size=batch_size, shuffle=False, num_workers=0)
	print("datasets sorted")
	net = Net()
	criterion = nn.CrossEntropyLoss()
	optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)
	print("training")
	for epoch in range(2):
		running_loss = 0.0
		for i, data in enumerate(trainloader, 0):
			inputs, labels = data
			optimizer.zero_grad()
			outputs = net(inputs)
			loss = criterion(outputs, labels)
			loss.backward()
			optimizer.step()
			running_loss += loss.item()
		if i % 2000 == 1999:
			print(f'[{epoch + 1}, {i + 1:5d}] loss: {running_loss / 2000:.3f}')
			running_loss = 0.0
	print('finished training')
	dataiter = iter(testloader)
	images, labels = next(dataiter)
	# img_grid = torchvision.utils.make_grid(images)
	# print(img_grid.tolist())
	# print('What the images actually are: ', ' '.join(f'{classes[labels[j]]:5s}' for j in range(4)))
	print(f"What the images actually are: {classes}")
	outputs = net(images)
	_, predicted = torch.max(outputs, 1)
	print(f"predicted: {classes[predicted[0]]}")
	c, addr = s.accept()
	with c:
		send_msg(c, "begin".encode('utf-8'))
		print(f"connection from {addr}")
		data = b""
		while True:
			print(data.decode())
			while True:
				data = recv_msg(c)
				if data:
					break
			if data.decode('utf-8') == "images":
				print("sending image")
				send_msg(c, open(img_name, "rb").read())
			elif data.decode('utf-8') == "info":
				print("sending info")
				send_msg(c, f"{classes[predicted[0]]}\n".encode())
			elif data.decode('utf-8') == "end":
				if sys.argv[1] == "debug":
					sys.exit()
				break
			else:
				print("unsure what recvd data is")
				continue
	sleep(1)
