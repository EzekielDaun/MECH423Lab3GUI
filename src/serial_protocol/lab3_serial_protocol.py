from dataclasses import dataclass
from enum import IntEnum


class SerialControlBytes(IntEnum):
    ECHO = (0x00 << 8) + 0x00
    DC_MOTOR_OPEN_LOOP_VOLTAGE = (0x01 << 8) + 0x00
    STEPPER_MOTOR_SINGLE_STEP = (0x02 << 8) + 0x00
    STEPPER_MOTOR_OPEN_LOOP_SPEED = (0x02 << 8) + 0x01


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
