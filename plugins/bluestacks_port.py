import logging
import time
from typing import Text, Tuple

import PIL
import adb_shell
import auto_derby
from auto_derby.clients import ADBClient
from adb_shell.adb_device import AdbDeviceTcp
import re

LOGGER = logging.getLogger(__name__)


class BlueStacksClient(ADBClient):
    def __init__(self, address: Text):
        hostname, instance, conf_path = address.split(":", 2)
        if len(instance) == 0:
            instance = "Nougat64"
        if len(conf_path) == 0:
            conf_path = "C:\\ProgramData\\BlueStacks_nxt\\bluestacks.conf"
        with open(conf_path, encoding="utf-8") as conf:
            for line in conf:
                re_match = re.match(
                    'bst\.instance\.%s\.status\.adb_port="(?P<port>\d{2,5})"'
                    % instance,
                    line,
                )
                if re_match != None:
                    break
        assert hostname, "invalid address: missing hostname: %s" % address
        assert re_match.group("port"), "invalid port: missing port: %s" % address
        port = re_match.group("port")

        LOGGER.info("BlueStacks Port: hostname=%s port=%s" % (hostname, port))

        self.hostname = hostname
        self.port = int(port)
        self.device = AdbDeviceTcp(self.hostname, self.port)
        self._height, self._width = 0, 0
        self._screenshot = self._screenshot_init

    def screenshot(self) -> PIL.Image.Image:
        while True:
            try:
                screenshot = self._screenshot()
                break
            except adb_shell.exceptions.TcpTimeoutException:
                LOGGER.info("Timeout")
                time.sleep(5)
                self.connect()
        return screenshot

    def tap(self, point: Tuple[int, int]) -> None:
        while True:
            try:
                super().tap(point)
                break
            except adb_shell.exceptions.TcpTimeoutException:
                LOGGER.info("Timeout")
                time.sleep(5)
                self.connect()

    def swipe(
        self, point: Tuple[int, int], *, dx: int, dy: int, duration: float
    ) -> None:
        while True:
            try:
                super().swipe(point, dx=dx, dy=dy, duration=duration)
                break
            except adb_shell.exceptions.TcpTimeoutException:
                LOGGER.info("Timeout")
                time.sleep(5)
                self.connect()


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        _next_client = auto_derby.config.client

        def _client():
            if not auto_derby.config.ADB_ADDRESS:
                return _next_client()
            return BlueStacksClient(auto_derby.config.ADB_ADDRESS)

        auto_derby.config.client = _client


auto_derby.plugin.register(__name__, Plugin())
