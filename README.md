# Kismet RSSI Bar

The Kismet RSSI Bar is a Kismet addon to find APs and client devices based on RSSI.
The Kismet RSSI Bar relies on the Kismet API and requires the device that is running
the RSSI bar to be either on the same network or same device. 

## Linux Requirements
 
 * sudo apt install xclip
 * sudo apt install python-tk
 * sudo apt install libportaudio2

## Adjustable Constants

![image](https://user-images.githubusercontent.com/96986202/203411908-3631558c-8e68-4379-9c5f-edbc3b1e4694.png)

The first three constants need to be correct and match the system
you are running Kismet on in order to function properly. Username 
and Password should be established by the user when running Kismet
for the first time. IP will be the IP of the machine running Kismet,
or will be 'localhost' or '127.0.0.1' if being run locally on the same
device.

MUTE and DISTANCE can be adjusted depending on the desired behavior of the user.
DISTANCE is in meters. 

## Notes

This project was developed while working on Angela Yu's 100 Days of Code
and is being continously updated with better coding practices. Version 2 of
this project will most likely be in a web interface. 
