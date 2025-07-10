from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.files import get, apply_conandata_patches, copy, rmdir
from conan.tools.build import cross_building
from conan.tools.env import VirtualRunEnv
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
        get(self, **self.conan_data["sources"][self.version])
        apply_conandata_patches(self)

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
                self.tool_requires("pkgconf/[>=2.2]")

    def get_makefiles_folder(self):
        gnustep_make_package_folder = self.dependencies.build["gnustep-make"].package_folder
        gnustep_makefiles_folder = f"{gnustep_make_package_folder}/share/GNUstep/Makefiles/"

        # There should be a more elegant way to handle these backwards slashes
        if self.settings.os == "Windows":
            gnustep_makefiles_folder = gnustep_makefiles_folder.replace('\\','/')
            gnustep_makefiles_folder = gnustep_makefiles_folder.replace('C:','/c')
            gnustep_makefiles_folder = f"{gnustep_makefiles_folder}"

        return gnustep_makefiles_folder
        
    def generate(self):
        if not cross_building(self):
            # Expose LD_LIBRARY_PATH when there are shared dependencies,
            # as configure tries to run a test executable (when not cross-building)
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        env = tc.environment()
        
        # We don't have a gnutls build for Windows, yet
        if self.settings.os == "Windows":
            tc.configure_args.append("--disable-tls")

        libdispatch_package_folder = self.dependencies["libdispatch"].package_folder

        if self.settings.os == "Windows":
            # The copy of MSYS2 in conancentral doesn't include pkg-config, but we acquired it as a built
            # tool, so use that
            env.define("PKG_CONFIG", os.path.join(self.dependencies.build["pkgconf"].package_folder, "bin", "pkgconf.exe"))

        # Resolve GNUstep makefiles
        gnustep_makefiles_folder = self.get_makefiles_folder()
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

        # Make install copies the additional makefiles into $DESTDIR/${gnustep_make_package_folder}/share/GNUstep/Makefiles/,
        # but gnustep_make_package_folder is a fully qualified path (/home/user/.conan/p/b/{package}/p/share/GNUstep/Makefiles/);
        # we fix that here.  This always runs in a GNU-like context (Linux or MSYS), so we can assume Unix paths.
        src = os.path.join(self.package_folder, self.get_makefiles_folder()[1:], "Additional")
        dst = os.path.join(self.package_folder, "share/GNUstep/Makefiles/Additional/")
        copy(
            self,
            "*.make",
            src=src,
            dst = dst)
        rmdir(self, os.path.join(self.package_folder, "home"))

    def package_info(self):
        self.cpp_info.libs = ["gnustep-base"]
