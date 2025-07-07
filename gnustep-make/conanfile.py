from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.files import get
from conan.tools.microsoft import unix_path
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
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def source(self):
        get(self, "https://github.com/gnustep/tools-make/releases/download/make-2_9_3/gnustep-make-2.9.3.tar.gz",
                  strip_root=True)

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
        tc.configure_args.append("--with-library-combo=ng-gnu-gnu")
        tc.configure_args.append("--with-runtime-abi=gnustep-2.2")
        tc.extra_ldflags = ["-fuse-ld=lld"]
        
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
