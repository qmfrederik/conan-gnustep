from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
from conan.errors import ConanInvalidConfiguration
import os

class TestPackageConan(ConanFile):
    name = "gnustep-make-test"
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"
    options = {"objc_runtime": ["gnu", "ng"]}
    default_options = {"objc_runtime": "ng"}

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

        if self.options.objc_runtime == "ng":
            self.requires("libobjc2/[^2.2.1]")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
