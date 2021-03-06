import pyxel

from .ui_constants import BUTTON_ENABLED_COLOR, BUTTON_PRESSED_COLOR
from .widget import Widget


class RadioButton(Widget):
    """
    Events:
        __on_change(value)
    """

    def __init__(self, parent, x, y, img, sx, sy, btn_count, **kwargs):
        width = btn_count * 9 - 2
        height = 7
        super().__init__(parent, x, y, width, height, **kwargs)

        self._img = img
        self._sx = sx
        self._sy = sy
        self._btn_count = btn_count
        self._value = 0

        self.add_event_handler("mouse_down", self.__on_mouse_down)
        self.add_event_handler("mouse_drag", self.__on_mouse_drag)
        self.add_event_handler("draw", self.__on_draw)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self._value != value:
            self._value = value
            self.call_event_handler("change", value)

    def __on_mouse_down(self, key, x, y):
        if key != pyxel.KEY_LEFT_BUTTON:
            return

        x -= self.x
        y -= self.y

        index = min(max(x // 9, 0), self._btn_count - 1)

        x1 = index * 9
        y1 = 0
        x2 = x1 + 6
        y2 = y1 + 6

        if x >= x1 and x <= x2 and y >= y1 and y <= y2:
            self.value = index

    def __on_mouse_drag(self, key, x, y, dx, dy):
        self.__on_mouse_down(key, x, y)

    def __on_draw(self):
        pyxel.pal(BUTTON_ENABLED_COLOR, BUTTON_PRESSED_COLOR)
        pyxel.blt(
            self.x + self.value * 9,
            self.y,
            self._img,
            self._sx + self.value * 9,
            self._sy,
            7,
            7,
        )
        pyxel.pal()
