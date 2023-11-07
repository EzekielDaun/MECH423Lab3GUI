from datetime import datetime

from loguru import logger
from pyqtgraph import GraphicsLayoutWidget
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGroupBox, QHBoxLayout

from ..serial_protocol.lab3_serial_protocol import SerialControlBytes, SerialPacket
from ..widget.valued_slider import ValuedSlider


class DCMotorWidget(QGroupBox):
    signal_serial_write = Signal(bytearray)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setTitle("DC Motor Control")

        self.__dc_motor_slider = ValuedSlider()
        self.__dc_motor_slider.slider.setTracking(True)
        self.__dc_motor_slider.slider.setRange(-0xFFFF, 0xFFFF)
        self.__dc_motor_slider.spinbox.setRange(-0xFFFF, 0xFFFF)
        self.__dc_motor_slider.signal_value_changed.connect(
            self.__slot_on_dc_motor_duty_changed
        )

        self.__graphics_layout_widget = GraphicsLayoutWidget()
        # self.__graphics_layout_widget.setTitle("DC Motor Data")

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

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.__dc_motor_slider)
        self.layout().addWidget(self.__graphics_layout_widget)

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

        # self.update_plot((value, datetime.now()))

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
