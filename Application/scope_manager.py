import visa
import sys
import RPi.GPIO as GPIO
import json
import numpy as np
from pathlib import Path
import time

GLOBAL_TOUT = 1000
GPIO_TIMEOUT = 2
error_code = -1
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)

FILE = Path(__file__).parent

class Scope:
    def __init__(self):
        rm = visa.ResourceManager()

        # Looking for the Device in a list
        for devices in rm.list_resources():
            if "USB" in devices:
                scope_visa_address = devices
                break
        if scope_visa_address is None:
            print(f"Unable to find oscilloscope device with USB prefix on the list: {rm.list_resources()}")
            sys.exit()

        try:
            self.ks_infinii_vision_x = rm.open_resource(scope_visa_address)
            print(f"Connection established with {self.ks_infinii_vision_x.query('*IDN?')}")
        except Exception:
            print(f"Unable to connect to oscilloscope at {scope_visa_address}. Aborting script.")
            sys.exit()

    def error_check(self):
        while error_code != 0:
            self.ks_infinii_vision_x.write('SYST:ERR?')
            raw_error = self.ks_infinii_vision_x.read()

            error_parts = raw_error.split(',')
            error_code = int(error_parts[0])
            error_message = error_parts[1].rstrip('\n')

            print(f'INSTRUMENT ERROR - Error code: {error_code}, error message: {error_message}')

    def save_setup(self):
        setup_data = self.ks_infinii_vision_x.query_binary_values(":SYStem:SETup?", datatype="B", is_big_endian=False)
        with open("settings.json", 'w') as f:
            json.dump(setup_data, f)

    def recall_setup(self):
        with open("settings.json", 'r') as f:
            recalled_setup = json.load(f)
        self.ks_infinii_vision_x.write_binary_values(":SYStem:SETup ", recalled_setup, datatype="B", is_big_endian=False)

    def close(self, do_exit=True):
        print('Exiting the process...')
        self.ks_infinii_vision_x.clear()
        self.ks_infinii_vision_x.close()
        GPIO.cleanup()
        if do_exit:
            sys.exit()


class ScopeManager(Scope):
    def __init__(self, channels: tuple[int, ...]=(), title=""):
        super().__init__()
        self.channels = channels
        self.title = title

    def set_channel(self, channels):
        self.channels = channels

    def set_title(self, title):
        self.title = title

    def initialize(self):
        print("Initializing oscilloscope...")
        self.ks_infinii_vision_x.timeout = GLOBAL_TOUT
        self.ks_infinii_vision_x.query(":STOP;*CLS;*OPC?")
        self.ks_infinii_vision_x.write(":WAVeform:FORMat WORD")
        self.ks_infinii_vision_x.write(":WAVeform:BYTeorder LSBFirst")
        self.ks_infinii_vision_x.write(":WAVeform:UNSigned 0")
        for channel in range(4):
            if self.channels[channel] == 1:
                self.ks_infinii_vision_x.write(f":CHANnel{channel + 1}:DISPlay ON")
                self.ks_infinii_vision_x.write(f":WAVeform:SOURce{channel + 1}")
        self.ks_infinii_vision_x.write(":WAVeform:POINts NORMal")
        self.ks_infinii_vision_x.chunk_size = 20480

        # Acquiring the Offset Values for all Channel
        self.y_increment = []
        self.y_origin = []
        self.y_reference = []
        for channel in range(4):
            if self.channels[channel] == 1:
                preamble = self.ks_infinii_vision_x.query(
                    f":WAVeform:SOURce CHANnel{channel + 1};:WAVeform:PREamble?").split(',')
                self.y_increment.append(float(preamble[7]))
                self.y_origin.append(float(preamble[8]))
                self.y_reference.append(float(preamble[9]))
            else:
                self.y_increment.append(None)
                self.y_origin.append(None)
                self.y_reference.append(None)
        x_increment = float(preamble[4])
        x_origin = float(preamble[5])
        x_reference = float(preamble[6])

        # Calibrating the x-axis
        max_points = int(self.ks_infinii_vision_x.query(":WAVeform:POINts?"))
        self.data_time = ((np.linspace(0, max_points - 1,
                                      max_points) - x_reference) * x_increment) + x_origin
        if float(preamble[1]) == "PEAK":
            self.data_time = np.repeat(self.data_time, 2)

        (FILE / "results" / self.title).mkdir(parents=True, exist_ok=True)

    def reinitialize(self):
        print("Reinitializing the Scope for Capture")
        self.ks_infinii_vision_x.clear()
        self.ks_infinii_vision_x.write(":SINGle")

    def acquire(self):
        try:
            GPIO.output(11, 1)
            print('Waiting...', end='')
            start = time.time()
            flag = 0

            # Running the loop for 2 seconds
            while (time.time() - start) < GPIO_TIMEOUT:
                try:
                    self.ks_infinii_vision_x.query_ascii_values('*OPC?')
                    GPIO.output(11, 0)
                    flag = 1
                    print('')
                    break
                except:
                    print('.', end='')

            # Checking the flag variable
            if flag == 0:
                GPIO.output(11, 0)
                print(
                    f"Aborting... could not record traces for more than {GPIO_TIMEOUT / 1000.0}s an error has occurred")
                sys.exit(1)

            time.sleep(0.5)

            # Data Acquisition for Channel 1
            data_all = []
            for channel in range(4):
                if self.channels[channel] == 1:
                    data_all.append(np.array(
                        self.ks_infinii_vision_x.query_binary_values(
                            f':WAVeform:SOURce CHANnel{channel + 1};DATA?', datatype="h",
                            is_big_endian=False)).round(decimals=3))
                    data_all[channel] = ((data_all[channel] - self.y_reference[channel]) * self.y_increment[channel]) + \
                                        self.y_origin[channel]
                else:
                    data_all.append(None)

            filename = FILE / "results" / self.title / f"{self.title}_{time.strftime('%Y%m%d')}.csv"

            data = np.array((self.data_time, data_all[0], data_all[1], data_all[2], data_all[3]))
            np.savetxt(filename, data.T, delimiter=',')
            print('Plot Acquired. Sleeping for 2s!')
            time.sleep(2)
        finally:
            # just as a fallback makes sure the switch is off when any error occurs
            GPIO.output(11, 0)
