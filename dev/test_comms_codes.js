"use strict";
exports.__esModule = true;
exports.AirTouchMessage = void 0;
var AirTouchMessage = /** @class */ (function () {
    function AirTouchMessage() {
        this.buffer = new Int8Array(13);
        this.sumByte = new Int8Array(13);
    }
    AirTouchMessage.prototype.resetMessage = function () {
        for (var i = 0; i < 13; i++) {
            this.buffer[i] = 0;
        }
        this.buffer[0] = 85;
        this.buffer[2] = 12;
    };
    AirTouchMessage.prototype.UInt8 = function (value) {
        return (value & 0xFF);
    };
    ;
    AirTouchMessage.prototype.Int8 = function (value) {
        var ref = this.UInt8(value);
        return (ref > 0x7F) ? ref - 0x100 : ref;
    };
    ;
    AirTouchMessage.prototype.printHexCode = function (msg) {
        //this.log.debug(Array.apply([], Array.from(this.buffer)).join(","));
        //console.log(this.buffer.join(","));
        var s = "";
        for (var i = 0; i < 13; i++) {
            s += "\\x" + this.buffer[i].toString(16);
        }
        //console.log("HEX: "+s);
        s = "";
        for (var i = 0; i < 13; i++) {
            s += " " + this.UInt8(this.buffer[i]);
        }
        console.log(msg + ": " + s);
    };
    AirTouchMessage.prototype.calcChecksum = function () {
        var reSum = 0;
        for (var i = 0; i <= this.sumByte.length - 1; i++) {
            this.sumByte[i] = this.buffer[i];
        }
        var reSum2 = 0;
        var i2 = 0;
        while (i2 <= this.sumByte.length - 2) {
            var b = this.sumByte[i2];
            if (b >= 0) {
                reSum = reSum2 + b;
            }
            else if (b == 0) //byte.minvalue
             {
                reSum = reSum2 + 128;
            }
            else {
                reSum = reSum2 + (b + 256);
            }
            i2++;
            reSum2 = reSum;
        }
        return reSum2;
    };
    AirTouchMessage.prototype.getInitMsg = function () {
        this.resetMessage();
        this.buffer[1] = 1;
        this.buffer[12] = this.calcChecksum();
        return this.buffer;
    };
    AirTouchMessage.prototype.toggleZone = function (zone) {
        this.resetMessage();
        this.buffer[1] = -127;
        this.buffer[3] = zone;
        this.buffer[4] = -128;
        this.buffer[12] = this.calcChecksum();
        return this.buffer;
    };
    AirTouchMessage.prototype.setFan = function (room, incDec) {
        this.resetMessage();
        this.buffer[1] = 1;
        this.buffer[1] = -127;
        this.buffer[3] = room;
        if (incDec >= 0) {
            this.buffer[4] = 2;
        }
        else {
            this.buffer[4] = 1;
        }
        this.buffer[5] = 1;
        this.buffer[12] = this.calcChecksum();
        return this.buffer;
    };
    AirTouchMessage.prototype.toggleAcOnOff = function (acId) {
        this.resetMessage();
        this.buffer[1] = -122;
        this.buffer[3] = acId;
        this.buffer[4] = -128;
        this.buffer[12] = this.calcChecksum();
        return this.buffer;
    };
    AirTouchMessage.prototype.setMode = function (acId, brandId, inMode) {
        this.resetMessage();
        var mode = inMode;
        //Translate apple homekit to airtouch:   In Homekit, Cool==2, in Airtouch, Cool == 4;
        //Also 'Fan' and 'Dry' don't exist in Homekit
        if (mode == 2) {
            mode = 4;
        }
        //this.log.debug("Air Conditioner brand id at mode select: " + brandId + " and mode " + mode);
        if (acId == 0 && brandId == 11) {
            switch (inMode) {
                case 0:
                    mode = 0;
                    break;
                case 1:
                    mode = 2;
                    break;
                case 2:
                    mode = 3;
                    break;
                case 3:
                    mode = 4;
                    break;
                case 4:
                    mode = 1;
                    break;
            }
        }
        if (acId == 0 && brandId == 15) {
            switch (inMode) {
                case 0:
                    mode = 5;
                    break;
                case 1:
                    mode = 2;
                    break;
                case 2:
                    mode = 3;
                    break;
                case 3:
                    mode = 4;
                    break;
                case 4:
                    mode = 1;
                    break;
            }
        }
        this.buffer[1] = -122;
        this.buffer[3] = acId;
        this.buffer[4] = -127;
        this.buffer[5] = mode;
        this.buffer[12] = this.calcChecksum();
        ts.printHexCode("AC Mode");
    };
    AirTouchMessage.prototype.setFanSpeed = function (acId, brandId, inMode) {
        this.resetMessage();
        var mode = inMode;
        if (acId == 0 && brandId == 15) {
            switch (mode) {
                case 0:
                    mode = 4;
                    break;
            }
        }
        if (acId == 0 && brandId == 2) {
            switch (mode) {
                case 0:
                    mode = 0;
                    break;
                case 4:
                    mode = 1;
                    break;
                default:
                    mode++;
                    break;
            }
        }
        //this.log.debug("Final mode sending for fan speed: " + mode);
        this.buffer[1] = -122;
        this.buffer[3] = acId;
        this.buffer[4] = -126;
        this.buffer[5] = mode;
        this.buffer[12] = this.calcChecksum();
        ts.printHexCode("AC Fan Speed");
    };
    AirTouchMessage.prototype.SetNewTemperature = function (acId, incDec) {
        this.resetMessage();
        this.buffer[1] = -122;
        this.buffer[3] = acId;
        if (incDec >= 0) {
            this.buffer[4] = -93;
        }
        else {
            this.buffer[4] = -109;
        }
        this.buffer[12] = this.calcChecksum();
        if (incDec >= 0) {
            ts.printHexCode("Increment Ac " + acId);
        }
        else {
            ts.printHexCode("Decrement Ac " + acId);
        }
    };
    return AirTouchMessage;
}());
exports.AirTouchMessage = AirTouchMessage;
var ts = new AirTouchMessage();
ts.setFanSpeed(0, 8, 1);
ts.setFanSpeed(1, 8, 1);
ts.setMode(1, 8, 1);
ts.setMode(1, 8, 2);
ts.getInitMsg();
ts.printHexCode("Init Message:");
ts.toggleZone(0);
ts.printHexCode("Toggle Zone 0:");
ts.toggleAcOnOff(1);
ts.printHexCode("Toggle AC 1:");
ts.SetNewTemperature(1, -1);
ts.SetNewTemperature(1, 1);
