from dataclasses import dataclass
from enum import IntEnum


class SerialControlBytes(IntEnum):
    ECHO = (0x00 << 8) + 0x00
    DC_MOTOR_OPEN_LOOP_VOLTAGE = (0x01 << 8) + 0x00
    DC_MOTOR_ABSOLUTE_POSITION = (0x01 << 8) + 0x01
    DC_MOTOR_RELATIVE_POSITION = (0x01 << 8) + 0x02
    STEPPER_MOTOR_SINGLE_STEP = (0x02 << 8) + 0x00
    STEPPER_MOTOR_OPEN_LOOP_SPEED = (0x02 << 8) + 0x01
    TWO_AXIS_CONTROL = (0x03 << 8) + 0x00


@dataclass(frozen=True)
class SerialPacket:
    control: SerialControlBytes
    data: bytearray

    @staticmethod
    def from_bytes(bytes: bytes):
        pass

    def to_bytearray(self):
        temp = bytearray([0xFF, self.control >> 8, self.control & 0x00FF, *self.data])

        if len(temp) < 15:
            temp = temp + bytearray(15 - len(temp))

        return temp + bytearray([sum(temp) % 0x100])  # checksum


@dataclass(frozen=True)
class MCUPacket:
    data: bytearray

    @staticmethod
    def from_bytes(bytes: bytes):
        if len(bytes) != 4:
            raise ValueError("Invalid packet length")
        if bytes[0] != 0xFF:
            raise ValueError("Invalid packet header")
        if bytes[3] != sum(bytes[:3]) % 0x100:
            raise ValueError("Invalid checksum")
        return MCUPacket(bytearray(bytes[1:3]))
