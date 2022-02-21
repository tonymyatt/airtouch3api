# Airtouch 3 Python API
Api for the monitoring and control of a HVAC unit branded Polyaire Airtouch 3.
https://www.polyaire.com.au/about-us/news/airtouch-version-3-now-available/

## Usage
To initialise:\
`at3 = AirTouch3("192.168.1.1")`

To read status from unit, return true if succesful, otherwise false:\
`at3.UpdateStatus();`

print(f"Group[{g.number}]: {g.name}; On: {g.is_on}; Mode is {g.mode}; Percent: {g.open_percent}%; Temp: {g.temperature}degC; Target: {g.temperature_sp}degC")
        for ac in self.acUnits.values():
            print(f"AC Unit[{ac.number}]: {ac.name}; On: {ac.is_on}; Error: {ac.has_error}; Mode: {ac.mode}; Brand ID: {ac.brand}; Fan: {ac.fan_speed} Temp: {ac.temperature}degC Target: {ac.temperature_sp}degC")
        for s in self.sensors.values():
            print(f"Sensor[{s.name}]: {s.temperature}degC; Low Battery: {s.low_battery}")

The following functions are available:

## General
`at3.name`\
`at3.id`\
`at3.comms_status`\
`at3.comms_error`\
`at3.groups`\
`at3.acUnits`\
`at3.sensors`
`at3.UpdateStatus()`
`at3.PrintStatus()`

## Group Functions (aka Zones in most other systems)
`at3.ToggleGroup(group_id)`\
`at3.TogglePositionGroup(group_id, direction)`\
## Group Objects
`at3.groups[group_id].number`\
`at3.groups[group_id].name`\
`at3.groups[group_id].is_on`\
`at3.groups[group_id].mode`\
`at3.groups[group_id].open_percent`\
`at3.groups[group_id].temperature`\
`at3.groups[group_id].tempeature_sp`\
`at3.groups[group_id].Toggle()`\
`at3.groups[group_id].PositionDec()`\
`at3.groups[group_id].PositionInc()`

## AC Unit Functions
`at3.ToogleAcUnit(unit_id)`\
`at3.ToggleTemperaturAcUnit(unit_id, direction)`\
## AC Unit Objects
`at3.acUnits[unit_id].number`\
`at3.acUnits[unit_id].is_on`\
`at3.acUnits[unit_id].has_error`\
`at3.acUnits[unit_id].mode`\
`at3.acUnits[unit_id].brand`\
`at3.acUnits[unit_id].fan_speed`\
`at3.acUnits[unit_id].temperature`\
`at3.acUnits[unit_id].temperature_sp`\
`at3.acUnits[unit_id].Toggle()`\
`at3.acUnits[unit_id].TemperatureInc()`\
`at3.acUnits[unit_id].TemperatureDec()`

## AC Sensor Objects
`at3.sensors[sensor_name].name`\
`at3.sensors[sensor_name].temperature`\
`at3.sensors[sensor_name].low_battery`

# Warning
This was code developed by testing with my Airtouch 3 system. I noted during development, if the unit received unexpected data, it would stop all communication (which includes to your mobile app) for a couple of minutes. There should be no issues with your Airtouch 3 system continuing to work with your mobile app while using this API, buts that your risk if you try it and you have problems.

# Thanks
With thanks to the following projects which provided inspiration:\
https://github.com/ozczecho/vzduch-dotek \
https://github.com/L0rdCha0s/homebridge-airtouch3-airconditioner \
https://github.com/LonePurpleWolf/airtouch4pyapi
