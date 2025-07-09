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

    def source(self):
        get(self, **self.conan_data["sources"][self.version])
        apply_conandata_patches(self)

    def requirements(self):
        self.requires("libobjc2/2.2.1")

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

        # Use shared blocks runtime
        libobjc2_package_folder = self.dependencies["libobjc2"].package_folder
        libobjc_library_name = "libobjc.so"
        
        if self.settings.os == "Windows":
            libobjc_library_name = "objc.lib"

        libobjc_include_dir = os.path.join(libobjc2_package_folder, "include")
        libobjc_library = os.path.join(libobjc2_package_folder, "lib", libobjc_library_name)

        # There should be a more elegant way to handle these backwards slashes
        if self.settings.os == "Windows":
            libobjc_include_dir = libobjc_include_dir.replace('\\','/')
            libobjc_library = libobjc_library.replace('\\','/')

        tc.variables["BlocksRuntime_INCLUDE_DIR"] = libobjc_include_dir
        tc.variables["BlocksRuntime_LIBRARIES"] = libobjc_library
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
