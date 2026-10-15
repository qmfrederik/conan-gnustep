from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.files import get, copy, mkdir
from conan.tools.build import cross_building
from conan.tools.env import VirtualRunEnv
import os
import shutil

class GnustepWinUXThemeRecipe(ConanFile):
    name = "gnustep-winuxtheme"
    version = "1.0.0"
    if os.getenv("CI"):
        revision_mode = "scm"
    package_type = "application"
    license = "LGPL-2.0-or-later"
    url = "https://github.com/gnustep/plugins-themes-WinUXTheme"
    description = "Win32 native widgets theme for GNUstep."

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"objc_runtime": ["gnu", "ng"]}
    default_options = {"objc_runtime": "ng"}
    python_requires = "gnustep-helpers/0.2"

    def set_version(self):
        self.version = self.python_requires["gnustep-helpers"].module.get_package_version(self)

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("WinUXTheme is only supported on Windows")

    def source(self):
        get(self, **sorted(self.conan_data["sources"].values())[0])

    def requirements(self):
        self.requires("gnustep-gui/[^0.32.0]")
        self.tool_requires("gnustep-make/[^2.9.3]")

    def build_requirements(self):
        # Require a MSYS2 shell on Windows (for GNU make)
        self.python_requires["gnustep-helpers"].module.windows_build_requirements(self)

    def generate(self):
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        env = tc.environment()

        self.python_requires["gnustep-helpers"].module.configure_windows_pkgconf(self, env)

        tc.generate(env)

        deps = PkgConfigDeps(self)
        deps.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        # There is no configure script; the GNUmakefile builds the bundle directly.
        autotools = Autotools(self)
        autotools.make()

    def package(self):
        # Copy the bundle from the build folder; "make install" would place it under the
        # fully qualified GNUstep prefix of the gnustep-make package.
        # GNUstep resolves themes in $GNUSTEP_SYSTEM_LIBRARY/Themes, which gnustep-base locates at lib/GNUstep.
        copy(self, "*",
             src=os.path.join(self.build_folder, "WinUXTheme.theme"),
             dst=os.path.join(self.package_folder, "lib", "GNUstep", "Themes", "WinUXTheme.theme"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []
