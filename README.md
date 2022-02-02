# Virtual-Whiteboard
## Description
A python project to draw on live video captured from the webcam(or any other camera) and broadcast it to a virtual camera via OBS Studio.
## Installation Instructions:
For the program to run properly followin installation instructions should be followed:
1. Clone the repository to the desired path.
2. Download the python packages of specified version mentioned in the [requirements.txt](https://github.com/Shriyam-Avasthi/Virtual-Whiteboard/blob/main/requirements.txt) file.
Or, run the command:
  `pip install -r /path/to/requirements.txt` 
  
3. Install [OBS Studio](https://obsproject.com/) for your operating system then follow.
#### Setting Up Virtual Camera in OBS:
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
