# Copyright 2024-present Maximilian Gerhardt <maximilian.gerhardt@rub.de>
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

"""
GR551x SDK

GR551x SDK supports full functionality of Bluetooth Low Energy (Bluetooth LE) 
Stack (Bluetooth 5.1), and provides a complete set of peripheral drivers, as
well as various library files. It includes a rich set of reference files and
examples on Bluetooth LE device roles, GATT profiles", "services, peripheral
APP/HAL drivers, libraries, OTA, DTM, power consumption, FreeRTOS, etc.

https://www.goodix.com/en/software_tool/gr551x_sdk
"""

import os

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()
mcu = board.get("build.mcu", "")

env.SConscript("_bare.py")

FRAMEWORK_DIR = platform.get_package_dir("framework-goodix-gr551x-sdk")
assert os.path.isdir(FRAMEWORK_DIR)

def get_linker_script():
    script = ""
    if "gr5515" in mcu.lower():
        script = "gcc_linker_gr5515.lds"
    else:
        script = "gcc_linker_gr5513.lds"
    default_ldscript = os.path.join(FRAMEWORK_DIR, "platform", "soc", "linker", "gcc", script)
    return default_ldscript


def prepare_startup_file(src_path):
    startup_file = os.path.join(src_path, "gcc", "startup_gr55xx.s")
    # Change file extension to uppercase:
    if not os.path.isfile(startup_file) and os.path.isfile(startup_file[:-2] + ".s"):
        os.rename(startup_file[:-2] + ".s", startup_file)
    if not os.path.isfile(startup_file):
        print("Warning! Cannot find the default startup file for %s. "
              "Ignore this warning if the startup code is part of your project." % mcu)


#
# Allow using custom linker scripts
#

if not board.get("build.ldscript", ""):
    env.Replace(LDSCRIPT_PATH=get_linker_script())

env.Append(
    # Add same include folders as Makefile
    CPPPATH=[
        # os.path.join(FRAMEWORK_DIR, "components", "boards"),
        os.path.join(FRAMEWORK_DIR, "components", "drivers_ext", "gr55xx"),
        os.path.join(FRAMEWORK_DIR, "components", "drivers_ext", "st7735"),
        # os.path.join(FRAMEWORK_DIR, "components", "drivers_ext", "vs1005"),
        os.path.join(FRAMEWORK_DIR, "components", "libraries", "app_alarm"),
        os.path.join(FRAMEWORK_DIR, "components", "libraries", "app_assert"),
        os.path.join(FRAMEWORK_DIR, "components", "libraries", "app_error"),
        os.path.join(FRAMEWORK_DIR, "components", "libraries", "app_key"),
        os.path.join(FRAMEWORK_DIR, "components", "libraries", "app_log"),
        os.path.join(FRAMEWORK_DIR, "components", "libraries", "app_queue"),
        os.path.join(FRAMEWORK_DIR, "components", "libraries", "app_timer"),
        os.path.join(FRAMEWORK_DIR, "components", "libraries", "at_cmd"),
        os.path.join(FRAMEWORK_DIR, "components", "libraries", "dfu_master"),
        os.path.join(FRAMEWORK_DIR, "components", "libraries", "dfu_port"),
        os.path.join(FRAMEWORK_DIR, "components", "libraries", "gui"),
        os.path.join(FRAMEWORK_DIR, "components", "libraries", "gui/gui_config"),
        os.path.join(FRAMEWORK_DIR, "components", "libraries", "hal_flash"),
        os.path.join(FRAMEWORK_DIR, "components", "libraries", "hci_uart"),
        os.path.join(FRAMEWORK_DIR, "components", "libraries", "pmu_calibration"),
        os.path.join(FRAMEWORK_DIR, "components", "libraries", "ring_buffer"),
        os.path.join(FRAMEWORK_DIR, "components", "libraries", "sensorsim"),
        # os.path.join(FRAMEWORK_DIR, "components", "libraries", "bsp"),
        os.path.join(FRAMEWORK_DIR, "components", "libraries", "fault_trace"),
        os.path.join(FRAMEWORK_DIR, "components", "libraries", "utility"),
        # os.path.join(FRAMEWORK_DIR, "components", "patch", "ind"),
        os.path.join(FRAMEWORK_DIR, "components", "sdk"),
        os.path.join(FRAMEWORK_DIR, "external", "freertos", "include"),
        os.path.join(FRAMEWORK_DIR, "external", "freertos", "portable", "GCC", "ARM_CM4F"),
        os.path.join(FRAMEWORK_DIR, "drivers", "inc"),
        os.path.join(FRAMEWORK_DIR, "platform", "boards"),
        os.path.join(FRAMEWORK_DIR, "platform", "include"),
        os.path.join(FRAMEWORK_DIR, "platform", "soc", "include"),
        os.path.join(FRAMEWORK_DIR, "platform", "arch", "arm", "cortex-m", "cmsis", "core", "include"),
        # os.path.join(FRAMEWORK_DIR, "components", "app_drivers", "inc"),
        os.path.join(FRAMEWORK_DIR, "drivers", "inc", "hal"),
        # project folder's src dir will likely have custom_config.h
        # so we add this to the global include path for the SDK build.
        "$PROJECT_SRC_DIR"
    ],
    # C only flags. Set standard
    CFLAGS=[
        "-std=gnu99"
    ],
    # C++ only flags. C++ is unused mostly. 
    CXXFLAGS=[
        "-std=gnu++14"
    ],
    # Flags for both C and C++
    CCFLAGS=[
        "--inline",
        # reduce spam from buggy SDK
        "-Wno-attributes",
        "-Wno-strict-aliasing"
    ],
    # So that libble_sdk.a is found, must be in the library search path
    LIBPATH=[
        os.path.join(FRAMEWORK_DIR, "platform", "soc", "linker", "gcc")
    ],
    # link in ble_sdk
    LIBS=[
        "ble_sdk"
    ],
    # leverage PlatformIO's library system to dynamically detect dependencies on optional
    # components.
    LIBSOURCE_DIRS=[
        os.path.join(FRAMEWORK_DIR, "components", "libraries"),
        os.path.join(FRAMEWORK_DIR, "components", "drivers_ext"),
        os.path.join(FRAMEWORK_DIR, "components", "profiles"),
        # contain FreeRTOS, Segger
        os.path.join(FRAMEWORK_DIR, "external")
    ],
    LINKFLAGS=[
        # reduces firmware size thanks to leightweight C-library
        "--specs=nano.specs",
        "--specs=nosys.specs",
        # has file with all ROM symbols and their address, mandatory
        os.path.join(FRAMEWORK_DIR, "platform", "soc", "linker", "gcc", "rom_symbol_gcc.txt")
    ]
)

prepare_startup_file(os.path.join(FRAMEWORK_DIR, "platform", "arch", "arm", "cortex-m"))

# build SoC base files
env.BuildSources(
    os.path.join("$BUILD_DIR", "FrameworkSDKSoC"), 
    os.path.join(FRAMEWORK_DIR, "platform", "soc"),
)

# default: just build all drivers.
env.BuildSources(
    os.path.join("$BUILD_DIR", "FrameworkSDKDrivers"), 
    os.path.join(FRAMEWORK_DIR, "drivers")
)
# for starter board
env.BuildSources(
    os.path.join("$BUILD_DIR", "FrameworkSDKBoards"), 
    os.path.join(FRAMEWORK_DIR, "platform", "boards")
)
# Makefile always builds Segger RTT files
env.BuildSources(
    os.path.join("$BUILD_DIR", "FrameworkSDKSegger"), 
    os.path.join(FRAMEWORK_DIR, "external", "segger_rtt")
)

# Various fixups: Set library dependency finder to "deep+" so it can find most libs
env_section = "env:" + env["PIOENV"]
platform.config.set(env_section, "lib_ldf_mode", "deep+")

# Automatically add some needed base libs
builtin_libs = [
    "pmu_calibration", # gr_soc.c depends on this
    "ring_buffer", # multiple drivers depend on this
    "app_key" # SK board depends on this
]
prev_libs = platform.config.get(env_section, "lib_deps", [])
for l in builtin_libs:
    if l not in prev_libs:
        prev_libs.append(l)
platform.config.set(env_section, "lib_deps", prev_libs)
