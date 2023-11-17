from loguru import logger
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QDoubleSpinBox, QGroupBox, QHBoxLayout, QPushButton

from ..serial_protocol.lab3_serial_protocol import SerialControlBytes, SerialPacket


class TwoAxisControlWidget(QGroupBox):
    signal_serial_write = Signal(bytearray)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__timer = QTimer()
        self.__timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.__timer.timeout.connect(self.__slot_on_timer_timeout)

        self.setTitle("2-Axis Control")

        self.__x_input = QDoubleSpinBox()
        self.__x_input.setRange(-32768, 32767)
        self.__x_input.setPrefix("X: ")
        self.__x_input.setSuffix("cm")

        self.__y_input = QDoubleSpinBox()
        self.__y_input.setRange(-32768, 32767)
        self.__y_input.setPrefix("Y: ")
        self.__y_input.setSuffix("cm")

        self.__speed_input = QDoubleSpinBox()
        self.__speed_input.setRange(0, 100)
        self.__speed_input.setPrefix("Speed: ")
        self.__speed_input.setSuffix("%")

        self.__button = QPushButton("Move")
        self.__button.clicked.connect(self.__slot_on_move_pushed)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.__x_input)
        self.layout().addWidget(self.__y_input)
        self.layout().addWidget(self.__button)

    def __slot_on_move_pushed(self):
        self.__timer.stop()
        x_input_cm = self.__x_input.value()
        y_input_cm = self.__y_input.value()

        self.__step_count = int(((x_input_cm**2 + y_input_cm**2) ** 0.5) * 10)

        x_input_encoder_tick = x_input_cm * 1000
        y_input_step = y_input_cm * 1000
        self.__x_step = int(x_input_encoder_tick / self.__step_count)
        self.__y_step = int(y_input_step / self.__step_count)

        self.__timer.start(50)
        logger.info(
            f"Start moving {self.__step_count} total steps with X step {self.__x_step} encoder ticks and Y step {self.__y_step} half steps"
        )

        self.__button.setDisabled(True)

    def __slot_on_timer_timeout(self):
        if self.isEnabled():
            if self.__step_count > 0:
                self.__step_count -= 1

                logger.debug(f"{self.__step_count}")
                self.signal_serial_write.emit(
                    SerialPacket(
                        SerialControlBytes.TWO_AXIS_CONTROL,
                        bytearray([0x00, 0x00, 0x00, 0x00])
                        + bytearray(  # DC motor relative position
                            self.__x_step.to_bytes(2, "little", signed=True)
                        )
                        + bytearray([0x00])
                        + bytearray(  # stepper motor speed
                            int(10).to_bytes(2, "little", signed=False)
                        )
                        + bytearray([0x00])
                        + bytearray(  # stepper motor relative position
                            self.__y_step.to_bytes(2, "little", signed=True)
                        ),
                    ).to_bytearray()
                )
            else:
                self.__timer.stop()
                self.__button.setEnabled(True)
                return
