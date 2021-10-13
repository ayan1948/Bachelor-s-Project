# Keysight_control_thesis

### Overview
This thesis is about automating the process of High Voltage Discharges over spark gaps and retrieving the data which
is later handle by a webservice client running the control dashboard, all done on a Raspberry Pi 4 running Ubuntu 18.04.

### Equipments
 - Keysight Oscilloscope
 - Raspberry Pi
 - Relay Actuator 5V and 7KV

### Software Design
 - **Web Service:** 
   - _Framework:_ Flask, Socket_IO
   - _Server:_ eventlet
   - _Database_: SQLite (SQL Alchemy)
 - **Oscilloscope Communication Service:**
   - _Library:_ VISA (pyvisa) & pyUSB

> **NOTE: Keysight officially support only certain linux distributions:**
> - 64-Bit Red Hat Enterprise Linux Desktop Workstation 7.1 to 7.6
> - 64-Bit CentOS Desktop Workstation 7.1 to 7.6
> - 64-Bit Ubuntu Desktop 16.04.x and 18.04.x

### Starting the Application
Install all the libraries from the /Application/requirements.txt with `pip install requirements.txt` and then run `python app.py` to run Flask.
