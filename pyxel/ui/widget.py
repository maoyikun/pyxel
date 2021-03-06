import pyxel

from .ui_constants import (
    WIDGET_CLICK_DIST,
    WIDGET_CLICK_FRAME,
    WIDGET_HOLD_FRAME,
    WIDGET_REPEAT_FRAME,
)


class Widget:
    """
    Events:
        __on_show()
        __on_hide()
        __on_enabled()
        __on_disabled()
        __on_mouse_down(key, x, y)
        __on_mouse_up(key, x, y)
        __on_mouse_drag(key, x, y, dx, dy)
        __on_mouse_hover(x, y)
        __on_mouse_click(key, x, y)
        __on_update()
        __on_draw()
    """

    class CaptureInfo:
        widget = None
        key = None
        time = None
        press_pos = None
        last_pos = None

    _capture_info = CaptureInfo()

    def __init__(
        self,
        parent,
        x,
        y,
        width,
        height,
        *,
        is_visible=True,
        is_enabled=True,
        is_key_repeat=False
    ):
        self._parent = None
        self._children = []
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self._is_visible = None
        self._is_enabled = None
        self.is_key_repeat = is_key_repeat
        self._event_handler_lists = {}

        self.parent = parent
        self.is_visible = is_visible
        self.is_enabled = is_enabled

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

        if value and self not in value._children:
            value._children.append(self)

    @property
    def is_visible(self):
        return self._is_visible

    @is_visible.setter
    def is_visible(self, value):
        if self._is_visible == value:
            return

        self._is_visible = value

        if value:
            self.call_event_handler("show")
        else:
            self.call_event_handler("hide")

    @property
    def is_enabled(self):
        return self._is_enabled

    @is_enabled.setter
    def is_enabled(self, value):
        if self._is_enabled == value:
            return

        self._is_enabled = value

        if value:
            self.call_event_handler("enabled")
        else:
            self.call_event_handler("disabled")

    def _get_event_handler_list(self, event):
        if event not in self._event_handler_lists:
            self._event_handler_lists[event] = []

        return self._event_handler_lists[event]

    def add_event_handler(self, event, handler):
        self._get_event_handler_list(event).append(handler)

    def remove_event_handler(self, event, handler):
        self._get_event_handler_list(event).remove(handler)

    def call_event_handler(self, event, *args):
        for handler in self._get_event_handler_list(event):
            handler(*args)

    def is_hit(self, x, y):
        return (
            x >= self.x
            and x < self.x + self.width
            and y >= self.y
            and y < self.y + self.height
        )

    def _capture_mouse(self, key):
        Widget._capture_info.widget = self
        Widget._capture_info.key = key
        Widget._capture_info.time = pyxel.frame_count
        Widget._capture_info.press_pos = (pyxel.mouse_x, pyxel.mouse_y)
        Widget._capture_info.last_pos = Widget._capture_info.press_pos

    def _release_mouse(self):
        Widget._capture_info.widget = None
        Widget._capture_info.key = None
        Widget._capture_info.time = None
        Widget._capture_info.press_pos = None
        Widget._capture_info.last_pos = None

    @staticmethod
    def update(root):
        capture_widget = Widget._capture_info.widget

        if capture_widget:
            capture_widget._process_capture()
        else:
            root._process_input()

        root._update()

    def _process_capture(self):
        capture_info = Widget._capture_info
        last_mx, last_my = capture_info.last_pos

        mx = pyxel.mouse_x
        my = pyxel.mouse_y

        if mx != last_mx or my != last_my:
            self.call_event_handler(
                "mouse_drag", capture_info.key, mx, my, mx - last_mx, my - last_my
            )
            capture_info.last_pos = (mx, my)

        if self.is_key_repeat and pyxel.btnp(
            capture_info.key, WIDGET_HOLD_FRAME, WIDGET_REPEAT_FRAME
        ):
            self.call_event_handler("mouse_down", capture_info.key, mx, my)

        if pyxel.btnr(capture_info.key):
            self.call_event_handler("mouse_up", capture_info.key, mx, my)

            press_x, press_y = capture_info.press_pos
            if (
                pyxel.frame_count <= capture_info.time + WIDGET_CLICK_FRAME
                and abs(pyxel.mouse_x - press_x) <= WIDGET_CLICK_DIST
                and abs(pyxel.mouse_y - press_y) <= WIDGET_CLICK_DIST
            ):
                self.call_event_handler("mouse_click", capture_info.key, mx, my)

            self._release_mouse()

    def _process_input(self):
        if not self._is_visible:
            return False

        if self._is_enabled:
            for widget in reversed(self._children):
                if widget._process_input():
                    return True
        else:
            return False

        mx = pyxel.mouse_x
        my = pyxel.mouse_y

        if self.is_hit(mx, my):
            key = None

            if pyxel.btnp(pyxel.KEY_LEFT_BUTTON):
                key = pyxel.KEY_LEFT_BUTTON
            elif pyxel.btnp(pyxel.KEY_RIGHT_BUTTON):
                key = pyxel.KEY_RIGHT_BUTTON
            elif pyxel.btnp(pyxel.KEY_MIDDLE_BUTTON):
                key = pyxel.KEY_MIDDLE_BUTTON

            if key is not None:
                self._capture_mouse(key)
                self.call_event_handler("mouse_down", key, mx, my)
            else:
                self.call_event_handler("mouse_hover", mx, my)

            return True

        return False

    def _update(self):
        if not self._is_visible:
            return

        self.call_event_handler("update")

        for child in self._children:
            child._update()

    @staticmethod
    def draw(root):
        if not root._is_visible:
            return

        root.call_event_handler("draw")

        for child in root._children:
            Widget.draw(child)
