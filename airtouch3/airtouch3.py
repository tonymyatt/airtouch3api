import socket
from typing import List
from typing import Dict
import hashlib
from enum import Enum
from xmlrpc.client import Boolean

from airtouch3.constants import AT3Const
from airtouch3.helper import AT3Helper

class AT3AcMode(Enum):
    AUTO = 0
    HEAT = 1
    DRY = 2
    FAN = 3
    COOL = 4

    def __str__(self):
        match self.value:
            case AT3AcMode.AUTO.value:  return "Auto"
            case AT3AcMode.HEAT.value:  return "Heat"
            case AT3AcMode.DRY.value:   return "Dry"
            case AT3AcMode.FAN.value:   return "Fan"
            case AT3AcMode.COOL.value:  return "Cool"
            case _:                     return "Unknown"

class AT3AcFanSpeed(Enum):
    QUIET = 0
    LOW = 1
    MED = 2
    HIGH = 3
    POWER = 4
    AUTO = 5

    def __str__(self):
        match self.value:
            case AT3AcFanSpeed.QUIET.value: return "Quiet"
            case AT3AcFanSpeed.LOW.value:   return "Low"
            case AT3AcFanSpeed.MED.value:   return "Medium"
            case AT3AcFanSpeed.HIGH.value:  return "High"
            case AT3AcFanSpeed.POWER.value: return "Powerful"
            case AT3AcFanSpeed.AUTO.value:  return "Auto"
            case _:                         return "Unknown"

class AT3GroupMode(Enum):
    TEMPERATURE = 0
    PERECENT = 1
    INVALID = 2

    def __str__(self):
        match self.value:
            case AT3GroupMode.TEMPERATURE.value: return "Temperature Control"
            case AT3GroupMode.PERECENT.value:    return "Percent Open"
            case AT3GroupMode.INVALID.value:     return "Invalid"
            case _:                              return "Unknown"

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
    _at3classToggleFunc = None
    _at3classToggleSpFunc = None

    def __init__(self, name, number, toggleFunc, toggleSpFunc):
        self.name = name
        self.number = number
        self._at3classToggleFunc = toggleFunc
        self._at3classToggleSpFunc = toggleSpFunc

    def Toggle(self) -> bool: 
        return self._at3classToggleFunc(self.number)
    def TemperatureInc(self) -> bool: 
        return self._at3classToggleSpFunc(self.number, AT3Command.INCREMENT)
    def TemperatureDec(self) -> bool: 
        return self._at3classToggleSpFunc(self.number, AT3Command.DECREMENT)

class AT3Group:
    name = "Unknown"
    number = -1
    is_on = False
    mode = AT3GroupMode.INVALID
    open_percent = -1
    temperature = -1
    temperature_sp = -1
    _at3classToggleFunc = None
    _at3classTogglePosFunc = None

    def __init__(self, name, number, toggleFunc, togglePosFunc):
        self.name = name
        self.number = number
        self._at3classToggleFunc = toggleFunc
        self._at3classTogglePosFunc = togglePosFunc
    
    def Toggle(self) -> bool: 
        return self._at3classToggleFunc(self.number)
    def PositionInc(self) -> int: 
        return self._at3classTogglePosFunc(self.number, AT3Command.INCREMENT)
    def PositionDec(self) -> int: 
        return self._at3classTogglePosFunc(self.number, AT3Command.DECREMENT)

class AT3TempSensor:
    name = "Unknown"
    temperature = -1
    available = False
    low_battery = False
    def __init__(self, name):
        self.name = name

class AirTouch3:

    _tcp_ip = ""
    _TCP_PORT = 8899    # Hardcoded as should never change

    name = ""
    id = ""
    comms_status = AT3CommsStatus.ERROR
    comms_error = "Uninitialised"
    groups: Dict[int, AT3Group] = dict()
    acUnits: Dict[int, AT3AcUnit] = dict()
    sensors: Dict[str, AT3TempSensor] = dict()

    def __init__(self, tcp_ip) -> None:
        self._tcp_ip = tcp_ip
        self.comms_status = AT3CommsStatus.NOT_CONNECTED
        self.comms_error = "Connection yet to be Attempted"

    def UpdateStatus(self) -> bool:

        # Send a command to the Air Touch 3
        # Byte1 = 1 means request status only
        data = self._Send_Recieve(AT3Const.CMD_1_STATUS, 0, 0, 0)
        
        # Process the response, returning valid processing of reponse
        return self._Process_Response(data)

    def ToogleAcUnit(self, acUnit) -> bool:

        # Send command to the Air Touch 3 if valid ac unit number
        if acUnit >= 0 and acUnit < len(self.acUnits):
            data = self._Send_Recieve(AT3Const.CMD_1_AC_CTRL, acUnit,
                                        AT3Const.CMD_4_TOGGLE, 0)

            # Process the response, if fails, return none to indicate error
            if not self._Process_Response(data): return None

            # return status of AC Unit
            return self.acUnits[acUnit].is_on

        # Invalid Ac Unit was given
        return None

    def ToggleTemperaturAcUnit(self, acUnit, direction:AT3Command) -> bool:

        # Send command to the Air Touch 3 if valid ac unit number
        if acUnit >= 0 and acUnit < len(self.acUnits):

            cmd = AT3Const.CMD_4_AC_TEMP_DEC
            if direction == AT3Command.INCREMENT: 
                cmd = AT3Const.CMD_4_AC_TEMP_INC
            data = self._Send_Recieve(AT3Const.CMD_1_AC_CTRL, acUnit, cmd, 0)

            # Process the response, if fails, return none to indicate error
            if not self._Process_Response(data): return None

            # return status of AC Unit
            return self.acUnits[acUnit].temperature_sp

        # Invalid Ac Unit was given
        return None

    def ToggleGroup(self, group) -> bool:

        # Send command to the Air Touch 3 if valid group number
        if group >= 0 and group < len(self.groups):
            data = self._Send_Recieve(AT3Const.CMD_1_GRP_CTRL, group, 
                                        AT3Const.CMD_4_TOGGLE, 0)

            # Process the response, if fails, return none to indicate error
            if not self._Process_Response(data): return None

            # return status of group
            return self.groups[group].is_on

        # Invalid group number was given
        return None

    def TogglePositionGroup(self, group, direction:AT3Command) -> int:
           
        # Send command to the Air Touch 3 if valid group number
        if group >= 0 and group < len(self.groups):

            cmd = AT3Const.CMD_4_GRP_POSDEC 
            if direction == AT3Command.INCREMENT:
                AT3Const.CMD_4_GRP_POSINC
                
            data = self._Send_Recieve(AT3Const.CMD_1_GRP_CTRL, group, cmd, 
                                        AT3Const.CMD_5_GRP_POS)

            # Process the response, if fails, return none to indicate error
            if not self._Process_Response(data): return None

            # return status of group
            return self.groups[group].open_percent

        # Invalid group number was given
        return None
    
    def PrintStatus(self) -> None:
        print(f"System Name: {self.name}")
        print(f"System ID: {self.id}")
        for g in self.groups.values():
            print(f"Group[{g.number}]: {g.name}; On: {g.is_on}; "
                  f"Mode is {g.mode}; Percent: {g.open_percent}%; "
                  f"Temp: {g.temperature}degC; "
                  f"Target: {g.temperature_sp}degC")
        for ac in self.acUnits.values():
            print(f"AC Unit[{ac.number}]: {ac.name}; On: {ac.is_on}; "
                  f"Error: {ac.has_error}; Mode: {ac.mode}; "
                  f"Brand ID: {ac.brand}; Fan: {ac.fan_speed}; "
                  f"Temp: {ac.temperature}degC; "
                  f"Target: {ac.temperature_sp}degC")
        for s in self.sensors.values():
            print(f"Sensor[{s.name}]: {s.temperature}degC; "
                  f"Low Battery: {s.low_battery}")

    def _Process_Response(self, response) -> bool:

        # No data received, must be a connection error, nothing to do
        # also make sure we recieved a response of length 492 bytes
        if not response or len(response) != AT3Const.RESPONSE_LEN:
            comms_status = AT3CommsStatus.ERROR
            comms_stauts = "Invalid Response Received"
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
                self.groups[z] = AT3Group(name, z, self.ToggleGroup, 
                                            self.TogglePositionGroup)

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
            if not self.acUnits.get(a):
                self.acUnits[a] = AT3AcUnit(name, a, self.ToogleAcUnit, 
                                                self.ToggleTemperaturAcUnit)

            # Get the ac unit and set the name
            acUnit = self.acUnits.get(a)
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
        sensor = self._Update_Or_Add_Sensor(name, byte_value)

        # If valid group and sensor available (should always be available 
        # because its a TP), set temperature of group
        # assign the temperature to the appropriate group
        if group_id > 0 and group_id <= num_groups and sensor:
            self.groups[group_id - 1].temperature = sensor.temperature  

        # Get the sensors in the system
        for s in range(AT3Const.TEMP_SENSOR_LEN):
            byte_value = response[AT3Const.DAOF_TEMP_SENSORS+s]
            self._Update_Or_Add_Sensor(f"Sensor {s+1}", byte_value)

        # Load the system name and id
        stt = AT3Const.DAOF_SYS_NAME
        end = stt + AT3Const.SYS_NAME_LEN
        self.name = response[stt:end].decode().strip().strip('\x00')
        stt = AT3Const.DAOF_SYS_ID
        end = stt + AT3Const.SYS_ID_LEN
        self.id = response[stt:end].decode().strip().strip('\x00')

        # Successfully processed response
        return True

    def _Update_Or_Add_Sensor(self, name, byte_value):

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

    def _Send_Recieve(self, byte1, byte3, byte4, byte5) -> bytes:

        # Should always be much less than this (ref AT3Const.RESPONSE_LEN)
        BUFFER_SIZE = 1024

        # Command is 12 bytes, add checksum as 13th
        rList = [AT3Const.CMD_0, byte1, AT3Const.CMD_2, byte3, byte4, byte5, 0, 0, 0, 0, 0, 0]
        rChk = AT3Helper.calculate_checksum(rList)
        rList.extend(rChk)
        arr = bytes(rList)

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5.0)
            s.connect((self._tcp_ip, self._TCP_PORT))
            s.send(arr)
            s.settimeout(20.0)
            data = s.recv(BUFFER_SIZE)
            s.close()
            self.comms_status = AT3CommsStatus.OK
            self.comms_error = ""
            return data
        except OSError as e:
            self.comms_status = AT3CommsStatus.NOT_CONNECTED
            self.comms_error = format(e)
            return None
