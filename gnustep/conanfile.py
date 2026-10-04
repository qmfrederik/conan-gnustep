from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, copy
import os

class GnustepRecipe(ConanFile):
    name = "gnustep"
    version = "0.1"
    if os.getenv("CI"):
        revision_mode = "scm"
    package_type = "library"
    license = "MIT"
    url = "https://github.com/qmfrederik/conan-gnustep"
    description = "A convenience package which provides GNUstep base and GUI libraries."

    # Binary configuration
    settings = {"os", "compiler", "build_type", "arch"}
    options = {"shared": [True, False], "fPIC": [True, False], "objc_runtime": ["gnu", "ng"]}
    default_options = {"shared": True, "fPIC": True, "objc_runtime": "ng"}
    python_requires = "gnustep-helpers/0.1"

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def set_version(self):
        self.version = self.python_requires["gnustep-helpers"].module.get_package_version(self)

    def requirements(self):
        # Depend on gnustep-base, gnustep-gui and libobjc2, and mark both the headers and libs as transitive.
        # This will ensure that any package which requires this gnustep package will automatically be able to
        # include the gnustep-base, gnustep-gui and libobj2 headers, and automatically link with these libraries.
        self.requires("gnustep-base/[^1.31.1]", transitive_headers=True, transitive_libs=True)
        self.requires("gnustep-gui/[^0.32.0]", transitive_headers=True, transitive_libs=True)
        
        if self.options.objc_runtime == "ng":
            self.requires("libobjc2/[^2.2.1]", transitive_headers=True, transitive_libs=True)

        self.tool_requires("gnustep-make/[^2.9.3]")

    def layout(self):
        self.cpp.package.includedirs = []
