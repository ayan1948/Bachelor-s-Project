import visa
import sys
import time
import RPi.GPIO as GPIO
import json
import numpy as np
import os

GLOBAL_TOUT = 1000
GPIO_TIMEOUT = 2
errorCode = -1
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)


class Scope:
    def __init__(self):
        rm = visa.ResourceManager()

        # Looking for the Device in a list
        for devices in rm.list_resources():
            if "USB" in devices:
                SCOPE_VISA_ADDRESS = devices
                break
        if SCOPE_VISA_ADDRESS is None:
            print(f"Unable to find oscilloscope device with USB prefix on the list: {rm.list_resources()}")
            sys.exit()

        try:
            self.KsInfiniiVisionX = rm.open_resource(SCOPE_VISA_ADDRESS)
            print("Connection established with " + str(self.KsInfiniiVisionX.query("*IDN?")))
        except Exception:
            print(f"Unable to connect to oscilloscope at " + str(SCOPE_VISA_ADDRESS) + ". Aborting script.")
            sys.exit()

    def error_check(self):
        while errorCode != 0:
            self.KsInfiniiVisionX.write('SYST:ERR?')
            rawError = self.KsInfiniiVisionX.read()

            errorParts = rawError.split(',')
            errorCode = int(errorParts[0])
            errorMessage = errorParts[1].rstrip('\n')

            print('INSTRUMENT ERROR - Error code: %d, error message: %s' % (errorCode, errorMessage))

    def save_setup(self):
        Setup = self.KsInfiniiVisionX.query_binary_values(":SYStem:SETup?", datatype="B", is_big_endian=False)
        with open("settings.json", 'w') as f:
            json.dump(Setup, f)

    def recall_setup(self):
        with open("settings.json", 'r') as f:
            recalled_Setup = json.load(f)
        self.KsInfiniiVisionX.write_binary_values(":SYStem:SETup ", recalled_Setup, datatype="B", is_big_endian=False)

    def close(self, do_exit=True):
        print('Exiting the process...')
        self.KsInfiniiVisionX.clear()
        self.KsInfiniiVisionX.close()
        GPIO.cleanup()
        if do_exit:
            sys.exit()


class ScopeManager(Scope):
    def __init__(self, channels=0, title=""):
        super().__init__()
        self.channels = channels
        self.title = title

    def set_channel(self, channels):
        self.channels = channels

    def set_title(self, title):
        self.title = title

    def initialize(self):
        print("Initializing oscilloscope...")
        self.KsInfiniiVisionX.timeout = GLOBAL_TOUT
        self.KsInfiniiVisionX.query(":STOP;*CLS;*OPC?")
        self.KsInfiniiVisionX.write(":WAVeform:FORMat WORD")
        self.KsInfiniiVisionX.write(":WAVeform:BYTeorder LSBFirst")
        self.KsInfiniiVisionX.write(":WAVeform:UNSigned 0")
        for channel in range(4):
            if self.channels[channel] == 1:
                self.KsInfiniiVisionX.write(":CHANnel" + str(channel + 1) + ":DISPlay ON")
                self.KsInfiniiVisionX.write(":WAVeform:SOURce" + str(channel + 1))
        self.KsInfiniiVisionX.write(":WAVeform:POINts NORMal")
        self.KsInfiniiVisionX.chunk_size = 20480

        # Acquiring the Offset Values for all Channel
        self.Y_INCrement = []
        self.Y_ORIGin = []
        self.Y_REFerence = []
        for channel in range(4):
            if self.channels[channel] == 1:
                Pre = self.KsInfiniiVisionX.query(
                    ":WAVeform:SOURce CHANnel" + str(channel + 1) + ";:WAVeform:PREamble?").split(',')
                self.Y_INCrement.append(float(Pre[7]))
                self.Y_ORIGin.append(float(Pre[8]))
                self.Y_REFerence.append(float(Pre[9]))
            else:
                self.Y_INCrement.append(None)
                self.Y_ORIGin.append(None)
                self.Y_REFerence.append(None)
        X_INCrement = float(Pre[4])
        X_ORIGin = float(Pre[5])
        X_REFerence = float(Pre[6])

        # Calibrating the x-axis
        MAX_CURRENTLY_AVAILABLE_POINTS = int(self.KsInfiniiVisionX.query(":WAVeform:POINts?"))
        self.DataTime = ((np.linspace(0, MAX_CURRENTLY_AVAILABLE_POINTS - 1,
                                      MAX_CURRENTLY_AVAILABLE_POINTS) - X_REFerence) * X_INCrement) + X_ORIGin
        if float(Pre[1]) == "PEAK":
            self.DataTime = np.repeat(self.DataTime, 2)

        os.mkdir(f'../results/{self.title}')

    def reinitialize(self):
        print("Reinitializing the Scope for Capture")
        self.KsInfiniiVisionX.clear()
        self.KsInfiniiVisionX.write(":SINGle")

    def acquire(self):
        try:
            GPIO.output(11, 1)
            print('Waiting...', end='')
            start = time.time()
            flag = 0

            # Running the loop for 2 seconds
            while (time.time() - start) < GPIO_TIMEOUT:
                try:
                    self.KsInfiniiVisionX.query_ascii_values('*OPC?')
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
            Data_all = []
            for channel in range(4):
                if self.channels[channel] == 1:
                    Data_all.append(np.array(
                        self.KsInfiniiVisionX.query_binary_values(
                            ':WAVeform:SOURce CHANnel' + str(channel + 1) + ';DATA?', datatype="h",
                            is_big_endian=False)).round(decimals=3))
                    Data_all[channel] = ((Data_all[channel] - self.Y_REFerence[channel]) * self.Y_INCrement[channel]) + \
                                        self.Y_ORIGin[channel]
                else:
                    Data_all.append(None)

            filename = os.path.join(f'../results/{self.title}', f"{self.title}_{time.strftime('%Y%m%d')}.csv")

            data = np.array((self.DataTime, Data_all[0], Data_all[1], Data_all[2], Data_all[3]))
            np.savetxt(filename, data.T, delimiter=',')
            print('Plot Acquired. Sleeping for 2s!')
            time.sleep(2)
        finally:
            # just as a fallback makes sure the switch is off when any error occurs
            GPIO.output(11, 0)
