from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
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
    python_requires = "gnustep-helpers/0.1"

    def set_version(self):
        self.version = self.python_requires["gnustep-helpers"].module.get_package_version(self)

    def source(self):
        get(self, **sorted(self.conan_data["sources"].values())[0])
        apply_conandata_patches(self)

    def requirements(self):
        self.requires("libobjc2/[^2.2.1]")
        self.requires("libdispatch/[^6.1.1]")
        self.requires("libffi/3.4.8")
        self.requires("libxml2/2.13.8")
        self.requires("libxslt/1.1.43")

        if self.settings.os != "Windows":
            self.requires("gnutls/3.8.7")

        self.requires("icu/77.1")
        self.requires("libcurl/8.12.1")
        self.requires("libiconv/1.17")
        self.requires("gnustep-make/[^2.9.3]")
        self.tool_requires("gnustep-make/[^2.9.3]")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def build_requirements(self):
        # Require a MSYS2 shell on Windows (for Autotools support)
        self.python_requires["gnustep-helpers"].module.windows_build_requirements(self)

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

        # On Windows, force targetting native Windows, even when building in an MSYS2 shell
        self.python_requires["gnustep-helpers"].module.configure_windows_host(self, tc)

        # On Windows, use a copy of pkgconf which ships via Conan
        self.python_requires["gnustep-helpers"].module.configure_windows_pkgconf(self, env)

        # On Windows, running the test requires the Source/obj folder to be in PATH, not just LD_LIBRARY_PATH
        if self.settings.os == "Windows":
            env.append_path("PATH", os.path.join(self.build_folder, "Source/obj"))

        tc.generate(env)

        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        def yes_no(opt): return "yes" if opt else "no"

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

        if not self.conf.get("tools.build:skip_test", default=False):
            # Build tests for release to match CRT of DLLs (for Windows compatibility).
            test_with_debug=yes_no(self.settings.build_type == "Debug")
            autotools.make(
                target="check",
                args=[f"GSMAKEOPTIONS='debug={test_with_debug}'"])

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
        
        if self.settings.os == "Windows":
            rmdir(self, os.path.join(self.package_folder, "c"))
        else:
            rmdir(self, os.path.join(self.package_folder, "home"))

    def package_info(self):
        self.cpp_info.libs = ["gnustep-base"]
        self.cpp_info.defines = ["GNUSTEP=1", "GNUSTEP_RUNTIME=1", "GNUSTEP_BASE_LIBRARY=1", "_NATIVE_OBJC_EXCEPTIONS=1"]
        if self.settings.os == "Windows":
            self.cpp_info.defines.append("GNUSTEP_WITH_DLL=1")
        self.cpp_info.cflags = ["-fconstant-string-class=NSConstantString", "-fblocks"]
