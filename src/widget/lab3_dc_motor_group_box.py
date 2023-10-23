from PySide6.QtCore import Qt

from PySide6.QtSerialPort import QSerialPort
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSlider,
)
from serial_protocol.lab3_serial_protocol import SerialControlBytes, SerialPacket


class DCMotorWidget(QGroupBox):
    def __init__(self, serial_port: QSerialPort, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__serial_port = serial_port

        self.setTitle("DC Motor Control")

        self.setLayout(QHBoxLayout())
        self.__dc_motor_slider = QSlider(Qt.Orientation.Horizontal)
        self.__dc_motor_slider.setMinimum(-0xFFFF)
        self.__dc_motor_slider.setMaximum(0xFFFF)
        self.__dc_motor_slider.setTracking(True)
        self.__dc_motor_slider.valueChanged.connect(
            self.__slot_on_dc_motor_slider_changed
        )

        self.__dc_motor_duty_label = QLabel(
            f"Duty: {abs(self.__dc_motor_slider.value())/self.__dc_motor_slider.maximum() * 100:+06.2f}%"
        )

        self.layout().addWidget(self.__dc_motor_slider)
        self.layout().addWidget(self.__dc_motor_duty_label)

    def __slot_on_dc_motor_slider_changed(self,value:int):
        direction = value > 0

        self.__serial_port.write(
            SerialPacket(
                SerialControlBytes.DC_MOTOR_OPEN_LOOP_VOLTAGE,
                bytearray([int(direction), abs(value) >> 8, abs(value) & 0x00FF]),
            ).to_bytearray()
        )
        self.__dc_motor_duty_label.setText(
            f"Duty: {value/self.__dc_motor_slider.maximum() * 100:+06.2f}%"
        )
