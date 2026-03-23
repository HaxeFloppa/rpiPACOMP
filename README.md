# Raspberry Pi PaPi Competition Submission - "Guardin"
Guardin is our submission for this year's (2026) PaPi competition. It uses machine learning and image classification to aid teachers in monitoring playgrounds or playground environments. It communicates with an app that would run on a teacher's computer, providing them with the taken image and what the AI identified alongside it.

For a better explanation (including devlogs), a powerpoint is available for download [here](https://stals-my.sharepoint.com/:p:/g/personal/rhailu29_stals_org_uk/IQCdVCPODnTDTLrIY68WzOuiAaEj8kAYt276rUS3mzj8p2U?e=lIRDJa). It was too big to be directly uploaded for use in the github repo.
# Comprehensive Build Guide
First, you'll want to write the code for the server. This requires:
- A Raspberry Pi and a starter kit
- A PiCamera
- Raspberry Pi OS
- Python
- Python packages including PyTorch, Torchvision, NumPy, Skimage, and PiCamZero.

1. Using PyTorch & TorchVision - following the official PyTorch documentation, put together the code for a simple image classifier.
2. Using python's built-in socket package, create a basic TCP socket section which will be used to send the images taken and the info the classifier identified.
3. Using the PiCamZero package make a setup so every second a picture is taken. Adjust the image classification process and socket program to also run every second.
4. Using PyTorch documentation again, create your own custom dataset setup to work with CSV files. Adjust the code so that a new, special dataset is made every second for each image taken.
To break down what is happening:
- At the start of the program the image classifier is trained on a dataset which is meant to consist of images of bullying. (This code is only a proof of concept, so the dataset consists of pictures of Rafael and Nathan)
- Afterwards, an infinite loop takes place. It starts with an image being taken and a custom dataset being created and loaded using that taken image.
- Run the taken image through the trained image classifier and save the results (aka what the classifier identified the image as out of the dataset it was trained with)
- Using socket, it'll send both the image and results over to a connected client.

Now you'll want to make a client for the server to communicate with.
This'll require:
- Any computer
- Python
- Python packages including Pillow.

1. Using Tkinter, create a basic GUI which includes four buttons.
- Button 1 is called "SAFE".
- Button 2 is called "REVIEW".
- Button 3 is called "DANGER".
- Button 4 is called "INFO".
2. Using Pillow, make it so when images are received it appears in a wide section in the middle of the screen on the homepage.
3. Make it so that each button leads you to a different page in the GUI.
- "SAFE" would lead to a page which shows images identified as "SAFE" by the image classifier.
- "REVIEW" would lead to a page which shows images identified as "REVIEW" by the image classifier.
- "DANGER" would lead to a page which shows images identified as "DANGER" by the image classifier.
- "INFO" would lead to a small text page which would explain how to navigate the app.
4. On the homepage make a small panel at the bottom of the GUI.
- Add a label which will change according to logs from the underlying code and also showing incoming results.
- Add a button at the very bottom which will begin the process of receiving images and results from the server. This button will say "Start Receiving".
To break down what is happening:
- When you click the button "Start Receiving", the client will begin the process of collecting images and their results from the server.
- The results appear in the text at the bottom panel and the images will appear in the middle of the homepage. The images and text are saved in a folder.
- Based on the given results images will appear on the three different flags for images (SAFE, REVIEW and DANGER).
