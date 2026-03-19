import os
import torch
import pandas as pd
from skimage import io, transform
import numpy as np
# import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, utils
import warnings
import torch.nn as nn

warnings.filterwarnings("ignore")
# plt.ion()
# setups the csv for all the images in the dataset - rafi
def setup_csv(data_dir, output_file):
	data = []
	classes = sorted(os.listdir(data_dir))
	if "images.csv" in classes:
		classes.remove("images.csv")
	for i in range(len(classes)):
		cls = classes[i]
		images = os.listdir(f'{data_dir}/{cls}')
		for j in range(len(images)):
			data.append([f'{cls}/{images[j]}', i])
	df = pd.DataFrame(data, columns=['image_path', 'label'])
	df.to_csv(output_file, index=False)
# more dataset stuff (the actual set for pytorch/torchvision) - rafi
class Dataset(Dataset):
	def __init__(self, csv_file, root_dir, transform=None):
		self.data_frame = pd.read_csv(csv_file)
		self.root_dir = root_dir
		self.transform = transform
	def __len__(self):
		return len(self.data_frame)
	def __getitem__(self, idx):
		img_name = os.path.join(self.root_dir,self.data_frame.iloc[idx, 0])
		image = io.imread(img_name)
		if len(image.shape) != 2 and len(image.shape) != 3:
        		print(f"Invalid image shape {image.shape} for file: {img_name}")
		if len(image.shape) == 2:
			image = np.stack([image]*3, axis=-1)
		elif image.shape[2] == 4:
			image = image[:, :, :3]
		label = int(self.data_frame.iloc[idx, 1])
		if self.transform:
			image = self.transform(image)
		return image, label
