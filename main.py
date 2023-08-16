from tkinter import ttk
from pysinewave import SineWave
from time import time
import tkinter as tk
import requests
import pyperclip
import mgrs

#####################################
# Author: Grokked Bandwidth         #
# Email: GrokkedBandwidth@gmail.com #
#                                   #
# Linux specific:                   #
# sudo apt install xclip            #
# sudo apt install python-tk        #
# sudo apt-get install libportaudio2#
#                                   #
#####################################

#####################################
#       Adjustable Constants        #
#       Adjust these depending on   #
#       what you need them to be    #
#####################################

USERNAME = 'kismet'
PASSWORD = 'kismet'
IP = 'localhost'
MUTE = True

#####################################
#       Aesthetic Constants        #
#       Mess with if you care about #
#       colors                      #
#####################################

BLACK = "#2C3333"
DARK_GREEN = "#212529"
LIGHT_GREEN = "#dee2e6"
OFF_WHITE = "#E7F6F2"
RED = '#ff0000'
ORANGE = '#ffa700'
YELLOW = '#fff400'
GREEN = '#2cba00'
L_GREEN = '#a3ff00'
GREY = "#413F42"
FONT = ("Arial", 10, "bold")
RSSI_FONT = ("Arial", 16, "bold")
mgrs_converter = mgrs.MGRS()

class RSSIBar:
    def __init__(self):
        self.rssi = 0
        self.best_seen = -120
        self.current_channel = 0
        self.current_mac = ""
        self.root = tk.Tk()
        self.root.geometry('1200x280')
        self.root.config(padx=20, pady=20, bg=BLACK)
        self.root.title('Kismet RSSI Bar v 1.6 (Beta)')
        self.sinewave = SineWave()
        self.uuid_list = []
        self.current_time = 0
        self.last_seen_time = 0
        self.best_time_second = 0
        self.best_time_minute = 0
        self.best_time_hour = 0
        self.best_time_seen = 0
        self.start_time = time()
        self.clock_count = 0
        self.df = False

        self.distance_count = 0
        self.best_lat = 0
        self.best_lon = 0
        self.first_location = ''
        self.first_location_time = 0
        self.current_location = ''
        self.mgrs = ''

        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("Horizontal.TProgressbar", background=RED)

        self.lock_params = {
            'channel': self.current_channel,
        }

        self.target_params = {
            'fields': [
                "kismet.device.base.last_time",
                "kismet.device.base.signal/kismet.common.signal.last_signal",
                "kismet.device.base.channel",
                "kismet.device.base.seenby",
                'kismet.device.base.location/kismet.common.location.last/kismet.common.location.geopoint'
            ]
        }
        self.location_params = {
            'fields': ['kismet.common.location.geopoint']
        }

        self.best_panel = tk.PanedWindow(master=self.root, bg=BLACK)
        self.best_panel.grid(column=0, row=2)

        self.channel_panel = tk.PanedWindow(master=self.root, bg=BLACK)
        self.channel_panel.grid(column=0, row=3)

        self.mac_label = tk.Label(text="Enter MAC, ex: FF:FF:FF:FF:FF:FF", bg=BLACK, fg=LIGHT_GREEN, font=FONT)
        self.mac_label.grid(column=0, row=0)

        self.value_label_best = tk.Label(
            master=self.best_panel,
            text=self.update_progress_label_best(-120),
            bg=BLACK,
            fg=LIGHT_GREEN,
            font=FONT)
        self.value_label_best.grid(column=0, row=0)

        self.lock_button = tk.Button(
            master=self.channel_panel,
            command=self.lock_channel,
            text="Lock to Channel",
            bg=DARK_GREEN,
            fg=OFF_WHITE,
            font=FONT)
        self.lock_button.grid(column=1, row=3, padx=10)

        self.channel_label = tk.Label(
            master=self.channel_panel,
            text=self.channel_update("0"),
            bg=BLACK,
            fg=LIGHT_GREEN,
            font=FONT)
        self.channel_label.grid(column=0, row=3, pady=10)

        self.mac_entry = tk.Entry(width=48)
        self.mac_entry.focus()
        self.mac_entry.grid(column=1, row=0, padx=10)

        self.location_button = tk.Button(
            master=self.best_panel,
            command=self.copy_location,
            text=self.update_best_location(0),
            bg=DARK_GREEN,
            fg=OFF_WHITE,
            font=FONT)
        self.location_button.grid(column=0, row=1, padx=10, pady=10)

        self.start_button = tk.Button(
            command=self.toggle_df,
            text="Start DF",
            bg=DARK_GREEN,
            fg=OFF_WHITE,
            font=FONT)
        self.start_button.grid(column=2, row=0, padx=10)

        self.paste_button = tk.Button(
            command=self.paste_mac,
            text="Paste from clipboard",
            bg=DARK_GREEN,
            fg=OFF_WHITE,
            font=FONT)
        self.paste_button.grid(column=3, row=0)

        self.value_label = ttk.Label(
            self.root,
            text=self.update_progress_label("0"),
            background=BLACK,
            foreground=LIGHT_GREEN,
            font=RSSI_FONT)
        self.value_label.grid(column=1, row=2, columnspan=2, rowspan=2)

        self.mute_button = tk.Button(
            command=self.toggle_audio,
            text="Mute Audio",
            bg=DARK_GREEN,
            fg=OFF_WHITE,
            font=FONT)
        self.mute_button.grid(column=4, row=0, padx=10, pady=10)

        self.channel_options_button = tk.Button(
            master=self.root,
            command=self.create_channel_options,
            text='Channel Options',
            bg=DARK_GREEN,
            fg=OFF_WHITE,
            font=FONT)
        self.channel_options_button.grid(column=3, row=2)

        self.pb = ttk.Progressbar(
            self.root,
            maximum=110,
            orient='horizontal',
            mode='determinate',
            length=800,
            style="Horizontal.TProgressbar"
        )
        self.pb.grid(column=0, row=1, columnspan=4, padx=10, pady=10)
        self.check_audio()
        self.screen()
        self.get_uuid_list()
        self.root.mainloop()

# Using API call to retrieve JSON from kismet REST API to obtain signal information

    def screen(self):
        self.current_time = time()
        if self.first_location == '' or self.first_location == [0, 0]:
            self.get_location()
        if self.current_time - self.start_time >= 60:
            self.start_time = self.current_time
        if self.df:
            self.get_rssi(self.current_mac)
        self.root.after(200, self.screen)

    def get_rssi(self, mac):
        response2 = requests.post(
            url=f"http://{USERNAME}:{PASSWORD}@{IP}:2501/devices/by-mac/{mac}/devices.json",
            json=self.target_params
            ).json()
        self.update_values(response2)
        self.update_labels()
        self.check_audio()
        self.pb['value'] = (120 - self.rssi * -1)
        self.rssi_color(self.rssi)

    def update_values(self, json):
        self.last_seen_time = json[0]['kismet.device.base.last_time']
        self.rssi = int(json[0]["kismet.common.signal.last_signal"])
        self.current_channel = str(json[0]["kismet.device.base.channel"])
        self.uuid_list = json[0]['kismet.device.base.seenby']
        if self.rssi >= self.best_seen:
            self.update_best_seen(json)

    def update_labels(self):
        self.value_label['text'] = self.update_progress_label(self.rssi)
        self.value_label_best['text'] = self.update_progress_label_best(self.best_seen)
        self.channel_label['text'] = self.channel_update(self.current_channel)
        self.mac_label['text'] = self.update_current_mac_label(self.current_mac)

    def update_best_seen(self, json):
        self.best_seen = self.rssi
        self.best_time_seen = time()
        try:
            self.best_lat = json[0]['kismet.common.location.geopoint'][1]
            self.best_lon = json[0]['kismet.common.location.geopoint'][0]
            self.mgrs = mgrs_converter.toMGRS(self.best_lat, self.best_lon)
            self.location_button['text'] = self.update_best_location(self.mgrs)
        except TypeError:
            pass

    def update_current_mac_label(self, mac):
        return f"Current MAC: {mac}"

    def update_progress_label(self, signal):
        return f"Current RSSI: {signal}"

    def update_progress_label_best(self, signal):
        return f"Best Seen: {signal} Time since: {round(time() - self.best_time_seen)}"

    def channel_update(self, channel):
        return f"Current Channel: {channel}"

    def update_best_location(self, mgrs):
        return f"Best Seen Location: {mgrs}\nClick to copy"

    def rssi_color(self, rssi):
        global RED, GREY, GREEN, L_GREEN, ORANGE, YELLOW
        if self.current_time - self.last_seen_time > 60:
            self.style.configure("Horizontal.TProgressbar", background=GREY)
        elif rssi < -90:
            self.style.configure("Horizontal.TProgressbar", background=RED)
        elif -90 <= rssi < -80:
            self.style.configure("Horizontal.TProgressbar", background=ORANGE)
        elif -80 <= rssi < -70:
            self.style.configure("Horizontal.TProgressbar", background=YELLOW)
        elif -70 <= rssi < -47:
            self.style.configure("Horizontal.TProgressbar", background=L_GREEN)
        else:
            self.style.configure("Horizontal.TProgressbar", background=GREEN)

    def toggle_df(self):
        if self.df:
            self.df = False
            self.start_button['text'] = 'Start DF'
            self.best_seen = -120
            self.mac_label['text'] = f'Current MAC {self.current_mac} (paused)'
        else:
            self.df = True
            self.start_button['text'] = 'Stop DF'
            self.current_mac = self.mac_entry.get().upper()

    def paste_mac(self):
        pyperclip.init_osx_pbcopy_clipboard()
        self.mac_entry.insert('end', pyperclip.paste())

    def copy_location(self):
        pyperclip.copy(f'{self.mgrs}')

    def get_location(self):
        response3 = requests.post(
            url=f"http://{USERNAME}:{PASSWORD}@{IP}:2501/gps/location.json", json=self.location_params).json()
        if self.first_location == '':
            self.first_location = response3['kismet.common.location.geopoint']
            self.first_location.reverse()
            self.first_location_time = time()
        else:
            self.current_location = response3['kismet.common.location.geopoint']
            self.current_location.reverse()

    def play_audio(self, rssi):
        frequency = 700 - ((rssi*-1)*5)
        self.sinewave.set_frequency(frequency)
        self.sinewave.play()

    def toggle_audio(self):
        global MUTE
        if MUTE:
            MUTE = False
            self.mute_button['text'] = 'Mute Audio'
        else:
            MUTE = True
            self.mute_button['text'] = 'Play Audio'

    def check_audio(self):
        if not MUTE:
            self.mute_button['text'] = 'Mute Audio'
            self.play_audio(self.rssi)
        elif MUTE:
            self.sinewave.stop()
            self.mute_button['text'] = 'Play Audio'

    def lock_channel(self):
        self.lock_params['channel'] = self.current_channel
        interface_list = []
        for item in self.uuid_list:
            interface_list.append(item['kismet.common.seenby.uuid'])
        for item in interface_list:
            lock = requests.post(
                url=f"http://{USERNAME}:{PASSWORD}@{IP}:2501/datasource/by-uuid/{item}/set_channel.cmd",
                json=self.lock_params,)

    def resume_hop(self):
        hop_params = {
            'channels': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14',
                         '36', '40', '44', '48', '52', '56', '60', '64', '100', '104', '108', '112',
                         '116', '120', '124', '128', '132', '136', '140', '144', '149', '153', '157', '161', '165'],
            'hoprate': 5
        }
        self.get_uuid_list()
        for item in self.uuid_list:
            lock = requests.post(
                url=f"http://{USERNAME}:{PASSWORD}@{IP}:2501/datasource/by-uuid/{item}/set_channel.cmd",
                json=hop_params, )

    def get_uuid_list(self):
        self.uuid_list = []
        params = {'fields': ['kismet.datasource.uuid']}
        response5 = requests.post(
            url=f"http://{USERNAME}:{PASSWORD}@{IP}:2501/datasource/all_sources.json",
            json=params).json()
        for item in response5:
            self.uuid_list.append(item['kismet.datasource.uuid'])


    def two_gig_survey(self):
        hop_params = {
            'channels': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14'],
            'hoprate': 5
        }
        self.get_uuid_list()
        for item in self.uuid_list:
            lock = requests.post(
                url=f"http://{USERNAME}:{PASSWORD}@{IP}:2501/datasource/by-uuid/{item}/set_channel.cmd",
                json=hop_params,)

    def five_gig_survey(self):
        hop_params = {
            'channels': ['36', '40', '44', '48', '52', '56', '60', '64', '100', '104', '108', '112', '116', '120', '124', '128', '132', '136', '140', '144', '149', '153', '157', '161', '165'],
            'hoprate': 5
        }
        self.get_uuid_list()
        for item in self.uuid_list:
            lock = requests.post(
                url=f"http://{USERNAME}:{PASSWORD}@{IP}:2501/datasource/by-uuid/{item}/set_channel.cmd",
                json=hop_params, )

    def one_six_eleven_survey(self):
        hop_params = {
            'channels': ['1', '6', '11'],
            'hoprate': 5
        }
        self.get_uuid_list()
        for item in self.uuid_list:
            lock = requests.post(
                url=f"http://{USERNAME}:{PASSWORD}@{IP}:2501/datasource/by-uuid/{item}/set_channel.cmd",
                json=hop_params, )

    def create_channel_options(self):
        hop_panel = tk.PanedWindow(master=self.root, bg=BLACK)
        hop_panel.grid(column=3, row=2)
        resume_button = tk.Button(
            master=hop_panel,
            command=self.resume_hop,
            text="All Hop",
            bg=DARK_GREEN,
            fg=OFF_WHITE,
            font=FONT)
        resume_button.grid(column=0, row=0, pady=10, padx=10)
        two_gig_button = tk.Button(
            master=hop_panel,
            command=self.two_gig_survey,
            text="2.4G Hop",
            bg=DARK_GREEN,
            fg=OFF_WHITE,
            font=FONT)
        two_gig_button.grid(column=1, row=0, pady=10, padx=10)
        five_gig_button = tk.Button(
            master=hop_panel,
            command=self.five_gig_survey,
            text="5G Hop",
            bg=DARK_GREEN,
            fg=OFF_WHITE,
            font=FONT)
        five_gig_button.grid(column=0, row=1, pady=10, padx=10)
        three_hop_button = tk.Button(
            master=hop_panel,
            command=self.one_six_eleven_survey,
            text="1, 6, 11 Hop",
            bg=DARK_GREEN,
            fg=OFF_WHITE,
            font=FONT)
        three_hop_button.grid(column=1, row=1, pady=10, padx=10)
        self.channel_options_button.destroy()


rssi_bar = RSSIBar()
