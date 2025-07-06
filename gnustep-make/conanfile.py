from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.files import get


class HelloConan(ConanFile):
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

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--with-library-combo=ng-gnu-gnu")
        tc.configure_args.append("--with-runtime-abi=gnustep-2.2")
        tc.extra_ldflags = ["-fuse-ld=lld"]
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()
