import os
import platform

from conans import ConanFile, CMake, tools


class AndroidtoolchainConan(ConanFile):
    name = "android-toolchain"
    version = "r13b"
    license = "GPL/APACHE2"
    url = ""
    settings = "os", "arch", "compiler"
    options = {"use_system_python": [True, False]}
    default_options = "use_system_python=True"
    requires = "android-ndk/%s@lasote/testing" % version
    description = "Recipe for building an Android toolchain for cross compile Android apps from Windows/Linux/OSX"

    def configure(self):
        if self.settings.os != "Android":
            raise Exception("Only os Android supported")
        if str(self.settings.compiler) not in ("gcc", "clang"):
            raise Exception("Not supported compiler, gcc and clang available")
        if str(self.settings.compiler) == "gcc" and str(self.settings.compiler.version) not in ("4.8", "4.9"):
            raise Exception("Not supported gcc compiler version, 4.8 and 4.9 available")
        if str(self.settings.compiler) == "clang" and str(self.settings.compiler.version) != "3.8":
            raise Exception("Not supported clang compiler version, only 3.8 available")

    @property
    def arch_id_str(self):

        return {"x86": "i686",
                "armv6": "arm",
                "armv7": "arm",
                "armv7hf": "arm",
                "armv8": "aarch64",
                "mips64": "mips64"}.get(str(self.info.settings.arch),
                                        str(self.info.settings.arch))

    @property
    def android_id_str(self):
        return "androideabi" if str(self.info.settings.arch) in ["armv6", "armv7"] else "android"

    def build(self):

        compiler_str = {"clang": "clang", "gcc": ""}.get(str(self.settings.compiler))
        toolchain = "%s-linux-%s-%s%s" % (self.arch_id_str, self.android_id_str, compiler_str, self.settings.compiler.version)
        # Command available in android-ndk package
        # --stl => gnustl, libc++, stlport
        stl = {"libstdc++": "gnustl", "libstdc++11": "gnustl", "libc++": "libc++"}.get(str(self.settings.compiler.libcxx))
        command = "make-standalone-toolchain.sh --toolchain=%s --platform=android-%s " \
                  "--install-dir=%s --stl=%s" % (toolchain, self.settings.os.api_level, self.package_folder, stl)
        self.output.warn(command)
        # self.run("make-standalone-toolchain.sh --help")
        self.run(command)
        if self.options.use_system_python:
            if os.path.exists(os.path.join(self.package_folder, "bin", "python")):
                os.unlink(os.path.join(self.package_folder, "bin", "python"))

        if not os.path.exists(os.path.join(self.package_folder, "bin")):
            raise Exception("Invalid toolchain, try a higher api_level or different architecture: %s-%s" % (self.settings.arch, self.settings.os.api_level))

    def package_info(self):
        host_os = platform.system().lower()
        prename = "%s-%s-%s-" % (self.arch_id_str, host_os, self.android_id_str)
        if self.settings.compiler == "gcc":
            cc_compiler = prename + "gcc"
            cxx_compiler = prename + "g++"
        else:
            cc_compiler = "clang"
            cxx_compiler = "clang++"

        sysroot = os.path.join(self.package_folder, "sysroot")
        self.env_info.CC = cc_compiler
        self.env_info.CXX = cxx_compiler

        self.env_info.CONAN_CMAKE_FIND_ROOT_PATH = sysroot
        self.env_info.PATH.extend([os.path.join(self.package_folder, onedir) for onedir in self.cpp_info.bindirs])

        arch = {"armv8": "armv8-a", "armv7": "armv7-a"}.get(str(self.settings.arch), self.settings.arch)

        # valid arguments to '-march=' are: armv2 armv2a armv3 armv3m armv4 armv4t armv5 armv5e armv5t armv5te
        # armv6 armv6-m armv6j armv6k armv6s-m armv6t2 armv6z armv6zk armv7 armv7-a armv7-m armv7-r armv7e-m armv7ve
        # armv8-a armv8-a+crc iwmmxt iwmmxt2 native

        arch_flag = "-march=%s" % arch if ("arm" in str(arch)) else ""

        # Common flags to C, CXX and LINKER
        flags = ["-fPIE"]
        if self.settings.compiler == "clang":
            flags.append("--gcc-toolchain=%s" % self.package_folder)
            flags.append("-target %s-linux-android" % arch)
            flags.append("-D_GLIBCXX_USE_CXX11_ABI=0")
        else:
            flags.append("-pie")

        if self.settings.arch == "armv7":
            flags.append("-mfloat-abi=softfp -mfpu=vfpv3-d16")

        self.cpp_info.cflags.extend(flags)
        self.cpp_info.cflags.append(arch_flag)
        self.cpp_info.sharedlinkflags.extend(flags)
        self.cpp_info.exelinkflags.extend(flags)
        self.cpp_info.sysroot = sysroot

