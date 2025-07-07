from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.files import get
from conan.tools.microsoft import unix_path
import os

class GnustepBaseRecipe(ConanFile):
    name = "gnustep-base"
    version = "1.31.1"
    package_type = "library"
    license = "LGPL-2.1"
    url = "https://github.com/gnustep/libs-base"
    description = "The GNUstep Base Library is a library of general-purpose, non-graphical Objective C objects."
    
    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}

    def source(self):
        get(self, "https://github.com/gnustep/libs-base/releases/download/base-1_31_1/gnustep-base-1.31.1.tar.gz",
                  strip_root=True)

    def requirements(self):
        self.requires("gnustep-make/2.9.3")
        self.requires("libobjc2/2.2.1")
        self.requires("libdispatch/6.1.1")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        # Require a MSYS2 shell on Windows (for Autotools support)
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def generate(self):
        tc = AutotoolsToolchain(self)
        env = tc.environment()
        
        # On Windows, the path to the the compiler may include spaces (e.g. C:\Program Files\LLVM\bin\clang.exe)
        # This creates issues in MSYS2.  Instead, set CC/CXX to the executable name only, and include the parent directly
        # in PATH.
        vars = self.buildenv.vars(self)
        
        if self._settings_build.os == "Windows":
            cc = vars["CC"]
            cxx = vars["CXX"]
            tc.configure_args.append(f"CC={os.path.basename(cc)}")
            tc.configure_args.append(f"CXX={os.path.basename(cxx)}")
            env.append_path("PATH", os.path.dirname(cc))
            env.append_path("PATH", os.path.dirname(cxx))

        gnustep_make_package_folder = self.dependencies["gnustep-make"].package_folder

        # Add gnustep-config to path
        env.append_path("PATH", os.path.join(gnustep_make_package_folder, "bin"))

        # Resolve GNUstep makefiles
        tc.configure_args.append(f"GNUSTEP_MAKEFILES={gnustep_make_package_folder}/share/GNUstep/Makefiles/")
        tc.configure_args.append("--disable-importing-config-file")
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
