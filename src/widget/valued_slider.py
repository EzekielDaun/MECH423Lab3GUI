from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QSlider,
    QSpinBox,
    QWidget,
)


class ValuedSlider(QWidget):
    signal_value_changed = Signal(int)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.__slider = QSlider(Qt.Orientation.Horizontal)
        self.__slider.valueChanged.connect(self.__slot_on_slider_value_change)

        self.__spinbox = QSpinBox()
        self.__spinbox.valueChanged.connect(self.__slot_on_spinbox_value_change)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.__slider)
        self.layout().addWidget(self.__spinbox)

    @property
    def slider(self):
        return self.__slider

    @property
    def spinbox(self):
        return self.__spinbox

    def __slot_on_slider_value_change(self, value: int):
        self.__spinbox.blockSignals(True)
        self.__spinbox.setValue(value)
        self.__spinbox.blockSignals(False)
        self.signal_value_changed.emit(value)

    def __slot_on_spinbox_value_change(self, value: int):
        self.__slider.blockSignals(True)
        self.__slider.setValue(value)
        self.__slider.blockSignals(False)
        self.signal_value_changed.emit(value)
