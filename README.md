# Virtual-Whiteboard
## Description
A Python project to draw on live video captured from the webcam(or any other camera) and broadcast it to a virtual camera via OBS Studio.

## Demo
You can find the project's demo at my YouTube page [here](https://www.youtube.com/watch?v=i-tAN5yTxr8).

## Installation Instructions:
For the program to run properly, the following installation instructions should be followed:
1. Clone the repository to the desired path.
2. Download the Python packages of the specified version mentioned in the [requirements.txt](https://github.com/Shriyam-Avasthi/Virtual-Whiteboard/blob/main/requirements.txt) file.
Or, run the command:
  `pip install -r /path/to/requirements.txt` 
 
**Note: The following steps are required only if you want to broadcast the output to other software. To just use this program, without broadcasting the output, the above two steps are all that you need to get started.**

3. Install [OBS Studio](https://obsproject.com/) for your operating system then follow the following instructions to set up the virtual camera.

4. Open OBS Studio.

5. Under the **Sources** tab, click on **+** button and select **Video Capture Device**.
 
 6. Click on **Create New** radio button and enter the name of the virtual camera, and click **OK** Button.

 7. Select **OBS Virtual Camera** from the **Device** dropdown, leaving other setting unchanged, click **OK** Button.
    
![Demo GIF](https://github.com/Shriyam-Avasthi/Virtual-Whiteboard/assets/56196449/4ca19c7c-96f5-4157-af1d-af793cfc7262)

The virtual camera has been set up successfully.

## How to Use:
To start the application, run the **GUI.py** file. 
The program works on various hand gestures. These are explained below:
1. Index finger Click: To toggle the active state of the currently selected tool.

![Single Finger Click](https://user-images.githubusercontent.com/56196449/160415897-b31e6eb9-436f-43fa-a121-c397b02a20ea.gif)

2. Index Finger drag: To draw on the canvas

3. Index And Middle finger drag: To Move the mouse inside the GUI.

![Mouse Tracking GIF](https://user-images.githubusercontent.com/56196449/160416168-56ee1921-dcb4-4943-a40a-d44bafcac8bc.gif)

4. Index and Middle finger click: To simulate a mouse click to click the GUI buttons.

![Mouse Click](https://user-images.githubusercontent.com/56196449/160416350-13fd88e8-de18-4c4a-a09a-ac6a1d1b61c6.gif)

5. Index finger and thumb pan: To change the drawing size of the tool.

![Size Change](https://user-images.githubusercontent.com/56196449/160416588-ee70077e-a1a6-40de-a3cb-86a1d46bcdae.gif)

6. Fist drag: To scroll the canvas.

![Canvas Move](https://user-images.githubusercontent.com/56196449/160416701-ff78c8d3-8208-4a50-8f91-cc5c31abc715.gif)

