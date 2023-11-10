from datetime import datetime

from loguru import logger
from pyqtgraph import GraphicsLayoutWidget
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QPushButton, QSpinBox, QVBoxLayout

from ..serial_protocol.lab3_serial_protocol import SerialControlBytes, SerialPacket
from ..widget.valued_slider import ValuedSlider


class DCMotorWidget(QGroupBox):
    signal_serial_write = Signal(bytearray)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setTitle("DC Motor Control")

        # duty cycle control
        self.__dc_motor_duty_slider = ValuedSlider()
        self.__dc_motor_duty_slider.slider.setTracking(True)
        self.__dc_motor_duty_slider.slider.setRange(-0xFFFF, 0xFFFF)
        self.__dc_motor_duty_slider.spinbox.setRange(-0xFFFF, 0xFFFF)
        self.__dc_motor_duty_slider.signal_value_changed.connect(
            self.__slot_on_dc_motor_duty_changed
        )
        dc_motor_duty_group_box = QGroupBox("Open Loop Speed Control")
        dc_motor_duty_group_box.setLayout(QHBoxLayout())
        dc_motor_duty_group_box.layout().addWidget(self.__dc_motor_duty_slider)

        # absolute position control
        self.__dc_motor_position_slider = ValuedSlider()
        self.__dc_motor_position_slider.slider.setTracking(True)
        self.__dc_motor_position_slider.slider.setRange(-32768, 32767)
        self.__dc_motor_position_slider.spinbox.setRange(-32768, 32767)
        self.__dc_motor_position_slider.slider.setValue(0)
        self.__dc_motor_position_slider.signal_value_changed.connect(
            self.__slot_on_absolute_position_changed
        )
        # relative position control
        self.__dc_motor_position_increment_spinbox = QSpinBox()
        self.__dc_motor_position_increment_spinbox.setRange(-32768, 32767)
        self.__dc_motor_relative_position_move_button = QPushButton("Relative Move")
        self.__dc_motor_relative_position_move_button.clicked.connect(
            self.__slot_on_relative_position_changed
        )
        relative_position_layout = QHBoxLayout()
        relative_position_layout.addWidget(self.__dc_motor_position_increment_spinbox)
        relative_position_layout.addWidget(
            self.__dc_motor_relative_position_move_button
        )
        dc_motor_position_group_box = QGroupBox("Position Control")
        dc_motor_position_group_box.setLayout(QVBoxLayout())
        dc_motor_position_group_box.layout().addWidget(self.__dc_motor_position_slider)
        dc_motor_position_group_box.layout().addLayout(relative_position_layout)  # type: ignore

        left_slider_layout = QVBoxLayout()
        left_slider_layout.addWidget(dc_motor_duty_group_box)
        left_slider_layout.addWidget(dc_motor_position_group_box)

        # data plot
        self.__graphics_layout_widget = GraphicsLayoutWidget()
        self.__position_plot = self.__graphics_layout_widget.addPlot(
            title="Position", row=0, col=0
        )
        self.__position_plot.setLabel("left", "Position (Cycle)")

        self.__velocity_plot = self.__graphics_layout_widget.addPlot(
            title="Velocity", row=1, col=0
        )
        self.__velocity_plot.setLabel("left", "Velocity (RPM)")

        self.__x_data = []
        self.__y_data1 = []
        self.__y_data2 = [0]

        dc_motor_data_plot_group_box = QGroupBox("Data Plot")
        dc_motor_data_plot_group_box.setLayout(QHBoxLayout())
        dc_motor_data_plot_group_box.layout().addWidget(self.__graphics_layout_widget)

        self.setLayout(QHBoxLayout())
        self.layout().addLayout(left_slider_layout)  # type: ignore
        # self.layout().addWidget(dc_motor_data_plot_group_box)

    def __slot_on_dc_motor_duty_changed(self, value: int):
        self.signal_serial_write.emit(
            SerialPacket(
                SerialControlBytes.DC_MOTOR_OPEN_LOOP_VOLTAGE,
                bytearray([int(value > 0), abs(value) >> 8, abs(value) & 0x00FF]),
            ).to_bytearray()
        )
        logger.info(
            f"DC motor duty changed to {abs(value)}, direction: {int(value > 0)}"
        )

    def update_plot(self, value: tuple[int, datetime]):
        count, time = value

        self.__x_data.append(time.timestamp())
        count_in_cycle = (count - 0x4000) / (20.4 * 48 / 4)
        self.__y_data1.append(count_in_cycle)
        if len(self.__y_data1) >= 2:
            self.__y_data2.append(
                (self.__y_data1[-1] - self.__y_data1[-2])
                / (self.__x_data[-1] - self.__x_data[-2])
                * 60
            )

        self.__x_data = self.__x_data[-100:]
        self.__y_data1 = self.__y_data1[-100:]
        self.__y_data2 = self.__y_data2[-100:]

        self.__position_plot.clear()
        self.__position_plot.plot(self.__x_data, self.__y_data1, pen="r", symbol="o")

        self.__velocity_plot.clear()
        self.__velocity_plot.plot(self.__x_data, self.__y_data2, pen="g", symbol="o")

    def __slot_on_absolute_position_changed(self, value: int):
        self.signal_serial_write.emit(
            SerialPacket(
                SerialControlBytes.DC_MOTOR_ABSOLUTE_POSITION,
                bytearray(value.to_bytes(length=2, byteorder="big", signed=True)),
            ).to_bytearray()
        )
        logger.info(f"DC motor absolute position changed to {value}")

    def __slot_on_relative_position_changed(self):
        self.signal_serial_write.emit(
            SerialPacket(
                SerialControlBytes.DC_MOTOR_RELATIVE_POSITION,
                bytearray(
                    self.__dc_motor_position_increment_spinbox.value().to_bytes(
                        length=2, byteorder="big", signed=True
                    )
                ),
            ).to_bytearray()
        )

        self.__dc_motor_position_slider.blockSignals(True)
        self.__dc_motor_position_slider.slider.setValue(
            self.__dc_motor_position_slider.slider.value()
            + self.__dc_motor_position_increment_spinbox.value()
        )
        self.__dc_motor_position_slider.blockSignals(False)

        logger.info(
            f"DC motor relative position moved {self.__dc_motor_position_increment_spinbox.value()}"
        )
