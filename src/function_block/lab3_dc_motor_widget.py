from PySide6.QtSerialPort import QSerialPort
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
)
from serial_protocol.lab3_serial_protocol import SerialControlBytes, SerialPacket
from widget.valued_slider import ValuedSlider


class DCMotorWidget(QGroupBox):
    def __init__(self, serial_port: QSerialPort, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__serial_port = serial_port

        self.setTitle("DC Motor Control")

        self.__dc_motor_slider = ValuedSlider()
        self.__dc_motor_slider.slider.setTracking(True)
        self.__dc_motor_slider.slider.setRange(-0xFFFF, 0xFFFF)
        self.__dc_motor_slider.spinbox.setRange(-0xFFFF, 0xFFFF)
        self.__dc_motor_slider.signal_value_changed.connect(
            self.__slot_on_dc_motor_duty_changed
        )

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.__dc_motor_slider)

    def __slot_on_dc_motor_duty_changed(self, value: int):
        self.__serial_port.write(
            SerialPacket(
                SerialControlBytes.DC_MOTOR_OPEN_LOOP_VOLTAGE,
                bytearray([int(value > 0), abs(value) >> 8, abs(value) & 0x00FF]),
            ).to_bytearray()
        )
