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
CMD_4_AC_MODE = 129         # AC mode in byte 4
CMD_4_AC_FAN_SPD = 130      # AC Fan speed in byte 4
CMD_4_AC_TEMP_DEC = 147     # AC Temperature setpoint decrement in byte 4
CMD_4_AC_TEMP_INC = 163     # AC Temperature setpoint increment in byte 4
CMD_5_GRP_POS = 1           # In Position dec/inc command, byte 5 is fixed
