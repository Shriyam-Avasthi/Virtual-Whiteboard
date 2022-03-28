# Virtual-Whiteboard
## Description
A python project to draw on live video captured from the webcam(or any other camera) and broadcast it to a virtual camera via OBS Studio.

## Demo
You can find the project's demo at my youtube page [here](https://www.youtube.com/watch?v=i-tAN5yTxr8).

## Installation Instructions:
For the program to run properly followin installation instructions should be followed:
1. Clone the repository to the desired path.
2. Download the python packages of specified version mentioned in the [requirements.txt](https://github.com/Shriyam-Avasthi/Virtual-Whiteboard/blob/main/requirements.txt) file.
Or, run the command:
  `pip install -r /path/to/requirements.txt` 
 
**Note: The following steps are required only if you want to broadcast the output to other softwares. To just use this program, without broadcasting the output, above two steps are all what you need to get started.**

3. Install [OBS Studio](https://obsproject.com/) for your operating system then follow the following instructions to set up virtual camera.
#### Setting Up Virtual Camera in OBS (To use the output in other softwares):
4. Open OBS Studio. Following screen will appear: 

 ![Open View](https://user-images.githubusercontent.com/56196449/152128308-50622234-3f69-40da-9299-00c9420f2841.png)

5. Under the **Sources** tab, click on **+** button and select **Video Capture Device**.

 ![image](https://user-images.githubusercontent.com/56196449/152129594-f3e30041-eda8-4268-8e6b-a5eb8123bb9b.png)
 
 6. Click on **Create New** radio button and enter the name of the virtual camera, and click **OK** Button.

 ![image](https://user-images.githubusercontent.com/56196449/152130044-fe8bc9ea-67e1-4c1e-be08-0bfa0843d634.png)

 7. Select **OBS Virtual Camera** from the **Device** dropdown, leaving other setting unchanged, click **OK** Button.

![image](https://user-images.githubusercontent.com/56196449/152130645-f692aaa6-0bd7-4f85-be09-a88baf99db00.png)

 8. Following screen will appear.

![image](https://user-images.githubusercontent.com/56196449/152131168-9af81cac-eb1c-4db3-a32f-c07662f03f3a.png)
Virtual camera has been set up successfully.

## How to Use:
To start the application, run the **GUI.py** file. 
The program works on varius hand gestures. These are explained below:
1. Index finger Click: To toggle the active state of the currently selected tool.

![Single Finger Click](https://user-images.githubusercontent.com/56196449/160415897-b31e6eb9-436f-43fa-a121-c397b02a20ea.gif)

2. Index Finger drag : To draw on the canvas

3. Index And Middle finger drag : To Move the mouse inside the GUI.

![Mouse Tracking GIF](https://user-images.githubusercontent.com/56196449/160416168-56ee1921-dcb4-4943-a40a-d44bafcac8bc.gif)

4. Index and Middle finger click : To simulate mouse click, to click the GUI buttons.

![Mouse Click](https://user-images.githubusercontent.com/56196449/160416350-13fd88e8-de18-4c4a-a09a-ac6a1d1b61c6.gif)

5. Index finger and thumb pan : To change the draawing size of the tool.

![Size Change](https://user-images.githubusercontent.com/56196449/160416588-ee70077e-a1a6-40de-a3cb-86a1d46bcdae.gif)

6. Fist drag : To scroll the canvas.

![Canvas Move](https://user-images.githubusercontent.com/56196449/160416701-ff78c8d3-8208-4a50-8f91-cc5c31abc715.gif)

