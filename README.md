# Airtouch 3 Python API
Api for the monitoring and control of a HVAC unit branded Polyaire Airtouch 3.
https://www.polyaire.com.au/about-us/news/airtouch-version-3-now-available/

## Warning
This was code developed by testing with my Airtouch 3 system. I noted during development, if the unit received unexpected data, it would stop all communication (which includes to your mobile app) for a couple of minutes. There should be no issues with your Airtouch 3 system continuing to work with your mobile app while using this API, buts that your risk if you try it and you have problems.
## Usage
To initialise:
`at3 = AirTouch3("192.168.1.1")`

To read status from unit, return true if succesful, otherwise false:
`at3.UpdateStatus();`

Public variables:
`at3.name`
`at3.id`
`at3.comms_status`
`at3.comms_error`
`at3.groups`
`at3.acUnits`
`at3.sensors`

The following functions are available:

General:
`at3.PrintStatus()`

Group Functions (aka Zones in most other systems):
`at3.ToggleGroup(group_id)`
`at3.TogglePositionGroup(group_id, direction)`
Alternate Object Functions:
`at3.groups[group_id].Toggle()`
`at3.groups[group_id].PositionDec()`
`at3.groups[group_id].PositionInc()`

AC Unit Functions:
`at3.ToogleAcUnit(unit_id)`
`at3.ToggleTemperaturAcUnit(unit_id, direction)`
Alternate Object Functions:
`at3.acUnits[unit_id].Toggle()`
`at3.acUnits[unit_id].TemperatureInc()`
`at3.acUnits[unit_id].TemperatureDec()`

## Thanks
With thanks to the following projects which provided inspiration:
https://github.com/ozczecho/vzduch-dotek
https://github.com/L0rdCha0s/homebridge-airtouch3-airconditioner
https://github.com/LonePurpleWolf/airtouch4pyapi