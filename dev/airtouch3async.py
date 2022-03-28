import asyncio
import socket
from typing import List
from typing import Dict
import hashlib
from enum import Enum
from xmlrpc.client import Boolean

class AT3Const:

    # General constants
    ZONES_LEN = 16              # Zones count in response from Air Touch 3
    GROUPS_LEN = 16             # Groups count in response from Air Touch 3
    AC_UNIT_LEN = 2             # AC Units supported by Air Touch 3
    TEMP_SENSOR_LEN = 32        # Sensor count in response from Air Touch 3
    GRP_NAME_LEN = 8            # Characters in Group names
    SYS_NAME_LEN = 16           # Characters in System name
    AC_NAME_LEN = 8             # Characters in AC names
    SYS_ID_LEN = 8              # Characters in System ID
    RESPONSE_LEN = 492          # Response length in bytes from Air Touch 3

    # Data Offsets - from start of response
    DAOF_GRP_NAME = 104         # Zone name (8 characters)
    DAOF_ZONE_STATE = 232       # Damper (aka Zone in Air Touch)
    DAOF_GRP_PERCENT = 248      # Percent position for all zones in a group
    DAOF_GRP_FIRSTZONE = 264    # First Zone in a Group
    DAOF_GRP_SETPOINT = 296     # Setpoint in degC-1 (yes thats substract one)
    DAOF_GRP_COUNT = 352        # Number of groups enabled in system
    DAOF_GRP_TEST = 353         # TODO TEST BLOCK OF DATA
    DAOF_SYS_NAME = 383         # String name of system
    DAOF_AC1_NAME = 399         # String name of AC Unit 1
    #DAOF_AC2_NAME = 407        # Not needed, use offset to get AC1 details
    DAOF_AC1_STATUS = 423       # Status of AC 1, bit 8 on/off, bit 7 error
    #DAOF_AC2_STATUS = 424      # Not needed, use offset to get AC1 details
    #AOF_AC1_ID = 425           # Not needed, will always be 0
    #DAOF_AC2_ID = 426          # Not needed, will always be 1
    DAOF_AC1_MODE = 427         # Mode of AC Unit 1, heat/cool etc
    #DAOF_AC2_MODE = 428        # Not needed, use offset to get AC1 details
    DAOF_AC1_FAN = 429          # Fan speed of AC Unit 1, High/Low/Auto etc
    #DAOF_AC2_FAN = 430         # Not needed, use offset to get AC1 details
    DAOF_AC1_TEMP_SP = 431      # Temperature setpoint for AC Unit 1 in degC
    #DAOF_AC2_TEMP_SP = 432     # Not needed, use offset to get AC1 details
    DAOF_AC1_TEMP_PV = 433      # Temperature actual for AC Unit 1 in degC
    #DAOF_AC2_TEMP_PV = 434     # Not needed, use offset to get AC1 details
    DAOF_AC1_BRAND = 439        # Brand ID of AC Unit 1; 8=Daikin
    #DAOF_AC2_BRAND = 440       # Not needed, use offset to get AC1 details
    #DAOF_AC1_THERM_MODE = 441  # TODO Needs work process this mode
    #DAOF_AC2_THERM_MODE = 442  # TODO Needs work process this mode
    DAOF_TP_GRP_ID = 443        # Touch Panel 1 Temperature Group ID
    DAOF_TP_TEMP = 445          # Touch Panel 1 Temperature in degC
    DAOF_TEMP_SENSORS = 451     # First Temperature sensor
    DAOF_SYS_ID = 483           # System ID (8 numbers)

    # Air Touch 3 Commands
    CMD_0 = 85                  # Byte 0 of command always fixed
    CMD_1_STATUS = 1            # Status reqest in byte 1
    CMD_1_GRP_CTRL = 129        # All group commands have fixed byte 1
    CMD_1_AC_CTRL = 134         # All AC Unit commands have fixed byte 1
    CMD_2 = 12                  # Byte 2 of command always fixed
    CMD_4_TOGGLE = 128          # Toggle on/off in byte 4
    CMD_4_GRP_POSDEC = 1        # Position decrement (5% down) in byte 4
    CMD_4_GRP_POSINC = 2        # Position increment (5% up) in byte 4
    CMD_4_AC_TEMP_DEC = 147     # AC Temperature setpoint decrement in byte 4
    CMD_4_AC_TEMP_INC = 163     # AC Temperature setpoint increment in byte 4
    CMD_5_GRP_POS = 1           # In Position dec/inc command, byte 5 is fixed

class AT3Helper:

    def calculate_checksum(message):
        r = 0
        for c in message:
            r += c
        r = (r % 256)
        return bytes([r])

    def bit8_in_byte_on(bin_value):
        return (bin_value & 0b10000000) > 0

    def bit7_in_byte_on(bin_value):
        return (bin_value & 0b01000000) > 0

class AT3AcMode(Enum):
    AUTO = 0
    HEAT = 1
    DRY = 2
    FAN = 3
    COOL = 4

    def __str__(self):
        if self == AT3AcMode.AUTO:
            return "Auto"
        if self == AT3AcMode.HEAT:
            return "Heat"
        if self == AT3AcMode.DRY:
            return "Dry"
        if self == AT3AcMode.FAN:
            return "Fan"
        if self == AT3AcMode.COOL:
            return "Cool"
        return "Unknown"

class AT3AcFanSpeed(Enum):
    QUIET = 0
    LOW = 1
    MED = 2
    HIGH = 3
    POWER = 4
    AUTO = 5

    def __str__(self):
        if self == AT3AcFanSpeed.QUIET:
            return "Quiet"
        if self == AT3AcFanSpeed.LOW:
            return "Low"
        if self == AT3AcFanSpeed.MED:
            return "Medium"
        if self == AT3AcFanSpeed.HIGH:
            return "High"
        if self == AT3AcFanSpeed.POWER:
            return "Powerful"
        if self == AT3AcFanSpeed.AUTO:
            return "Auto"
        return "Unknown"

class AT3GroupMode(Enum):
    TEMPERATURE = 0
    PERECENT = 1
    INVALID = 2

    def __str__(self):
        if self == AT3GroupMode.TEMPERATURE:
            return "Temperature Control"
        if self == AT3GroupMode.PERECENT:
            return "Percent Open"
        if self == AT3GroupMode.INVALID:
            return "Invalid"
        return "Unknown"

class AT3CommsStatus(Enum):
    NOT_CONNECTED = 0
    OK = 1
    ERROR = 2

class AT3Command(Enum):
    INCREMENT = 0
    DECREMENT = 1

class AT3AcUnit:
    name = "Unknown"
    number = -1
    is_on = False
    has_error = False
    mode = AT3AcMode.AUTO
    fan_speed = AT3AcFanSpeed.AUTO
    brand = -1
    temperature = -1
    temperature_sp = -1
    _at3class_toggle_func = None
    _at3class_toggle_sp_func = None

    def __init__(self, name, number, toggle_func, toggle_sp_func):
        self.name = name
        self.number = number
        self._at3class_toggle_func = toggle_func
        self._at3class_toggle_sp_func = toggle_sp_func

    def toggle(self) -> bool: 
        return self._at3class_toggle_func(self.number)
    def temperature_inc(self) -> bool: 
        return self._at3class_toggle_sp_func(self.number, AT3Command.INCREMENT)
    def temperature_dec(self) -> bool: 
        return self._at3class_toggle_sp_func(self.number, AT3Command.DECREMENT)

class AT3Group:
    name = "Unknown"
    number = -1
    is_on = False
    mode = AT3GroupMode.INVALID
    open_percent = -1
    temperature = -1
    temperature_sp = -1
    _at3class_toggle_func = None
    _at3class_toggle_pos_func = None

    def __init__(self, name, number, toggle_func, toggle_pos_func):
        self.name = name
        self.number = number
        self._at3class_toggle_func = toggle_func
        self._at3class_toggle_pos_func = toggle_pos_func
    
    def toggle(self) -> bool: 
        return self._at3class_toggle_func(self.number)
    def position_inc(self) -> int: 
        return self._at3class_toggle_pos_func(self.number, AT3Command.INCREMENT)
    def position_dec(self) -> int: 
        return self._at3class_toggle_pos_func(self.number, AT3Command.DECREMENT)

class AT3TempSensor:
    name = "Unknown"
    temperature = -1
    available = False
    low_battery = False
    def __init__(self, name):
        self.name = name

class AirTouch3ASync:

    # Hardcoded as should never change
    _TCP_PORT = 8899

    _tcp_ip = ""
    _socket = None
    name = ""
    id = ""
    comms_status = AT3CommsStatus.ERROR
    comms_error = "Uninitialised"
    recv_task = None
    groups: Dict[int, AT3Group] = dict()
    ac_units: Dict[int, AT3AcUnit] = dict()
    sensors: Dict[str, AT3TempSensor] = dict()
    _update_callbacks = []

    def __init__(self, tcp_ip) -> None:
        self._tcp_ip = tcp_ip
        self.comms_status = AT3CommsStatus.NOT_CONNECTED
        self.comms_error = "Connection yet to be Attempted"
        self.recv_task = self._socket_connect()

    def update_status(self):

        # Send a command to the Air Touch 3
        # Byte1 = 1 means request status only
        self._send(AT3Const.CMD_1_STATUS, 0, 0, 0)

    def register_update_callback(self, func):
        self._update_callbacks.append(func)

    def unregister_update_callback(self, func):
        self._update_callbacks.remove(func)

    def toggle_ac_unit(self, acUnit):

        # Send command to the Air Touch 3 if valid ac unit number
        if acUnit >= 0 and acUnit < len(self.ac_units):
            self._send(AT3Const.CMD_1_AC_CTRL, acUnit,
                                        AT3Const.CMD_4_TOGGLE, 0)

    def toggle_temperature_ac_unit(self, acUnit, direction:AT3Command):

        # Send command to the Air Touch 3 if valid ac unit number
        if acUnit >= 0 and acUnit < len(self.ac_units):

            cmd = AT3Const.CMD_4_AC_TEMP_DEC
            if direction == AT3Command.INCREMENT: 
                cmd = AT3Const.CMD_4_AC_TEMP_INC
            self._send(AT3Const.CMD_1_AC_CTRL, acUnit, cmd, 0)

    def toggle_group(self, group):

        # Send command to the Air Touch 3 if valid group number
        if group >= 0 and group < len(self.groups):
            self._send(AT3Const.CMD_1_GRP_CTRL, group, 
                                        AT3Const.CMD_4_TOGGLE, 0)

    def toggle_position_group(self, group, direction:AT3Command):
           
        # Send command to the Air Touch 3 if valid group number
        if group >= 0 and group < len(self.groups):

            cmd = AT3Const.CMD_4_GRP_POSDEC 
            if direction == AT3Command.INCREMENT:
                cmd = AT3Const.CMD_4_GRP_POSINC
                
            self._send_recieve(AT3Const.CMD_1_GRP_CTRL, group, cmd, 
                                        AT3Const.CMD_5_GRP_POS)

    def print_status(self) -> None:
        print(f"System Name: {self.name}")
        print(f"System ID: {self.id}")
        for g in self.groups.values():
            print(f"Group[{g.number}]: {g.name}; On: {g.is_on}; "
                  f"Mode is {g.mode}; Percent: {g.open_percent}%; "
                  f"Temp: {g.temperature}degC; "
                  f"Target: {g.temperature_sp}degC")
        for ac in self.ac_units.values():
            print(f"AC Unit[{ac.number}]: {ac.name}; On: {ac.is_on}; "
                  f"Error: {ac.has_error}; Mode: {ac.mode}; "
                  f"Brand ID: {ac.brand}; Fan: {ac.fan_speed}; "
                  f"Temp: {ac.temperature}degC; "
                  f"Target: {ac.temperature_sp}degC")
        for s in self.sensors.values():
            print(f"Sensor[{s.name}]: {s.temperature}degC; "
                  f"Low Battery: {s.low_battery}")

    def _update_or_add_sensor(self, name, byte_value):

        temperature = byte_value & 0b0011_1111               # Bits 0 to 6
        available = AT3Helper.bit8_in_byte_on(byte_value)    # Bit 8
        low_battery = AT3Helper.bit7_in_byte_on(byte_value)  # Bit 7

        # Nothing to do if not available
        if not available:
            return None

        # Make sure there is an entry in the dict for the sensor
        if not self.sensors.get(name):
            self.sensors[name] = AT3TempSensor(name)

        # We will always have a sensor at the given name index at this point
        sensor = self.sensors.get(name)
        sensor.temperature = temperature
        sensor.available = available
        sensor.low_battery = low_battery
        return sensor

    def _socket_connect(self):
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #self._socket.settimeout(5.0)
            self._socket.connect((self._tcp_ip, self._TCP_PORT))
            self.comms_status = AT3CommsStatus.OK
            self.comms_error = ""
            return asyncio.create_task(self._wait_for_data())
        except OSError as e:
            self.comms_status = AT3CommsStatus.NOT_CONNECTED
            self.comms_error = format(e)
            return None

    async def _wait_for_data(self):

        # Never get for than 492 bytes(ref AT3Const.RESPONSE_LEN)
        BUFFER_SIZE = 492

        while True:
            response = self._socket.recv(BUFFER_SIZE)
            self._process_response(response)

            # Notify all callbacks or new status
            for func in self._update_callbacks:
                func()
        
    def _process_reponse(self, response):
        
        # also make sure we recieved a response of length 492 bytes
        if not response or len(response) != AT3Const.RESPONSE_LEN:
            self.comms_status = AT3CommsStatus.ERROR
            self.comms_status = "Invalid Response Received"
            print("ERROR! "+str(len(response))+" "+self.comms_status)
            return False

        # Loop through the maximum number of zones
        # these are the dampers themselves, which are "grouped" 
        # into what is usually known as zones
        zones = []
        for z in range(AT3Const.ZONES_LEN):
            # MSB is zone on/off (x) and LS three bits are zone 
            # number 0-7 (y) x000_0yyy. Note the zone number for 
            # zones 1-8 is 0-7 and repeats for zones 9-16, ie 0-7
            byte_value = response[AT3Const.DAOF_ZONE_STATE+z]
            zones.append(AT3Helper.bit8_in_byte_on(byte_value))

        # Loop through all the groups, only load the number 
        # configured in the system
        num_groups = int(response[AT3Const.DAOF_GRP_COUNT])
        for z in range(min(AT3Const.GROUPS_LEN, num_groups)):

            # Group names are all fixed character length
            stt = AT3Const.DAOF_GRP_NAME + (z * AT3Const.GRP_NAME_LEN)
            end = stt + AT3Const.GRP_NAME_LEN
            name = response[stt:end].decode().strip().strip('\x00')

            # Groups are stored using their number as the index
            # Try and get the group via its number, if non found, add it
            if not self.groups.get(z):
                self.groups[z] = AT3Group(name, z, self.toggle_group, 
                                            self.toggle_position_group)

            # Get the group from he dict and set the name
            group = self.groups.get(z)
            group.name = name

            # Get the first zone in the group and base the status 
            # of the group on that zone. All zones in a group will have
            # the same status, so only need to read the first
            byte_value = response[AT3Const.DAOF_GRP_FIRSTZONE+z]
            first_zone = int((byte_value & 0b1111_0000) >> 4)
            group.is_on = zones[first_zone]    

            # Mode of zone is 7th bit, if on then temp control, 
            # else percent position
            byte_value = response[AT3Const.DAOF_GRP_PERCENT+z]
            group.mode = AT3GroupMode.PERECENT
            if AT3Helper.bit8_in_byte_on(byte_value):
                group.mode = AT3GroupMode.TEMPERATURE

            # Temperature setpoint is bottom 5 bits 
            # (less one from setpoint, kinda wierd?!)
            byte_value = response[AT3Const.DAOF_GRP_SETPOINT+z]
            group.temperature_sp = int(byte_value & 0b0001_1111) + 1

            # Group percent is bottom 7 bits and 1 count per 5%
            byte_value = response[AT3Const.DAOF_GRP_PERCENT+z]
            percent = 5*int(byte_value & 0b0111_1111)
            group.open_percent = percent if group.is_on else 0

        # Update AC Units from the response
        # TODO At the moment, get data for two air cons, need to work  out 
        # how many air cons are being used and what groups are allocated 
        # to each air con
        for a in range(AT3Const.AC_UNIT_LEN):

            # Names are straight after each other in the config file
            stt = AT3Const.DAOF_AC1_NAME + AT3Const.AC_NAME_LEN*a
            end = stt + AT3Const.AC_NAME_LEN
            name = response[stt:end].decode().strip().strip('\x00')

            # AC Units are stored using their number as the index
            # Try and get the group via its number, if non found, add it
            if not self.ac_units.get(a):
                self.ac_units[a] = AT3AcUnit(name, a, self.toggle_ac_unit, 
                                                self.toggle_temperature_ac_unit)

            # Get the ac unit and set the name
            acUnit = self.ac_units.get(a)
            acUnit.name = name
            
            # Status contains on/off and error bits
            status = response[AT3Const.DAOF_AC1_STATUS+a]
            acUnit.is_on = AT3Helper.bit8_in_byte_on(status)
            acUnit.has_error = AT3Helper.bit7_in_byte_on(status)

            # Get the brand id, we need this to issue commands to the AcUnit, 
            # otherwise, who cares right?
            acUnit.brand = int(response[AT3Const.DAOF_AC1_BRAND+a])

            # Mode at in heat/cool etc
            acUnit.mode = AT3AcMode(int(response[AT3Const.DAOF_AC1_MODE+a]))
            
            # Fan Speed is only bottom 4 bits
            byte_value = response[AT3Const.DAOF_AC1_FAN+a]
            acUnit.fan_speed = AT3AcFanSpeed(int(byte_value & 0b0000_1111))

            # Get the temp control mode, but dont do anything with it
            # TODO Not used at the moment, dont know how air touch 3 
            # re-assigns the temperature feedback based on this mode
            #data[DAOF_AC1_THERM_MODE+a]
            
            # This is the temperature from the AC unit itself, depending 
            # on setup, a zone temp might be being used as the AC temp 
            # feedback TODO, need to reassign the temperature based on the 
            # therm mode above
            acUnit.temperature = int(response[AT3Const.DAOF_AC1_TEMP_PV+a])

            # Temperature setpoint; ignore top two bits as usual, for 
            # temp values
            byte_value = response[AT3Const.DAOF_AC1_TEMP_SP+a]
            acUnit.temperature_sp = int(byte_value & 0b0011_1111)

        # Touch pad information, add to sensor list
        # The Group the touch pad temperature is assigned to
        group_id = int(response[AT3Const.DAOF_TP_GRP_ID])
        name = "Touch Pad 1"

        # Save sensor into the sensor list, returns the sensor object
        byte_value = response[AT3Const.DAOF_TP_TEMP]
        sensor = self._update_or_add_sensor(name, byte_value)

        # If valid group and sensor available (should always be available 
        # because its a TP), set temperature of group
        # assign the temperature to the appropriate group
        if group_id > 0 and group_id <= num_groups and sensor:
            self.groups[group_id - 1].temperature = sensor.temperature  

        # Get the sensors in the system
        for s in range(AT3Const.TEMP_SENSOR_LEN):
            byte_value = response[AT3Const.DAOF_TEMP_SENSORS+s]
            self._update_or_add_sensor(f"Sensor {s+1}", byte_value)

        # Load the system name and id
        stt = AT3Const.DAOF_SYS_NAME
        end = stt + AT3Const.SYS_NAME_LEN
        self.name = response[stt:end].decode().strip().strip('\x00')
        stt = AT3Const.DAOF_SYS_ID
        end = stt + AT3Const.SYS_ID_LEN
        self.id = response[stt:end].decode().strip().strip('\x00')

    def _send(self, byte1, byte3, byte4, byte5):

        if not self.comms_status == AT3CommsStatus.OK:
            return

        # Command is 12 bytes, add checksum as 13th
        rList = [AT3Const.CMD_0, byte1, AT3Const.CMD_2, 
                    byte3, byte4, byte5, 0, 0, 0, 0, 0, 0]
        rChk = AT3Helper.calculate_checksum(rList)
        rList.extend(rChk)
        arr = bytes(rList)

        self._socket.send(arr)

def print_ac_on_off():
    print("Data has changed!")

async def main():
    await asyncio.sleep(100)
    at3 = AirTouch3ASync('192.168.1.72')
    print("Registering callbacks")
    at3.register_update_callback(at3.print_status)
    at3.register_update_callback(print_ac_on_off)
    print("Updating Status")
    at3.update_status()

    #if at3.recv_task:
    #    await at3.recv_task

asyncio.run(main())