# Keysight_control_thesis

### Overview
This thesis is about automating the process of High Voltage Discharges over spark gaps and retrieving the data which
is later handle by a webservice client running the control dashboard, all done on a Raspberry Pi 4 running Ubuntu 18.04.

### Equipments
 - Keysight Oscilloscope
 - Raspberry Pi
 - 70Kv relay actuator

### Software Design
 Since Raspberry Pi supports python natively and python being a very flexible open source language, also due to its huge
 user base which could help query out issues later in the future.
 - **Web Service:** 
   - _Framework:_ Flask, Socket_IO
   - _Server:_ eventlet
   - _Database_: SQLite
 - **Oscilloscope Communication Service:**
   - _Library:_ VISA(pyvisa)

> **NOTE: Keysight officially support only certain linux distributions:**
> - 64-Bit Red Hat Enterprise Linux Desktop Workstation 7.1 to 7.6
> - 64-Bit CentOS Desktop Workstation 7.1 to 7.6
> - 64-Bit Ubuntu Desktop 16.04.x and 18.04.x

