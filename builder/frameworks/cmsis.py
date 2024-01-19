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

"""
CMSIS

The ARM Cortex Microcontroller Software Interface Standard (CMSIS) is a
vendor-independent hardware abstraction layer for the Cortex-M processor
series and specifies debugger interfaces. The CMSIS enables consistent and
simple software interfaces to the processor for interface peripherals,
real-time operating systems, and middleware. It simplifies software
re-use, reducing the learning curve for new microcontroller developers
and cutting the time-to-market for devices.

http://www.arm.com/products/processors/cortex-m/cortex-microcontroller-software-interface-standard.php
"""

import glob
import os
import string

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()
mcu = board.get("build.mcu", "")

env.SConscript("_bare.py")

CMSIS_DIR = platform.get_package_dir("framework-cmsis-gr551x")
assert os.path.isdir(CMSIS_DIR)

def get_linker_script():
    script = ""
    if "gr5515" in mcu.lower():
        script = "gcc_linker_gr5515.lds"
    else:
        script = "gcc_linker_gr5513.lds"
    default_ldscript = os.path.join(CMSIS_DIR, "soc", "linker", "gcc", script)
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

#
# Prepare build environment
#

# The final firmware is linked against standard library with two specifications:
# nano.specs - link against a reduced-size variant of libc
# nosys.specs - link against stubbed standard syscalls

env.Append(
    CPPPATH=[
        os.path.join(CMSIS_DIR, "cmsis", "core", "include"),
        os.path.join(CMSIS_DIR, "soc", "include"),
        "$PROJECT_SRC_DIR"
    ],

    LINKFLAGS=[
        "--specs=nano.specs",
        "--specs=nosys.specs",
        os.path.join(CMSIS_DIR, "soc", "linker", "gcc", "rom_symbol_gcc.txt")
    ]
)

#
# Compile CMSIS sources
#

prepare_startup_file(os.path.join(CMSIS_DIR, "soc", "linker"))

env.BuildSources(
    os.path.join("$BUILD_DIR", "FrameworkCMSIS"), 
    os.path.join(CMSIS_DIR),
    src_filter = [
        "-<*>",
        "+<gcc/>",
        "+<soc/common/gr_system.c>",
        "+<soc/common/gr_platform.c>",
        "+<soc/src/gr_soc.c>",
    ]
)