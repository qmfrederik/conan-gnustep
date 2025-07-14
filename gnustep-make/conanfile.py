from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.files import get
from conan.tools.build import cross_building
from conan.tools.env import VirtualRunEnv

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
        get(self, **self.conan_data["sources"][self.version])

    def requirements(self):
        self.requires("libobjc2/[^2.2.1]")

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
        if not cross_building(self):
            # Expose LD_LIBRARY_PATH when there are shared dependencies,
            # as configure tries to run a test executable (when not cross-building)
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        env = tc.environment()
        tc.configure_args.append("--with-library-combo=ng-gnu-gnu")
        tc.configure_args.append("--with-runtime-abi=gnustep-2.2")
        env.append("LDFLAGS", "-fuse-ld=lld")
        
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
