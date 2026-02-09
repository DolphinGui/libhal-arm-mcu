#!/usr/bin/python
#
# Copyright 2024 - 2025 Khalil Estell and the libhal contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from conan import ConanFile
from conan.tools.cmake import CMakeDeps, CMakeToolchain
from conan.tools.env import VirtualBuildEnv
from conan.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=2.0.14"


class libhal_arm_mcu_conan(ConanFile):
    name = "libhal-arm-mcu"
    license = "Apache-2.0"
    homepage = "https://github.com/libhal/libhal-arm-mcu"
    description = ("A collection of libhal drivers and libraries for the "
                   "Cortex M series ARM processors and microcontrollers.")
    topics = ("arm", "cortex", "cortex-m", "cortex-m0", "cortex-m0plus",
              "cortex-m1", "cortex-m3", "cortex-m4", "cortex-m4f", "cortex-m7",
              "cortex-m23", "cortex-m55", "cortex-m35p", "cortex-m33", "lpc",
              "lpc40", "lpc40xx", "lpc4072", "lpc4074", "lpc4078", "lpc4088",
              "stm32f1", "stm32f103")
    settings = "compiler", "build_type", "os", "arch"

    python_requires = "libhal-bootstrap/[>=4.3.0 <5]"
    python_requires_extend = "libhal-bootstrap.library"

    options = {
        "use_libhal_exceptions": [True, False],
        "use_picolibc": [True, False],
        "platform": ["ANY"],
        "use_default_linker_script": [True, False],
        "variant": [None, "ANY"],
        "board": [None, "ANY"],
        "rp_header_only": [True, False],
        "rp_link_type": [None, "no_flash", "blocked_ram", "copy_to_ram"]
    }

    default_options = {
        "use_libhal_exceptions": True,
        "use_picolibc": True,
        "platform": "ANY",
        "use_default_linker_script": True,
        "variant": None,
        "board": None,
        "rp_header_only": False,
        "rp_link_type": None,
    }

    def requirements(self):
        self.requires("libhal/[^4.18.0]", transitive_headers=True)
        self.requires("libhal-util/[^5.7.0]", transitive_headers=True)
        self.requires("ring-span-lite/[^0.7.0]", transitive_headers=True)
        self.requires("scope-lite/0.2.0")

        if self.settings.os == "baremetal" and self.settings.compiler == "gcc":
            if self.options.use_libhal_exceptions:
                self.requires(
                    "libhal-exceptions/[^1.1.1]", transitive_headers=True)
            if self.options.use_picolibc:
                compiler_version = str(self.settings.compiler.version)
                self.requires("prebuilt-picolibc/" + compiler_version)
        if str(self.options.platform).startswith("rp2"):
            self.requires("picosdk/2.2.0")
            self.tool_requires("pioasm/2.2.0")

    def _macro(self, string):
        return string.upper().replace("-", "_")

    def generate(self):
        virt = VirtualBuildEnv(self)
        virt.generate()
        tc = CMakeToolchain(self)
        if str(self.options.platform).startswith("rp2"):
            tc.cache_variables["PICO_BOARD"] = str(self.options.board)
            tc.cache_variables["ONLY_INCLUDE_PICO_HEADERS"] =  self.options.rp_header_only
            tc.cache_variables["PICO_DEFAULT_BINARY_TYPE"] = self.options.rp_link_type or "default"
        if self.options.variant:
            tc.preprocessor_definitions["LIBHAL_VARIANT_" + self._macro(str(self.options.variant))] = "1"
        tc.preprocessor_definitions["LIBHAL_PLATFORM_" + self._macro(str(self.options.platform))] = "1"
        tc.generate()
        cmake = CMakeDeps(self)
        cmake.generate()

    def validate(self):
        if str(self.options.platform).startswith("rp2"):
            if self.options.board is None:
                raise ConanInvalidConfiguration("Must specify a board for picosdk")
            if "rp2350" in str(self.options.platform):
                if not self.options.variant:
                    raise ConanInvalidConfiguration("RP2350 variant not specified")
                if self.options.variant not in ["rp2350a", "rp2350b"]:
                    raise ConanInvalidConfiguration("Invalid RP2350 variant specified")
        super().validate()

    def package_info(self):
        core = self.cpp_info.components["arm-mcu"]
        core.libs = ["libhal-arm-mcu"]
        core.set_property("cmake_target_name", "libhal::arm-mcu")
        core.set_property("cmake_target_aliases", [
            "libhal::lpc40",
            "libhal::stm32f1",
            "libhal::stm32f4",
            "libhal::rp2350"
        ])
        core.exelinkflags = []
        core.requires = ["libhal::libhal","libhal-util::libhal-util", 
        "ring-span-lite::ring-span-lite", 
        "scope-lite::scope-lite"]

        platform = str(self.options.platform)
        self.buildenv_info.define("LIBHAL_PLATFORM", platform)
        self.buildenv_info.define("LIBHAL_PLATFORM_LIBRARY", "arm-mcu")
        if str(self.options.platform).startswith("rp2"):
            core.requires += ["picosdk::picosdk"]
            defines = []
            if self.options.variant:
                defines.append("LIBHAL_VARIANT_" + self._macro(str(self.options.variant)) + "=1")
            defines.append("LIBHAL_PLATFORM_" + self._macro(str(self.options.platform)) + "=1")
            core.defines = defines
            for iotype in "usb", "uart", "rtt", "semihosting":
              self.cpp_info.components[f"rp-stdio-{iotype}"].set_property("cmake_target_name", f"libhal::rp-stdio-{iotype}")
              self.cpp_info.components[f"rp-stdio-{iotype}"].libs = [f"rp-stdio-{iotype}"]
              self.cpp_info.components[f"rp-stdio-{iotype}"].requires = ["picosdk::picosdk"]

        if (self.settings.os == "baremetal" and
                self.options.use_default_linker_script):
            core.requires += ["libhal-exceptions::libhal-exceptions", "prebuilt-picolibc::prebuilt-picolibc"]
            # If the platform matches the linker script, just use that linker
            # script
            core.exelinkflags = [
                "-L" + os.path.join(self.package_folder, "linker_scripts")]

            full_linker_path = os.path.join(
                self.package_folder, "linker_scripts", platform + ".ld")
            # if the file exists, then we should use it as the linker
            if os.path.isfile(full_linker_path):
                self.output.info(f"linker file '{full_linker_path}' found!")
                core.exelinkflags.append("-T" + platform + ".ld")

            # if there is no match, then the linker script could be a pattern
            # based on the name of the platform
            else:
                self.append_linker_using_platform(platform)

    def package_id(self):
        self.info.python_requires.major_mode()
        del self.info.options.use_picolibc
        del self.info.options.use_libhal_exceptions
        del self.info.options.platform
        del self.info.options.use_default_linker_script

    def append_linker_using_platform(self, platform: str):
        if platform.startswith("stm32f1"):
            linker_script_name = list(str(self.options.platform))
            # Replace the MCU number and pin count number with 'x' (don't care)
            # to map to the linker script
            linker_script_name[8] = 'x'
            linker_script_name[9] = 'x'
            linker_script_name = "".join(linker_script_name)
            self.cpp_info.components["arm-mcu"].exelinkflags.append(
                "-T" + linker_script_name + ".ld")
        elif platform.startswith("rp"):
            self.cpp_info.components["arm-mcu"].exelinkflags.append(
                "-Trpdefault.ld")
        # Add additional script searching queries here
