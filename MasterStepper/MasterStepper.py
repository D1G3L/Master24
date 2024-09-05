import serial
import time
import tkinter as tk
from tkinter import font
import pandas as pd

# To ensure the code runs smoothly, please install all the required packages using the following command:
# pip install pandas openpyxl pyserial
#
# Additionally, this code was executed in an Anaconda environment with Python version 3.9.7

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Stepper Control")
        self.geometry("1600x1200") 
        self.configure(bg="white")
        
        self.title_font = font.Font(size=36, weight='bold')
        self.custom_font = font.Font(size=16, weight='bold')

        # initialize connection to arduino
        self.ser = self.initialize_serial_connection('COM10')

        self.guessed_direction = None
        self.confidence = None
        self.startTime = None
        self.endTime = None

        self.create_widgets()
        self.bind_keys()

    # function handles serial connection initialization
    def initialize_serial_connection(self, port, baudrate=9600, timeout=2):
        try:
            ser = serial.Serial(port, baudrate, timeout=timeout)
            time.sleep(2)
            return ser
        except serial.SerialException as e:
            print(f"Error opening serial connection: {e}")
            return None

    # function sends commands to arduino
    def send_command(self, command):
        if self.ser is not None and self.ser.is_open:
            self.ser.write((command + '\n').encode())
            time.sleep(1)
        else:
            print("Serial connection is not open.")

    # function creates screen visuals
    def create_widgets(self):
        self.first_screen = tk.Frame(self, bg="white")
        self.second_screen = tk.Frame(self, bg="white")
        
        # first screen
        self.left_right_label = tk.Label(self.first_screen, text="Left/\nLinks", font=self.title_font, bg="white")
        self.left_right_label.pack(side="left", expand=True, fill="both")
        
        self.right_label = tk.Label(self.first_screen, text="Right/\nRechts", font=self.title_font, bg="white")
        self.right_label.pack(side="right", expand=True, fill="both")
        
        # second screen
        self.sure_label = tk.Label(self.second_screen, text="How Sure are you?\nWie sicher sind sie?", font=self.title_font, bg="white")
        self.sure_label.pack(side="top", expand=True, fill="both")
        
        self.sure_options = tk.Frame(self.second_screen, bg="white")
        self.sure_options.pack(expand=True, fill="both")
        
        # numbers and labels
        labels = [
            "Not at all confident\n \n(Überhaupt nicht sicher)", 
            "Very unconfident\n \n(Sehr unsicher)", 
            "Unconfident\n \n(Unsicher)", 
            "Neither confident nor unconfident\n \n(Weder unsicher noch sicher)", 
            "Somewhat confident\n \n(Etwas sicher)", 
            "Confident\n \n(Sicher)", 
            "Very confident\n \n(Sehr sicher)"
        ]
        
        for i in range(7):
            option = tk.Label(self.sure_options, text=str(i+1), font=self.custom_font, bg="white")
            option.grid(row=0, column=i, padx=20, pady=10, sticky="nsew")
            
            label = tk.Label(self.sure_options, text=labels[i], font=self.custom_font, bg="white")
            label.grid(row=1, column=i, padx=20, pady=10, sticky="nsew")

        for i in range(7):
            self.sure_options.columnconfigure(i, weight=1)

        self.show_first_screen()

    # function to bind keys
    def bind_keys(self):
        self.bind('f', lambda e: self.handle_screen_change('f'))
        self.bind('j', lambda e: self.handle_screen_change('j'))

        for i in range(1, 8):
            self.bind(str(i), lambda e, num=i: self.handle_number(num))
        
        key_map = {
            'q': 'q', # rotation clockwise 
            'w': 'w', # rotation counterclockwise
            'a': 'a', # step clockwise
            's': 's', # step counterclockwise
            'y': 'y', # swing clockwise
            'x': 'x', # swing counterclockwise
            'b': 'b'  # stop motor
        }
        for key, value in key_map.items():
            self.bind(key, lambda e, value=value: self.handle_time_and_send(value))

    # function handles screen change
    def handle_screen_change(self, key):
        self.guessed_direction = key
        self.endTime = time.time()
        self.send_command('b')
        self.show_second_screen()

    # function handles inputs for confidence score
    def handle_number(self, number):
        self.confidence = number
        self.save_to_excel()
        self.show_first_screen()
    
    # function handles inputs for movements
    def handle_time_and_send(self, key):
        if key in ['q', 'w', 'a', 's', 'y', 'x']:
            self.startTime = time.time()
        # if user presses 'f' or 'j', stop movement by sending 'b' command to arduino
        if key in ['f', 'j']:
            self.send_command('b') 
        self.send_command(key)
        
    # function to save inputs to excel file
    def save_to_excel(self):
        data = {
            'guessed_direction': [self.guessed_direction],
            'confidence': [self.confidence],
            'startTime': [self.startTime],
            'endTime': [self.endTime]
        }
        df = pd.DataFrame(data)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f'output_{timestamp}.xlsx'

        # write ecxel file
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
        except Exception as e:
            print(f"Error writing to Excel file: {e}")
    
    # function shows first screen
    def show_first_screen(self):
        self.second_screen.pack_forget()
        self.first_screen.pack(expand=True, fill="both")

    # function shows second screen
    def show_second_screen(self):
        self.first_screen.pack_forget()
        self.second_screen.pack(expand=True, fill="both")

if __name__ == "__main__":
    app = Application()
    app.mainloop()
