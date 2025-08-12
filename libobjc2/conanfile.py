from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get
import os

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
    python_requires = "gnustep-helpers/0.1"

    def set_version(self):
        self.version = self.python_requires["gnustep-helpers"].module.get_package_version(self)

    def source(self):
        get(self, **sorted(self.conan_data["sources"].values())[0])

    def requirements(self):
        self.requires("tsl-robin-map/1.3.0")

        # Use the blocks runtime which ships with libdispatch
        self.requires("libdispatch/[^6.1.1]")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)
    
    def generate(self):
        def yes_no(opt): return "yes" if opt else "no"

        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        # Prevent picking up a default install location through gnustep-config
        tc.variables["GNUSTEP_INSTALL_TYPE"] = "NONE"
        tc.variables["TESTS"] = yes_no(not self.conf.get("tools.build:skip_test", default=False))
        tc.variables["EMBEDDED_BLOCKS_RUNTIME"] = "OFF"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.test()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["objc"]
