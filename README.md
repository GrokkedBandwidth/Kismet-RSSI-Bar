# Kismet RSSI Bar

The Kismet RSSI Bar is a Kismet addon to find APs and client devices based on RSSI.
The Kismet RSSI Bar relies on the Kismet API and requires the device that is running
the RSSI bar to be either on the same network or same device. 

##  Installation Requirements

```
$ sudo apt install xclip
$ sudo apt install python-tk
$ sudo apt install libportaudio2
$ pip3 install -r requirements.txt
```

## Launching
After Kismet is running, run the following:
````
$ cd kismet_rssi_bar
$ python3 main.py
````

## Manual
![RSSI-Bar](https://user-images.githubusercontent.com/96986202/224187301-ce3f64cb-a8f8-48a7-9996-1b5e91860955.png)

### Start up
To start the rssi bar, a Kismet server must be running at the designated IP in main.py. 

### Start DF
Once a MAC has been identified, enter it into the top bar on the screen and press 'Start DF'. Once started, the progress bar will begin adjusting based on the 
received RSSI. The 'Best Seen' will adjust based on the current DF session and will reset per DF session. This value is not the same as the best seen value inside
Kismet. Time since is a value that will count the time, in seconds, from the last best seen time. 
'Best Seen Location' Will change from 0, 0 once 'Best Seen' changes and Kismet has GPS. This value will change each time 'Best Seen' changes. 'Current Channel' Will 
update based on the channel value in Kismet and 'Lock to Channel' will lock all Kismet interfaces to the value in 'Current Channel'.

### Channel Options
Once clicked, channel options will offer several channel presets not available in Kismet. Each channel preset does not turn on any channels HT or VHT options. 

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
and is being continuously updated with better coding practices. Version 2 of
this project will most likely be in a web interface. 
