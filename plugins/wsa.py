from ast import Raise
import io
import logging
import re
import time
import auto_derby
import PIL.Image
from auto_derby.clients import ADBClient
from typing import Tuple

LOGGER = logging.getLogger(__name__)

class WSAClient(ADBClient):
    """A adb client variant that works with WSA."""
    def load_size(self):
        display_string = self.device.shell(
            f"dumpsys display",
            decode=True,
            transport_timeout_s=None,
        )
        display_data = re.findall(
            "^\\s+mUniqueId=(\\w+):(?:(?:(?:\\w+\\.?)+):((?:\\w+\\.?)+):)?(\\d+)$",
            display_string,
            re.MULTILINE,
        )
        display_id = [
            item
            for item in display_data
            if item[0] == "virtual" and item[1] == "jp.co.cygames.umamusume"
        ]
        self._wsa = None
        if len(display_id) == 0:
            self._display_param = ""
            LOGGER.info(
                "wsa display: No Umamusume opened."
            )
        else:
            self._wsa = True
            LOGGER.info(
                "wsa display: UniqueId=%s:%s:%s",
                display_id[0][0],
                display_id[0][1],
                display_id[0][2],
            )
        self._display_param = f"-d {display_id[0][2]}"
        res = self.device.shell(f"wm size {self._display_param}")
        match = re.match(r"Physical size: (\d+)x(\d+)", res)
        assert match, "unexpected command result: %s" % res
        self._width = int(match.group(2))
        self._height = int(match.group(1))
        if self._width > self._height:
            # handle orientation
            self._height, self._width = self._width, self._height
        self._resize = None
        # WORKAROUND: near 16:9 screen size in WSA
        if (
            len(self._display_param) != 0
            and abs(self._width / self._height - 0.5625) < 0.005
        ):
            self._resize = True
            self._width = int(self._height / 16 * 9)
        LOGGER.debug("screen size: width=%d height=%d", self.width, self.height)

    def _screenshot_png(self) -> PIL.Image.Image:
        img_data = self.device.shell(
            f"screencap {self.display_param} -p",
            decode=False,
            transport_timeout_s=None,
        )
        img = PIL.Image.open(io.BytesIO(img_data))
        return img

    def _screenshot_raw(self) -> PIL.Image.Image:
        # https://stackoverflow.com/a/59470924
        img_data = self.device.shell(
            f"screencap {self.display_param}",
            decode=False,
            transport_timeout_s=None,
        )
        width = int.from_bytes(img_data[0:4], "little")
        height = int.from_bytes(img_data[4:8], "little")
        pixel_format = int.from_bytes(img_data[8:12], "little")
        # https://developer.android.com/reference/android/graphics/PixelFormat#RGBA_8888
        assert pixel_format == 1, "unsupported pixel format: %s" % pixel_format
        img = PIL.Image.frombuffer(
            "RGBA", (width, height), img_data[12:], "raw", "RGBX", 0, 1
        ).convert("RGBA")
        return img
        
    def screenshot(self) -> PIL.Image.Image:
        if not self._resize and not self._wsa:
            return self._screenshot()
        # WORKAROUND: strange bugged screenshot from WSA
        if self._wsa:
            while True:
                img = self._screenshot()
                output = io.BytesIO()
                img.save(output, "PNG")  # a format needs to be provided
                contents = output.getvalue()
                output.close()
                size = len(contents)
                if size > 100000:
                    break
                LOGGER.debug("screenshot seems failed: filesize=%d", size)
        else:
            img = self._screenshot()
        if self._resize:
            img = img.resize((self.width, self.height))
        return img


    def swipe(
        self, point: Tuple[int, int], *, dx: int, dy: int, duration: float
    ) -> None:
        x1, y1 = point
        x2, y2 = x1 + dx, y1 + dy
        duration_ms = int(duration * 1e3)
        duration_ms = max(200, duration_ms)  # not work if too fast
        command = f"input {self._display_param} swipe {x1} {y1} {x2} {y2} {duration_ms}"
        LOGGER.debug("swipe: %s", command)
        res = self.device.shell(
            command,
            read_timeout_s=10 + duration,
        )
        assert not res, res
        time.sleep(self.action_wait)



class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        _next_client = auto_derby.config.client

        def _client():
            auto_derby.config.ADB_ADDRESS = "127.0.0.1:58526"
            return WSAClient(auto_derby.config.ADB_ADDRESS)

        auto_derby.config.client = _client


auto_derby.plugin.register(__name__, Plugin())
