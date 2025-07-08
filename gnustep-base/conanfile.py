from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.files import get, patch, replace_in_file
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
    exports_sources = "*.patch"

    def source(self):
        get(self, "https://github.com/gnustep/libs-base/releases/download/base-1_31_1/gnustep-base-1.31.1.tar.gz",
                  strip_root=True)

        # These patches are maintained at https://github.com/qmfrederik/libs-base/tree/base-1_31_1-PACKAGE
        patch(self, patch_file=os.path.join(self.export_sources_folder, "0001-Support-libcurl-7.61.patch"))
        patch(self, patch_file=os.path.join(self.export_sources_folder, "0002-expose-declarations-in-NSDebug.h-even-when-NDEBUG-is.patch"))

    def requirements(self):
        self.requires("libobjc2/2.2.1")
        self.requires("libdispatch/6.1.1")
        self.requires("libffi/3.4.8")
        self.requires("libxml2/2.13.8")
        self.requires("libxslt/1.1.43")

        if self.settings.os != "Windows":
            self.requires("gnutls/3.8.7")

        self.requires("icu/77.1")
        self.requires("libcurl/8.12.1")
        self.requires("libiconv/1.17")
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
        tc = AutotoolsToolchain(self)
        env = tc.environment()
        
        # On Windows, the path to the the compiler may include spaces (e.g. C:\Program Files\LLVM\bin\clang.exe)
        # This creates issues in MSYS2.  Instead, set CC/CXX to the executable name only, and include the parent directly
        # in PATH.
        vars = self.buildenv.vars(self)
        
        if self.settings.os == "Windows":
            cc = vars["CC"]
            cxx = vars["CXX"]
            tc.configure_args.append(f"CC={os.path.basename(cc)}")
            tc.configure_args.append(f"CXX={os.path.basename(cxx)}")
            env.append_path("PATH", os.path.dirname(cc))
            env.append_path("PATH", os.path.dirname(cxx))
            tc.configure_args.append("--disable-tls")

        gnustep_make_package_folder = self.dependencies.build["gnustep-make"].package_folder
        libdispatch_package_folder = self.dependencies["libdispatch"].package_folder
        iconv_package_folder = self.dependencies["libiconv"].package_folder
        ffi_package_folder = self.dependencies["libffi"].package_folder

        gnustep_makefiles_folder = f"{gnustep_make_package_folder}/share/GNUstep/Makefiles/"
        
        # There should be a more elegant way to handle these backwards slashes
        if self.settings.os == "Windows":
            gnustep_makefiles_folder = gnustep_makefiles_folder.replace('\\','/')
            gnustep_makefiles_folder = gnustep_makefiles_folder.replace('C:','/c')
            gnustep_makefiles_folder = f"{gnustep_makefiles_folder}"

        # Add gnustep-config to path
        env.append_path("PATH", os.path.join(gnustep_make_package_folder, "bin"))

        # Add the iconv and libffi bin folder to path.  The configure process will generate an
        # executable which uses iconv, and will try to launch it.  This results in
        # iconv-2.dll being loaded, hence the need for it to be in PATH
        env.append_path("PATH", os.path.join(iconv_package_folder, "bin"))
        env.append_path("PATH", os.path.join(ffi_package_folder, "bin"))

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
        env.append("LDFLAGS", f"-Wl,-rpath-link={libdispatch_package_folder}/libs/")

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
