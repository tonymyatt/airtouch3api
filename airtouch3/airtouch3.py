from enum import Enum
import socket
from typing import Dict

import airtouch3.constants as const
from airtouch3.helper import (
    calculate_checksum, 
    bit8_in_byte_on, 
    bit7_in_byte_on
)

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

    def __init__(self, name, number, at3object):
        self.name = name
        self.number = number
        self._at3 = at3object

    def toggle(self) -> bool: 
        return self._at3.toggle_ac_unit(self.number)
    def temperature_inc(self) -> bool: 
        return self._at3.toggle_temperature_ac_unit(self.number, AT3Command.INCREMENT)
    def temperature_dec(self) -> bool: 
        return self._at3.toggle_temperature_ac_unit(self.number, AT3Command.DECREMENT)
    def set_fan_speed(self, speed:AT3AcFanSpeed) -> AT3AcFanSpeed: 
        return self._at3.set_fan_speed_ac_unit(self.number, speed)
    def set_mode(self, mode:AT3AcMode) -> AT3AcMode:
        return self._at3.set_mode_ac_unit(self.number, mode)

class AT3Group:
    name = "Unknown"
    number = -1
    is_on = False
    mode = AT3GroupMode.INVALID
    open_percent = -1
    temperature = -1
    temperature_sp = -1

    def __init__(self, name, number, at3object):
        self.name = name
        self.number = number
        self._at3 = at3object

    def toggle(self) -> bool: 
        return self._at3.toggle_group(self.number)
    def position_inc(self) -> int: 
        return self._at3.toggle_position_group(self.number, AT3Command.INCREMENT)
    def position_dec(self) -> int: 
        return self._at3.toggle_position_group(self.number, AT3Command.DECREMENT)

class AT3TempSensor:
    name = "Unknown"
    temperature = -1
    available = False
    low_battery = False
    def __init__(self, name):
        self.name = name

class AirTouch3:

    # Hardcoded as should never change
    _TCP_PORT = 8899

    _tcp_ip = ""

    comms_status = AT3CommsStatus.ERROR
    comms_error = "Uninitialised"
    name = ""
    id = ""
    groups: Dict[int, AT3Group] = dict()
    ac_units: Dict[int, AT3AcUnit] = dict()
    sensors: Dict[str, AT3TempSensor] = dict()

    def __init__(self, tcp_ip) -> None:
        self._tcp_ip = tcp_ip
        self.comms_status = AT3CommsStatus.NOT_CONNECTED
        self.comms_error = "Connection yet to be Attempted"

    def update_status(self) -> bool:

        # Send a command to the Air Touch 3 to read status
        data = self._send_recieve(const.CMD_1_STATUS, 0, 0, 0)
        
        # Process the response, returning valid processing of reponse
        return self._process_response(data)

    def toggle_ac_unit(self, acUnit) -> bool:

        # Send command to the Air Touch 3 if valid ac unit number
        if acUnit >= 0 and acUnit < len(self.ac_units):
            data = self._send_recieve(const.CMD_1_AC_CTRL, acUnit,
                                        const.CMD_4_TOGGLE, 0)

            # Process the response, if fails, return none to indicate error
            if not self._process_response(data): return None

            # return status of AC Unit
            return self.ac_units[acUnit].is_on

        # Invalid Ac Unit was given
        return None

    def toggle_temperature_ac_unit(self, acUnit, direction:AT3Command) -> bool:

        # Invalid Ac Unit was given
        if acUnit < 0 or acUnit >= len(self.ac_units):
            return None

        cmd = const.CMD_4_AC_TEMP_DEC
        if direction == AT3Command.INCREMENT: 
            cmd = const.CMD_4_AC_TEMP_INC
        data = self._send_recieve(const.CMD_1_AC_CTRL, acUnit, cmd, 0)

        # Process the response, if fails, return none to indicate error
        if not self._process_response(data): return None

        # return status of AC Unit
        return self.ac_units[acUnit].temperature_sp  

    def set_fan_speed_ac_unit(self, acUnit, speed:AT3AcFanSpeed) -> AT3AcFanSpeed:

        # Invalid Ac Unit was given
        if acUnit < 0 or acUnit >= len(self.ac_units):
            return None

        data = self._send_recieve(const.CMD_1_AC_CTRL, acUnit, 
                                    const.CMD_4_AC_FAN_SPD, speed.value)

        # Process the response, if fails, return none to indicate error
        if not self._process_response(data): return None

        # return status of AC Unit
        return self.ac_units[acUnit].fan_speed

    def set_mode_ac_unit(self, acUnit, mode: AT3AcMode) -> AT3AcMode:

         # Invalid Ac Unit was given
        if acUnit < 0 or acUnit >= len(self.ac_units):
            return None

        data = self._send_recieve(const.CMD_1_AC_CTRL, acUnit, 
                                    const.CMD_4_AC_MODE, mode.value)
        
        # Process the response, if fails, return none to indicate error
        if not self._process_response(data): return None

        # return status of AC Unit
        return self.ac_units[acUnit].mode


    def toggle_group(self, group) -> bool:

        # Send command to the Air Touch 3 if valid group number
        if group >= 0 and group < len(self.groups):
            data = self._send_recieve(const.CMD_1_GRP_CTRL, group, 
                                        const.CMD_4_TOGGLE, 0)

            # Process the response, if fails, return none to indicate error
            if not self._process_response(data): return None

            # return status of group
            return self.groups[group].is_on

        # Invalid group number was given
        return None

    def toggle_position_group(self, group, direction:AT3Command) -> int:
           
        # Send command to the Air Touch 3 if valid group number
        if group >= 0 and group < len(self.groups):

            cmd = const.CMD_4_GRP_POSDEC 
            if direction == AT3Command.INCREMENT:
                cmd = const.CMD_4_GRP_POSINC
                
            data = self._send_recieve(const.CMD_1_GRP_CTRL, group, cmd, 
                                        const.CMD_5_GRP_POS)

            # Process the response, if fails, return none to indicate error
            if not self._process_response(data): return None

            # return status of group
            return self.groups[group].open_percent

        # Invalid group number was given
        return None
    
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

    def _process_response(self, response) -> bool:

        # No data received, must be a connection error, nothing to do
        # also make sure we recieved a response of length 492 bytes
        if not response or len(response) != const.RESPONSE_LEN:
            self.comms_status = AT3CommsStatus.ERROR
            self.comms_status = "Invalid Response Received"
            return False

        # Loop through the maximum number of zones
        # these are the dampers themselves, which are "grouped" 
        # into what is usually known as zones
        zones = []
        for z in range(const.ZONES_LEN):
            # MSB is zone on/off (x) and LS three bits are zone 
            # number 0-7 (y) x000_0yyy. Note the zone number for 
            # zones 1-8 is 0-7 and repeats for zones 9-16, ie 0-7
            byte_value = response[const.DAOF_ZONE_STATE+z]
            zones.append(bit8_in_byte_on(byte_value))

        # Loop through all the groups, only load the number 
        # configured in the system
        num_groups = int(response[const.DAOF_GRP_COUNT])
        for z in range(min(const.GROUPS_LEN, num_groups)):

            # Group names are all fixed character length
            stt = const.DAOF_GRP_NAME + (z * const.GRP_NAME_LEN)
            end = stt + const.GRP_NAME_LEN
            name = response[stt:end].decode().strip().strip('\x00')

            # Groups are stored using their number as the index
            # Try and get the group via its number, if non found, add it
            if not self.groups.get(z):
                self.groups[z] = AT3Group(name, z, self)

            # Get the group from he dict and set the name
            group = self.groups.get(z)
            group.name = name

            # Get the first zone in the group and base the status 
            # of the group on that zone. All zones in a group will have
            # the same status, so only need to read the first
            byte_value = response[const.DAOF_GRP_FIRSTZONE+z]
            first_zone = int((byte_value & 0b1111_0000) >> 4)
            group.is_on = zones[first_zone]    

            # Mode of zone is 7th bit, if on then temp control, 
            # else percent position
            byte_value = response[const.DAOF_GRP_PERCENT+z]
            group.mode = AT3GroupMode.PERECENT
            if bit8_in_byte_on(byte_value):
                group.mode = AT3GroupMode.TEMPERATURE

            # Temperature setpoint is bottom 5 bits 
            # (less one from setpoint, kinda wierd?!)
            byte_value = response[const.DAOF_GRP_SETPOINT+z]
            group.temperature_sp = int(byte_value & 0b0001_1111) + 1

            # Group percent is bottom 7 bits and 1 count per 5%
            byte_value = response[const.DAOF_GRP_PERCENT+z]
            percent = 5*int(byte_value & 0b0111_1111)
            group.open_percent = percent if group.is_on else 0

        # Update AC Units from the response
        # TODO At the moment, get data for two air cons, need to work  out 
        # how many air cons are being used and what groups are allocated 
        # to each air con
        for a in range(const.AC_UNIT_LEN):

            # Names are straight after each other in the config file
            stt = const.DAOF_AC1_NAME + const.AC_NAME_LEN*a
            end = stt + const.AC_NAME_LEN
            name = response[stt:end].decode().strip().strip('\x00')

            # AC Units are stored using their number as the index
            # Try and get the group via its number, if non found, add it
            if not self.ac_units.get(a):
                self.ac_units[a] = AT3AcUnit(name, a, self)

            # Get the ac unit and set the name
            acUnit = self.ac_units.get(a)
            acUnit.name = name
            
            # Status contains on/off and error bits
            status = response[const.DAOF_AC1_STATUS+a]
            acUnit.is_on = bit8_in_byte_on(status)
            acUnit.has_error = bit7_in_byte_on(status)

            # Get the brand id, we need this to issue commands to the AcUnit, 
            # otherwise, who cares right?
            acUnit.brand = int(response[const.DAOF_AC1_BRAND+a])

            # Mode at in heat/cool etc in bottom 4 bits
            byte_value = response[const.DAOF_AC1_MODE+a]
            acUnit.mode = AT3AcMode(int(byte_value & 0b0000_1111))
            
            # Fan Speed is only bottom 4 bits
            byte_value = response[const.DAOF_AC1_FAN+a]
            acUnit.fan_speed = AT3AcFanSpeed(int(byte_value & 0b0000_1111))

            # Get the temp control mode, but dont do anything with it
            # TODO Not used at the moment, dont know how air touch 3 
            # re-assigns the temperature feedback based on this mode
            #data[DAOF_AC1_THERM_MODE+a]
            
            # This is the temperature from the AC unit itself, depending 
            # on setup, a zone temp might be being used as the AC temp 
            # feedback TODO, need to reassign the temperature based on the 
            # therm mode above
            acUnit.temperature = int(response[const.DAOF_AC1_TEMP_PV+a])

            # Temperature setpoint; ignore top two bits as usual, for 
            # temp values
            byte_value = response[const.DAOF_AC1_TEMP_SP+a]
            acUnit.temperature_sp = int(byte_value & 0b0011_1111)

        # Touch pad information, add to sensor list
        # The Group the touch pad temperature is assigned to
        group_id = int(response[const.DAOF_TP_GRP_ID])
        name = "Touch Pad 1"

        # Save sensor into the sensor list, returns the sensor object
        byte_value = response[const.DAOF_TP_TEMP]
        sensor = self._update_or_add_sensor(name, byte_value)

        # If valid group and sensor available (should always be available 
        # because its a TP), set temperature of group
        # assign the temperature to the appropriate group
        if group_id > 0 and group_id <= num_groups and sensor:
            self.groups[group_id - 1].temperature = sensor.temperature  

        # Get the sensors in the system
        for s in range(const.TEMP_SENSOR_LEN):
            byte_value = response[const.DAOF_TEMP_SENSORS+s]
            self._update_or_add_sensor(f"Sensor {s+1}", byte_value)

        # Load the system name and id
        stt = const.DAOF_SYS_NAME
        end = stt + const.SYS_NAME_LEN
        self.name = response[stt:end].decode().strip().strip('\x00')
        stt = const.DAOF_SYS_ID
        end = stt + const.SYS_ID_LEN
        self.id = response[stt:end].decode().strip().strip('\x00')

        # Successfully processed response
        return True

    def _update_or_add_sensor(self, name, byte_value):

        temperature = byte_value & 0b0011_1111     # Bits 0 to 6
        available = bit8_in_byte_on(byte_value)    # Bit 8
        low_battery = bit7_in_byte_on(byte_value)  # Bit 7

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

    def _send_recieve(self, byte1, byte3, byte4, byte5) -> bytes:

        # Should always be much less than this (ref const.RESPONSE_LEN)
        BUFFER_SIZE = 1024

        # Command is 12 bytes, add checksum as 13th
        rList = [const.CMD_0, byte1, const.CMD_2, 
                    byte3, byte4, byte5, 0, 0, 0, 0, 0, 0]
        rChk = calculate_checksum(rList)
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
