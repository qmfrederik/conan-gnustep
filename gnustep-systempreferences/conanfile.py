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
    package_type = "library"
    license = "GPL-2.0-or-later"
    url = "https://github.com/gnustep/apps-systempreferences"
    description = "System Preferences application and PreferencePanes framework for GNUstep."

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "objc_runtime": ["gnu", "ng"]}
    default_options = {"shared": True, "fPIC": True, "objc_runtime": "ng"}
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
            # Expose LD_LIBRARY_PATH when there are shared dependencies,
            # as configure tries to run a test executable (when not cross-building)
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        env = tc.environment()

        # The GNUstep makefiles are stored in the gnustep-make and gnustep-base package (gnustep-base
        # deploys a single makefile, but that contains additional preprocessor definitions which are
        # needed).
        # The GNUstep filesystem doesn't deal with this layout very well, so create a single directory
        # into which we merge both file systems
        gnustep_make_makefiles = os.path.join(self.dependencies.build["gnustep-make"].package_folder, "share/GNUstep/Makefiles/")
        gnustep_base_makefiles = os.path.join(self.dependencies["gnustep-base"].package_folder, "share/GNUstep/Makefiles")
        gnustep_gui_makefiles = os.path.join(self.dependencies["gnustep-gui"].package_folder, "share/GNUstep/Makefiles")
        build_makefiles = os.path.join(self.build_folder, "build/Makefiles")
        mkdir(self, build_makefiles)
        shutil.copytree(gnustep_make_makefiles, build_makefiles, dirs_exist_ok=True)
        shutil.copytree(gnustep_base_makefiles, build_makefiles, dirs_exist_ok=True)
        shutil.copytree(gnustep_gui_makefiles, build_makefiles, dirs_exist_ok=True)

        if self.settings.os == "Windows":
            build_makefiles = build_makefiles.replace('\\','/')
            build_makefiles = build_makefiles.replace('C:','/c')

        # Resolve GNUstep makefiles
        tc.configure_args.append(f"GNUSTEP_MAKEFILES={build_makefiles}")
        tc.make_args.append(f"GNUSTEP_MAKEFILES={build_makefiles}")

        # Fix header paths
        gnustep_base_include = os.path.join(self.dependencies["gnustep-base"].package_folder, "include/")
        gnustep_gui_include = os.path.join(self.dependencies["gnustep-gui"].package_folder, "include/")
        objc_include = os.path.join(self.dependencies["libobjc2"].package_folder, "include/")
        
        if self.settings.os == "Windows":
            tc.make_args.append(f"OBJC_INCLUDE_PATH='{gnustep_base_include};{gnustep_gui_include};{objc_include}'")
        else:
            tc.make_args.append(f"OBJC_INCLUDE_PATH={gnustep_base_include}:{gnustep_gui_include}:{objc_include}")

        # Overriding some linker flags via ALL_LDFLAGS means overriding all; so find all dependencies
        # and provider linker paths
        ldflags = ""
        if self.options.objc_runtime == "ng":
            ldflags += " -fuse-ld=lld"

        gnustep_base_lib = self.get_package_folder("gnustep-base", "lib/")
        gnustep_gui_lib = self.get_package_folder("gnustep-gui", "lib/")
        ldflags += f" -L{gnustep_base_lib} -L{gnustep_gui_lib}"

        # Resolve library paths for the Objective-C runtime
        if self.options.objc_runtime == "ng":
            dispatch_lib = self.get_package_folder("libdispatch", "lib/")
            libobjc2_lib = self.get_package_folder("libobjc2", "lib/")
            ldflags+= f" -L{dispatch_lib} -L{libobjc2_lib}"

        if self.settings.os == "Windows":
            # gnustep-make names a framework's import library libPreferencePanes.dll.lib, but clang resolves
            # -lPreferencePanes to PreferencePanes.lib, so rename it and let the modules find it in the framework folder.
            tc.make_args.append("FRAMEWORK_LIBRARY_FILE=PreferencePanes.lib")
            framework_dir = os.path.join(self.build_folder, "PreferencePanes", "PreferencePanes.framework")
            framework_dir = framework_dir.replace('\\', '/').replace('C:', '/c')
            ldflags += f" -L{framework_dir}"
        tc.make_args.append(f"ALL_LDFLAGS={ldflags}")

        # On Windows, force targetting native Windows, even when building in an MSYS2 shell
        self.python_requires["gnustep-helpers"].module.configure_windows_host(self, tc)

        # On Windows, use a copy of pkgconf which ships via Conan
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
        self.cpp_info.libs = ["PreferencePanes"]
