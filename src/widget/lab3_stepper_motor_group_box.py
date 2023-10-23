from PySide6.QtCore import Qt
from PySide6.QtSerialPort import QSerialPort
from PySide6.QtWidgets import (
    QAbstractButton,
    QButtonGroup,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
)
from serial_protocol.lab3_serial_protocol import SerialControlBytes, SerialPacket


class StepperMotorWidget(QGroupBox):
    def __init__(self, serial_port: QSerialPort, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__serial_port = serial_port

        self.setTitle("Stepper Motor Control")

        self.setLayout(QVBoxLayout())
        self.__stepper_motor_single_step_cw_button = QPushButton("Single Step CW")
        self.__stepper_motor_single_step_ccw_button = QPushButton("Single Step CCW")
        self.__stepper_motor_single_step_button_group = QButtonGroup()
        self.__stepper_motor_single_step_button_group.addButton(
            self.__stepper_motor_single_step_cw_button
        )
        self.__stepper_motor_single_step_button_group.addButton(
            self.__stepper_motor_single_step_ccw_button
        )
        self.__stepper_motor_single_step_button_group.buttonClicked.connect(
            self.__slot_on_stepper_motor_single_step
        )
        stepper_motor_single_step_button_layout = QHBoxLayout()
        stepper_motor_single_step_button_layout.addWidget(
            self.__stepper_motor_single_step_cw_button
        )
        stepper_motor_single_step_button_layout.addWidget(
            self.__stepper_motor_single_step_ccw_button
        )
        self.layout().addLayout(stepper_motor_single_step_button_layout)  # type: ignore

        self.__slider = QSlider(Qt.Orientation.Horizontal)
        self.__slider.setMinimum(-0xFFFF)
        self.__slider.setMaximum(0xFFFF)
        self.__slider.setTracking(True)
        self.__slider.valueChanged.connect(self.__slot_on_slider_changed)
        self.layout().addWidget(self.__slider)

    def __slot_on_stepper_motor_single_step(self, button: QAbstractButton):
        if button is self.__stepper_motor_single_step_cw_button:
            self.__serial_port.write(
                SerialPacket(
                    SerialControlBytes.STEPPER_MOTOR_SINGLE_STEP,
                    bytearray([1]),
                ).to_bytearray()
            )
        else:
            self.__serial_port.write(
                SerialPacket(
                    SerialControlBytes.STEPPER_MOTOR_SINGLE_STEP,
                    bytearray([0]),
                ).to_bytearray()
            )

    def __slot_on_slider_changed(self, value: int):
        direction = value > 0

        self.__serial_port.write(
            SerialPacket(
                SerialControlBytes.STEPPER_MOTOR_OPEN_LOOP_SPEED,
                bytearray([int(direction), abs(value) >> 8, abs(value) & 0x00FF]),
            ).to_bytearray()
        )
