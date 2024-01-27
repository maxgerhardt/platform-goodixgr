# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import subprocess

from platformio.managers.platform import PlatformBase
from platformio import util

IS_WINDOWS = sys.platform.startswith("win")

class GoodixgrPlatform(PlatformBase):
    gprogrammer_pkg = {
        # Windows
        "windows_amd64": "https://github.com/maxgerhardt/pio-tool-goodix-gprogrammer.git#windows",
        "windows_x86": "https://github.com/maxgerhardt/pio-tool-goodix-gprogrammer.git#windows",
        # No Windows ARM64 or ARM32 builds.
        # Linux
        "linux_x86_64": "https://github.com/maxgerhardt/pio-tool-goodix-gprogrammer.git#linux",
        #"linux_i686": "",
        #"linux_aarch64": "",
        #"linux_armv7l": "",
        #"linux_armv6l": "",
        # Mac (Intel and ARM)
        #"darwin_x86_64": "",
        #"darwin_arm64": ""
    }

    def configure_default_packages(self, variables, targets):
        board = variables.get("board")
        board_config = self.board_config(board)
        build_mcu = variables.get("board_build.mcu", board_config.get("build.mcu", ""))
        sys_type = util.get_systype()

        frameworks = variables.get("pioframework", [])
        if "cmsis" in frameworks:
            assert build_mcu, ("Missing MCU field for %s" % board)
            device_package = "framework-cmsis-" + build_mcu[0:len("gr551")] + "x"
            if device_package in self.packages:
                self.packages[device_package]["optional"] = False

        # configure J-LINK tool
        jlink_conds = [
            "jlink" in variables.get(option, "")
            for option in ("upload_protocol", "debug_tool")
        ]
        if board:
            jlink_conds.extend([
                "jlink" in board_config.get(key, "")
                for key in ("debug.default_tools", "upload.protocol")
            ])
        jlink_pkgname = "tool-jlink"
        if not any(jlink_conds) and jlink_pkgname in self.packages:
            del self.packages[jlink_pkgname]

        # Activate programmer package if needed, otherwise disable    
        # This is either the explicitly set upload_protocol or the default upload protocol of the board
        upload_protocol = variables.get("upload_protocol", board_config.get("upload.protocol", ""))
        # set the package version if we may be using the uploader due to the upload protocol.
        # but only if we also have a pacakge for it. Otherwise, don't attempt to install it. 
        if "gprogrammer" in upload_protocol and sys_type in GoodixgrPlatform.gprogrammer_pkg:
            self.packages["tool-goodix-gprogrammer"]["version"] = GoodixgrPlatform.gprogrammer_pkg[sys_type] 
            self.packages["tool-goodix-gprogrammer"]["optional"] = False
        else:
            # prevent installation of tool for platforms that don't support it.
            del self.packages["tool-goodix-gprogrammer"]

        return PlatformBase.configure_default_packages(self, variables,
                                                       targets)

    def get_boards(self, id_=None):
        result = PlatformBase.get_boards(self, id_)
        if not result:
            return result
        if id_:
            return self._add_default_debug_tools(result)
        else:
            for key, value in result.items():
                result[key] = self._add_default_debug_tools(result[key])
        return result

    def _add_default_debug_tools(self, board):
        debug = board.manifest.get("debug", {})
        upload_protocols = board.manifest.get("upload", {}).get(
            "protocols", [])
        if "tools" not in debug:
            debug["tools"] = {}

        # BlackMagic, J-Link, ST-Link
        for link in ("blackmagic", "jlink"):
            if link not in upload_protocols or link in debug["tools"]:
                continue
            if link == "blackmagic":
                debug["tools"]["blackmagic"] = {
                    "hwids": [["0x1d50", "0x6018"]],
                    "require_debug_port": True
                }
            elif link == "jlink":
                assert debug.get("jlink_device"), (
                    "Missed J-Link Device ID for %s" % board.id)
                debug["tools"][link] = {
                    "server": {
                        "package": "tool-jlink",
                        "arguments": [
                            "-singlerun",
                            "-if", "SWD",
                            "-select", "USB",
                            "-device", debug.get("jlink_device"),
                            "-port", "2331"
                        ],
                        "executable": ("JLinkGDBServerCL.exe"
                                       if IS_WINDOWS else
                                       "JLinkGDBServer")
                    }
                }
            debug["tools"][link]["onboard"] = link in debug.get("onboard_tools", [])
            debug["tools"][link]["default"] = link in debug.get("default_tools", [])

        board.manifest["debug"] = debug
        return board

    def configure_debug_session(self, debug_config):
        if debug_config.speed:
            server_executable = (debug_config.server or {}).get("executable", "").lower()
            if "jlink" in server_executable:
                debug_config.server["arguments"].extend(
                    ["-speed", debug_config.speed]
                )