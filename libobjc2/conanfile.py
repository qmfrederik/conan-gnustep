from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get

class libobjc2Recipe(ConanFile):
    name = "libobjc2"
    version = "2.2.1"
    package_type = "library"
    license = "MIT"
    url = "https://github.com/gnustep/libobjc2"
    description = "Objective-C runtime library intended for use with Clang."
    topics = ("Objective-C", "GNUstep", "clang")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}

    def source(self):
        get(self, "https://github.com/gnustep/libobjc2/archive/v2.2.1.zip",
                  strip_root=True)

    def requirements(self):
        self.requires("tsl-robin-map/1.3.0")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)
    
    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        # Prevent picking up a default install location through gnustep-config
        tc.variables["GNUSTEP_INSTALL_TYPE"] = "NONE"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

