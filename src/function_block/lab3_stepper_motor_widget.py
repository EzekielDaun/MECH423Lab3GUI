from PySide6.QtSerialPort import QSerialPort
from PySide6.QtWidgets import (
    QAbstractButton,
    QButtonGroup,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
)
from serial_protocol.lab3_serial_protocol import SerialControlBytes, SerialPacket
from widget.valued_slider import ValuedSlider

from loguru import logger


class StepperMotorWidget(QGroupBox):
    def __init__(self, serial_port: QSerialPort, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__serial_port = serial_port

        self.setTitle("Stepper Motor Control")

        self.setLayout(QVBoxLayout())
        self.__single_step_widget = StepperMotorSingleStepWidget(self.__serial_port)
        self.layout().addWidget(self.__single_step_widget)
        self.__speed_widget = StepperMotorOpenLoopSpeedWidget(self.__serial_port)
        self.layout().addWidget(self.__speed_widget)


class StepperMotorSingleStepWidget(QGroupBox):
    def __init__(self, serial_port: QSerialPort, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__serial_port = serial_port

        self.setTitle("Single Half-Step")

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

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.__stepper_motor_single_step_cw_button)
        self.layout().addWidget(self.__stepper_motor_single_step_ccw_button)

    def __slot_on_stepper_motor_single_step(self, button: QAbstractButton):
        if button is self.__stepper_motor_single_step_cw_button:
            self.__serial_port.write(
                serial_bytes := SerialPacket(
                    SerialControlBytes.STEPPER_MOTOR_SINGLE_STEP,
                    bytearray([1]),
                ).to_bytearray()
            )
            logger.info("stepper motor cw single step")
            logger.debug(f"serial_bytes: {serial_bytes}")
        elif button is self.__stepper_motor_single_step_ccw_button:
            self.__serial_port.write(
                serial_bytes := SerialPacket(
                    SerialControlBytes.STEPPER_MOTOR_SINGLE_STEP,
                    bytearray([0]),
                ).to_bytearray()
            )
            logger.info("stepper motor ccw single step")
            logger.debug(f"serial_bytes: {serial_bytes}")


class StepperMotorOpenLoopSpeedWidget(QGroupBox):
    def __init__(self, serial_port: QSerialPort, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__serial_port = serial_port

        self.setTitle("Open Loop Speed")

        self.__valued_slider = ValuedSlider()
        self.__valued_slider.slider.setTracking(True)
        self.__valued_slider.slider.setRange(-0xFFFF, 0xFFFF)
        self.__valued_slider.spinbox.setRange(-0xFFFF, 0xFFFF)
        self.__valued_slider.signal_value_changed.connect(self.__slot_on_speed_changed)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.__valued_slider)

    def __slot_on_speed_changed(self, value: int):
        self.__serial_port.write(
            SerialPacket(
                SerialControlBytes.STEPPER_MOTOR_OPEN_LOOP_SPEED,
                bytearray([int(value > 0), abs(value) >> 8, abs(value) & 0x00FF]),
            ).to_bytearray()
        )
