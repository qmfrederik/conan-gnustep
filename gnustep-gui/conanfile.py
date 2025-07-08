from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.files import get, apply_conandata_patches
from conan.tools.build import cross_building
from conan.tools.env import VirtualRunEnv
import os

class GnustepGuiRecipe(ConanFile):
    name = "gnustep-gui"
    version = "0.32.0"
    package_type = "library"
    license = "LGPL-2.1"
    url = "https://github.com/gnustep/libs-gui"
    description = "The GNUstep gui library is a library of graphical user interface classes written completely in the Objective-C language; the classes are based upon Apple's Cocoa framework (which came from the OpenStep specification)."
    
    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    exports_sources = "*.patch"

    def source(self):
        get(self, **self.conan_data["sources"][self.version])
        apply_conandata_patches(self)

    def requirements(self):
        self.requires("gnustep-base/1.31.1")
        self.requires("libjpeg/9e")
        self.requires("libtiff/4.7.0")
        self.tool_requires("gnustep-make/2.9.3")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def build_requirements(self):
        # Require a MSYS2 shell on Windows (for Autotools support)
        if self.settings.os == "Windows":
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

        gnustep_make_package_folder = self.dependencies.build["gnustep-make"].package_folder
        gnustep_makefiles_folder = f"{gnustep_make_package_folder}/share/GNUstep/Makefiles/"
        
        # There should be a more elegant way to handle these backwards slashes
        if self.settings.os == "Windows":
            gnustep_makefiles_folder = gnustep_makefiles_folder.replace('\\','/')
            gnustep_makefiles_folder = gnustep_makefiles_folder.replace('C:','/c')
            gnustep_makefiles_folder = f"{gnustep_makefiles_folder}"

        # Add gnustep-config to path
        env.append_path("PATH", os.path.join(gnustep_make_package_folder, "bin"))

        # Resolve GNUstep makefiles
        tc.configure_args.append(f"GNUSTEP_MAKEFILES={gnustep_makefiles_folder}")
        tc.make_args.append(f"GNUSTEP_MAKEFILES={gnustep_makefiles_folder}")
        tc.configure_args.append("--disable-importing-config-file")

        # Force the use of a relative value for srcdir.  Some configure checks will inject
        # the value of srcdir into a C source file, like this:
        # #include "$srcdir/config/config.reuseaddr.c"
        # If $srcdir contains a Unix-like path (e.g. /c/Users/...), this path will be passed
        # through the compiler (clang) which is expecting Windows-like paths, resulting
        # in build failures.
        tc.configure_args.append("--srcdir=.")

        if self.settings.os == "Windows":
            # On Windows, force targetting native Windows, even when building in an MSYS2 shell (we're somewhat cross-compiling
            # from MSYS2 to native Windows, even though we're using the _native_ tooling within MSYS2).
            # If these variables are not set, gnustep-make will include -lm in the libs used when compiling, resulting in a
            # compiler error when building gnustep-base.
            #
            # The output in configure logs for tools-make should be like this:
            # checking build system type... x86_64-w64-mingw32
            # checking host system type... x86_64-pc-windows
            # checking target system type... x86_64-pc-windows
            tc.configure_args.append(f"--host=x86_64-pc-windows")
            tc.configure_args.append(f"--target=x86_64-pc-windows")

            # Generate pkg-config data for dependencies, which we can inject into the configure process.
            print(f"Generating pkg-config data in {self.generators_folder}")
            deps = PkgConfigDeps(self)
            deps.generate()
            env.define("PKG_CONFIG_PATH", self.generators_folder)

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
