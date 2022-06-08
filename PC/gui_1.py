from threading import Thread, Lock
import socket
import json
import os
import time
import tkinter as tk
import tkinter.messagebox
import customtkinter
from PIL import Image

# Modes: "System" (standard), "Dark", "Light"
customtkinter.set_appearance_mode("System")
# Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):
    PATH = os.path.dirname(os.path.realpath(__file__))
    WIDTH = 780
    HEIGHT = 520

    def __init__(self):
        super().__init__()
        # ============== client settings ================
        self.streamLock = Lock()
        self.clientSocket = ""
        self.IP = socket.gethostbyname(socket.gethostname())
        self.PORT = 5005
        self.messageSent = {'ping': "0"}
        self.messageReceived = {}
        self.chat = "Waiting \n"
        self.activeAction = ''
        self.isConnected = False
        self.transmission = True

        # ============== gui settings ================
        # self.title("Robo Face Control :{} IP_Number :{}".format(
        #     self.server_name, self.ip_address))
        self.title("Robo Face Control")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")

        # call .on_closing() when app gets closed
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # ============ create two frames ============

        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self,
                                                 width=150,
                                                 corner_radius=10)
        self.frame_left.grid(row=0, column=0, sticky="nswe", padx=5)

        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)

        # ============ frame_left ============

        # configure grid layout (1x11)
        # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(0, minsize=11)
        self.frame_left.grid_rowconfigure(6, weight=1)  # empty row as spacing
        # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(8, minsize=20)
        # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(11, minsize=10)

        self.sol_isim = customtkinter.CTkLabel(master=self.frame_left,
                                               text="Fonsiyonlar",
                                               text_font=("Roboto Medium", -12))  # font name and size in px
        self.sol_isim.grid(row=1, column=0, pady=5, padx=10)

        self.BTN_loading = customtkinter.CTkButton(master=self.frame_left,
                                                   height=15,
                                                   text="Loading",
                                                   border_width=3,   # <- custom border_width
                                                   fg_color=None,   # <- no fg_color
                                                   command=lambda: self.send_command('loading'))
        self.BTN_loading.grid(row=2, column=0, pady=10, padx=20)
        self.BTN_home = customtkinter.CTkButton(master=self.frame_left,
                                                height=15,
                                                text="Home",
                                                border_width=3,   # <- custom border_width
                                                fg_color=None,   # <- no fg_color
                                                command=lambda: self.send_command('home'))
        self.BTN_home.grid(row=3, column=0, pady=10, padx=20)

        self.BTN_clock = customtkinter.CTkButton(master=self.frame_left,
                                                 height=15,
                                                 text="Clock",
                                                 border_width=3,   # <- custom border_width
                                                 fg_color=None,   # <- no fg_color
                                                 command=lambda: self.send_command('clock'))
        self.BTN_clock.grid(row=4, column=0, pady=10, padx=20)

        self.BTN_weather = customtkinter.CTkButton(master=self.frame_left,
                                                   height=15,
                                                   text="Weather",
                                                   border_width=3,   # <- custom border_width
                                                   fg_color=None,   # <- no fg_color
                                                   command=lambda: self.send_command('weather'))
        self.BTN_weather.grid(row=5, column=0, pady=10, padx=20)

        self.divider = customtkinter.CTkLabel(master=self.frame_left,
                                              text="---------",
                                              text_font=("Roboto Medium", -8))
        self.divider.grid(row=6, column=0, pady=2)

        self.BTN_stop = customtkinter.CTkButton(master=self.frame_left,
                                                height=15,
                                                text="PAUSE",
                                                border_width=3,   # <- custom border_width
                                                fg_color=None,   # <- no fg_color
                                                command=self.stop_sending_command)
        self.BTN_stop.grid(row=7, column=0, pady=10, padx=20, sticky="w")

        # ============ frame_left_bottom_connection ============================
        self.frame_connect = customtkinter.CTkFrame(master=self.frame_left)
        self.frame_connect.grid(row=8, column=0, columnspan=1,
                                rowspan=4, pady=5, padx=5, sticky="nsew")
        self.frame_connect.columnconfigure(0, weight=2)

        self.IP_entry = customtkinter.CTkEntry(master=self.frame_connect,
                                               width=40,
                                               fg_color="lightgray",
                                               text_color="black",
                                               textvariable="192.168.2.13",
                                               placeholder_text="IP")
        self.IP_entry.grid(row=1, column=0, pady=10, padx=10, sticky="we")

        self.PORT_entry = customtkinter.CTkEntry(master=self.frame_connect,
                                                 width=50,
                                                 fg_color="lightgray",
                                                 text_color="black",
                                                 placeholder_text="PORT")
        self.PORT_entry.grid(row=2, column=0, pady=10, padx=10, sticky="we")
        image_size = 40
        self.BTN_connected = customtkinter.CTkButton(master=self.frame_connect,
                                                     text="Connect", command=self.init_connect)
        self.BTN_connected.grid(row=3, column=0, pady=10, padx=10, sticky="ns")

        self.BTN_mode = customtkinter.CTkSwitch(master=self.frame_left,
                                                text="Dark Mode",
                                                command=self.change_mode)
        self.BTN_mode.grid(row=13, column=0, pady=20, padx=20, sticky="w")

        # ============ frame_right ============

        # configure grid layout (3x7)
        self.frame_right.rowconfigure(1, weight=2)
        self.frame_right.rowconfigure(2, weight=1)
        self.frame_right.columnconfigure(0, weight=3)

        # ============ frame_right_top ============
        self.frame_info = customtkinter.CTkFrame(master=self.frame_right)
        self.frame_info.grid(row=0, column=0, columnspan=3,
                             rowspan=1, pady=10, padx=10, sticky="nsew")
        self.CPU_text = customtkinter.CTkButton(master=self.frame_info, text="", width=50, height=50,
                                                corner_radius=10, fg_color="gray40", hover_color="gray25")

        self.CPU_text.grid(row=0, column=0, columnspan=1,
                           padx=20, pady=10, sticky="e")
        self.BATTERY_PER = customtkinter.CTkButton(master=self.frame_info, text="", width=50, height=50,
                                                   corner_radius=10, fg_color="gray40", hover_color="gray25", border_width=3, border_color="#D35B58")

        self.BATTERY_PER.grid(row=0, column=1, columnspan=1,
                              padx=20, pady=10, sticky="e")
        self.BATTERY_LEFT = customtkinter.CTkButton(master=self.frame_info, text="", width=50, height=50,
                                                    corner_radius=10, fg_color="gray40", hover_color="gray25")

        self.BATTERY_LEFT.grid(row=0, column=2, columnspan=1,
                               padx=20, pady=10, sticky="e")

        # ============ frame_right_middle ============
        self.frame_log = customtkinter.CTkFrame(master=self.frame_right)
        self.frame_log.grid(row=1, column=0, columnspan=3,
                            pady=10, padx=10, sticky="nsew")
        # configure grid layout (1x1)
        self.frame_log.rowconfigure((2), weight=1)
        self.frame_log.columnconfigure(0, weight=1)

        self.chatbox = customtkinter.CTkLabel(master=self.frame_log,
                                              text="İşlem bekleniyor", height=150,
                                              fg_color=(
                                                  "white", "gray38"),
                                              justify=tkinter.LEFT)
        self.chatbox.grid(row=0, column=0, columnspan=3,
                          sticky="nswe", padx=20, pady=20)

        self.progressbar = customtkinter.CTkProgressBar(master=self.frame_log)
        self.progressbar.grid(row=1, column=0, sticky="ew", padx=15, pady=15)
        self.message_entry = customtkinter.CTkEntry(
            master=self.frame_log, placeholder_text="Type and Press ENTER button")
        self.message_entry.grid(
            row=2, column=0, columnspan=3, pady=10, padx=10, sticky="we")

        # set default values
        self.IP_entry.insert(0, "192.168.2.13")
        self.PORT_entry.insert(0, "5005")
        self.message_entry.configure(state=tk.DISABLED)
        self.BTN_mode.select()
        self.progressbar.set(0)
        self.bind('<Return>', self.send_message)
        self.threads = []

    def send_message(self, event):
        text = event.widget.get()
        print("mesaj gelen: ", text)
        self.messageSent['command'] = text
        event.widget.delete(0, "end")
        # self.message_entry.update()

    def init_connect(self):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # start connection

        try:
            if not self.isConnected:
                self.clientSocket.connect((self.IP, self.PORT))
                self.clientSocket.settimeout(.1)
                print("bağlandı")
                self.post_connect(True)
                x = Thread(target=self.recieve_thread, daemon=True).start()
                self.threads.append(x)
            else:
                self.clientSocket.close
                self.clientSocket.settimeout(.5)
                self.post_connect(False)
        except ConnectionRefusedError:
            print("server kapalı "+self.IP+' - '+str(self.PORT))

    def post_connect(self, status):
        if status:
            self.chatbox.configure(text='Connected')
            self.BTN_connected.set_text("Disconnect")
            self.PORT_entry.configure(
                fg_color=("black", "gray38"), state=tk.DISABLED)
            self.IP_entry.configure(
                fg_color=("black", "gray38"), state=tk.DISABLED)
            self.message_entry.configure(state=tk.NORMAL)
            self.isConnected = True

        else:
            self.progressbar.set(0/10)
            self.message_entry.configure(state=tk.DISABLED)
            self.chatbox.configure(text='Disconnected')
            self.PORT_entry.configure(
                fg_color="lightgray", state=tk.NORMAL)
            self.IP_entry.configure(
                fg_color="lightgray", state=tk.NORMAL)
            self.isConnected = False
            self.clientSocket.close()
            self.BTN_connected.set_text("Connect")

    def recieve_thread(self):
        counter = 0
        while self.isConnected:
            if self.transmission:
                if counter > 9:
                    counter = 0
                data_string = json.dumps(self.messageSent).encode(
                    'utf-8')
                try:
                    self.clientSocket.send(data_string)
                    print("sent : ", data_string)
                    self.messageSent = {'ping': "0"}
                except:
                    print("cant send data")
                    self.isConnected = False
                try:
                    data = self.clientSocket.recv(1024)
                    if len(data) == 0:
                        self.isConnected = False
                except ValueError:
                    print("no data")
                    self.isConnected = False
                except BlockingIOError:
                    self.isConnected = False  # socket is open and reading from it would block
                except ConnectionResetError:
                    self.isConnected = False  # socket was closed for some other reason
                except Exception as e:
                    self.isConnected = False  # socket was closed for some unknown reason
                self.messageReceived = json.loads(data.decode('utf-8'))
                self.check_action(counter)
                counter += 1
                time.sleep(0.5)
        self.post_connect(False)

    def check_action(self, counter):
        self.progressbar.set(counter/10)
        self.CPU_text.set_text(self.messageReceived['CPU_TEMP'])
        self.BATTERY_PER.set_text(self.messageReceived['BATTERY_PERCENTAGE'])
        self.BATTERY_LEFT.set_text(self.messageReceived['BATTERY_LEFT'])

        def deactivate_button(btn):
            self.chat += str(self.activeAction)+" closed \n"
            buttonName = 'BTN_'+btn
            if hasattr(self, buttonName):
                button = getattr(self, buttonName)
                button.configure(fg_color=None)

        if 'current' in self.messageReceived:
            if self.activeAction != self.messageReceived['current']:
                print("received : ", self.activeAction, self.messageReceived)
                self.chat += str(self.messageReceived['current'])+" open \n"
                buttonName = 'BTN_'+self.messageReceived['current']
                if hasattr(self, buttonName):
                    button = getattr(self, buttonName)
                    button.configure(fg_color='green')
                if self.activeAction:
                    deactivate_button(self.activeAction)
                self.activeAction = self.messageReceived['current']
        else:
            if self.activeAction:
                deactivate_button(self.activeAction)
            self.activeAction = None
        self.chatbox.configure(text=self.chat)

    def send_command(self, command):
        self.transmission = True
        self.BTN_stop.configure(fg_color='red')
        self.messageSent.pop('ping', None)
        self.messageSent['command'] = command

    def stop_sending_command(self):
        colour = None if self.transmission else "red"
        self.BTN_stop.configure(fg_color=colour)
        self.transmission = not self.transmission

    def change_mode(self):
        if self.BTN_mode.get() == 1:
            customtkinter.set_appearance_mode("dark")
        else:
            customtkinter.set_appearance_mode("light")

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()
