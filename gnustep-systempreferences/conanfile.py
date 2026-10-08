from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.files import get, copy, mkdir, apply_conandata_patches
from conan.tools.build import cross_building
from conan.tools.env import VirtualRunEnv
import os
import shutil

class GnustepSystemPreferencesRecipe(ConanFile):
    name = "gnustep-systempreferences"
    version = "1.2.1"
    if os.getenv("CI"):
        revision_mode = "scm"
    package_type = "application"
    license = "GPL-2.0-or-later"
    url = "https://github.com/gnustep/apps-systempreferences"
    description = "System Preferences application and PreferencePanes framework for GNUstep."

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"objc_runtime": ["gnu", "ng"]}
    default_options = {"objc_runtime": "ng"}
    exports_sources = "*.patch"
    python_requires = "gnustep-helpers/0.1"

    def set_version(self):
        self.version = self.python_requires["gnustep-helpers"].module.get_package_version(self)

    def source(self):
        get(self, **sorted(self.conan_data["sources"].values())[0])
        apply_conandata_patches(self)

    def requirements(self):
        self.requires("gnustep-gui/[^0.32.0]")
        self.tool_requires("gnustep-make/[^2.9.3]")

    def build_requirements(self):
        # Require a MSYS2 shell on Windows (for GNU make)
        self.python_requires["gnustep-helpers"].module.windows_build_requirements(self)

    def get_package_folder(self, package_name, folder_path):
        full_folder_path = os.path.join(self.dependencies[package_name].package_folder, folder_path)

        if self.settings.os == "Windows":
            full_folder_path = full_folder_path.replace('\\','/')
            full_folder_path = full_folder_path.replace('C:','/c')

        return full_folder_path

    def generate(self):
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        env = tc.environment()

        # Merge the makefiles of gnustep-make, gnustep-base and gnustep-gui into a single directory
        # (see gnustep-gui for details).
        build_makefiles = os.path.join(self.build_folder, "build/Makefiles")
        mkdir(self, build_makefiles)
        shutil.copytree(os.path.join(self.dependencies.build["gnustep-make"].package_folder, "share/GNUstep/Makefiles"), build_makefiles, dirs_exist_ok=True)
        shutil.copytree(os.path.join(self.dependencies["gnustep-base"].package_folder, "share/GNUstep/Makefiles"), build_makefiles, dirs_exist_ok=True)
        shutil.copytree(os.path.join(self.dependencies["gnustep-gui"].package_folder, "share/GNUstep/Makefiles"), build_makefiles, dirs_exist_ok=True)

        if self.settings.os == "Windows":
            build_makefiles = build_makefiles.replace('\\','/').replace('C:','/c')
        tc.make_args.append(f"GNUSTEP_MAKEFILES={build_makefiles}")

        # The headers are spread over several packages, so be explicit about the include paths.
        # clang reads OBJC_INCLUDE_PATH directly, so it needs native paths (no MSYS conversion).
        includes = [os.path.join(self.dependencies[dep].package_folder, "include") for dep in ("gnustep-base", "gnustep-gui", "libobjc2")]
        separator = ";" if self.settings.os == "Windows" else ":"
        tc.make_args.append(f"OBJC_INCLUDE_PATH='{separator.join(includes)}'")

        ldflags = f"-L{self.get_package_folder('gnustep-base', 'lib/')} -L{self.get_package_folder('gnustep-gui', 'lib/')}"
        if self.options.objc_runtime == "ng":
            ldflags += f" -L{self.get_package_folder('libdispatch', 'lib/')} -L{self.get_package_folder('libobjc2', 'lib/')}"
        if self.settings.os == "Windows":
            # gnustep-make names a framework's import library libPreferencePanes.dll.lib, but clang resolves
            # -lPreferencePanes to PreferencePanes.lib, so rename it and let the modules find it in the framework folder.
            tc.make_args.append("FRAMEWORK_LIBRARY_FILE=PreferencePanes.lib")
            framework_dir = os.path.join(self.build_folder, "PreferencePanes", "PreferencePanes.framework")
            ldflags += f" -L{framework_dir.replace('\\', '/').replace('C:', '/c')}"
        tc.make_args.append(f"ALL_LDFLAGS={ldflags}")

        self.python_requires["gnustep-helpers"].module.configure_windows_pkgconf(self, env)

        tc.generate(env)

        deps = PkgConfigDeps(self)
        deps.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        # There is no configure script; the GNUmakefiles build everything directly.
        autotools = Autotools(self)
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []
