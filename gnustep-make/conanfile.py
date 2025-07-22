from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.files import get
from conan.tools.build import cross_building
from conan.tools.env import VirtualRunEnv
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version

import os

class GnustepMakeRecipe(ConanFile):
    name = "gnustep-make"
    version = "2.9.3"
    package_type = "library"
    license = "GPL-3.0"
    url = "https://github.com/gnustep/tools-make"
    description = "The makefile package is a simple, powerful and extensible way to write makefiles for a GNUstep-based project."
    
    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "objc_runtime": ["gnu", "ng"]}
    default_options = {"shared": False, "fPIC": True, "objc_runtime": "ng"}
    python_requires = "gnustep-helpers/0.1"

    def set_version(self):
        self.version = self.python_requires["gnustep-helpers"].module.get_package_version(self)

    def source(self):
        get(self, **sorted(self.conan_data["sources"].values())[0])

    def validate(self):
        # Require clang 20 on Windows
        if self.settings.os == "Windows" and (self.settings.compiler != "clang" or Version(self.settings.compiler.version) < "20"):
            raise ConanInvalidConfiguration("GNUstep requires clang 20.0 or later on Windows")
        elif self.settings.compiler != "gcc" and self.settings.compiler != "clang":
            raise ConanInvalidConfiguration(f"GNUstep requires clang or gcc.  You are currently using {self.settings.compiler}")

    def requirements(self):
        if self.settings.compiler == "clang":
            self.requires("libobjc2/[^2.2.1]")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        # Require a MSYS2 shell on Windows (for Autotools support)
        self.python_requires["gnustep-helpers"].module.windows_build_requirements(self)

    def generate(self):
        if not cross_building(self):
            # Expose LD_LIBRARY_PATH when there are shared dependencies,
            # as configure tries to run a test executable (when not cross-building)
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        env = tc.environment()
        
        if self.options.objc_runtime == "ng":
            tc.configure_args.append("--with-library-combo=ng-gnu-gnu")
            tc.configure_args.append("--with-runtime-abi=gnustep-2.2")
            env.append("LDFLAGS", "-fuse-ld=lld")
        else:
            tc.configure_args.append("--with-library-combo=gnu-gnu-gnu")
        
        # On Windows, force targetting native Windows, even when building in an MSYS2 shell
        self.python_requires["gnustep-helpers"].module.configure_windows_host(self, tc)

        tc.generate(env)

        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.defines = [ "_NONFRAGILE_ABI=1" ]
        self.cpp_info.cflags = [ "-fexceptions", "-fobjc-exceptions" ]
        
        if self.options.objc_runtime == "ng":
            self.cpp_info.cflags.append("-fobjc-runtime=gnustep-2.2")
            self.cpp_info.requires = [ "libobjc2::libobjc2" ]
        else:
            self.cpp_info.system_libs = ["objc"]
