from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.files import get, apply_conandata_patches, mkdir, replace_in_file
from conan.tools.build import cross_building
from conan.tools.env import VirtualRunEnv
import os
import shutil

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
        self.requires("libpng/1.6.50")
        self.requires("giflib/5.2.2")
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
        build_makefiles = os.path.join(self.build_folder, "build/Makefiles")
        mkdir(self, build_makefiles)
        shutil.copytree(gnustep_make_makefiles, build_makefiles, dirs_exist_ok=True)
        shutil.copytree(gnustep_base_makefiles, build_makefiles, dirs_exist_ok=True)

        if self.settings.os == "Windows":
            build_makefiles = build_makefiles.replace('\\','/')
            build_makefiles = build_makefiles.replace('C:','/c')

        # Resolve GNUstep makefiles
        tc.configure_args.append(f"GNUSTEP_MAKEFILES={build_makefiles}")
        tc.make_args.append(f"GNUSTEP_MAKEFILES={build_makefiles}")
        tc.configure_args.append("--disable-importing-config-file")

        gnustep_base_include = self.get_package_folder("gnustep-base", "include/")
        tc.make_args.append(f"OBJC_INCLUDE_PATH={gnustep_base_include}")

        # Similarly, because the headers are spread out in different packages (and not just in a central location), be explicit about
        # the include paths.  Conan passes this data to the ./configure script, and libs-gui compiles correctly, but somehow this
        # data is lost when starting to compile the libgmodel bundle.  Work around this using even more environment variables.
        gnustep_base_lib = self.get_package_folder("gnustep-base", "lib/")
        dispatch_lib = self.get_package_folder("libdispatch", "lib/")
        libobjc2_lib = self.get_package_folder("libobjc2", "lib/")
        tc.make_args.append(f"ALL_LDFLAGS=-L{gnustep_base_lib} -L{dispatch_lib} -L{libobjc2_lib}")

        if self.settings.os != "Windows":
            # Force linking with libicu
            tc.make_args.append("CONFIG_SYSTEM_LIBS=-licuuc")

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

            # The Conan packages for libjpeg ship with a library named libjpeg.lib (as opposed to jpeg.lib);
            # account for this by using -llibjpeg instead of -ljpeg.
            # Another approach for fixing this would be to patch the upstream configure script to use pkgconfig
            # to find libjpeg.
            replace_in_file(
                self,
                os.path.join(self.source_folder, "configure"),
                "-ljpeg",
                "-llibjpeg",
            )

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
