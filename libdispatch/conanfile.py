import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, apply_conandata_patches

class LibDispatchRecipe(ConanFile):
    name = "libdispatch"
    version = "6.1.1"
    package_type = "library"
    license = "Apache-2.0"
    url = "https://github.com/swiftlang/swift-corelibs-libdispatch"
    description = "The libdispatch Project, (a.k.a. Grand Central Dispatch), for concurrency on multicore hardware."
    
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

        tc.variables["BUILD_TESTING"] = "NO"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["dispatch"]
