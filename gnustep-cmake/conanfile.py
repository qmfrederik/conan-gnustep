from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps

class GnustepCmakeRecipe(ConanFile):
    name = "gnustep-cmake"
    version = "0.1.0"
    package_type = "header-library"
    license = "MIT"
    url = "https://github.com/qmfrederik/conan-gnustep/"
    description = "A CMake package for using GNUstep."

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "CMakeLists.txt", "GNUstepConfig.cmake"

    # Minimum settings required for CMake
    settings = "build_type"

    def requirements(self):
        self.requires("libobjc2/2.2.1")
        self.requires("gnustep-base/1.31.1")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        # No information provided, only the in-package .cmake is used here
        # Other build systems or CMake via CMakeDeps will fail
        # See https://docs.conan.io/2/examples/tools/cmake/cmake_toolchain/use_package_config_cmake.html
        # for more details
        self.cpp_info.builddirs = ["share/cmake/GNUstep/"]
        self.cpp_info.set_property("cmake_find_mode", "none")
