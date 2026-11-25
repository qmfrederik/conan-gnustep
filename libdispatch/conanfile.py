import os
import glob
from pathlib import Path
from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, apply_conandata_patches

class LibDispatchRecipe(ConanFile):
    name = "libdispatch"
    version = "6.4.3"
    if os.getenv("CI"):
        revision_mode = "scm"
    package_type = "library"
    license = "Apache-2.0"
    url = "https://github.com/swiftlang/swift-corelibs-libdispatch"
    description = "The libdispatch Project, (a.k.a. Grand Central Dispatch), for concurrency on multicore hardware."
    
    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    exports_sources = "*.patch"
    python_requires = "gnustep-helpers/0.3"

    def init(self):
        if not isinstance(self.python_requires, str):
            self.version = self.python_requires["gnustep-helpers"].module.get_package_version(self)

    def source(self):
        get(self, **sorted(self.conan_data["sources"].values())[0])
        apply_conandata_patches(self)

    def requirements(self):
        # Use the blocks runtime which is built into libobjc2, rather than building a separate libBlocksRuntime
        if not is_apple_os(self):
            self.requires("libobjc2/[^2.3]", transitive_headers=True, transitive_libs=True)

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

        if not is_apple_os(self):
            # libobjc2 exports the blocks runtime (and installs Block.h and Block_private.h), but doesn't install a
            # separate libBlocksRuntime. Point FindBlocksRuntime.cmake to libobjc2, so libdispatch doesn't build its own copy.
            libobjc2 = self.dependencies["libobjc2"].cpp_info
            library_names = ["libobjc.so", "libobjc.dll.a", "libobjc.a", "objc.lib"]
            libobjc2_library = next(
                path for libdir in libobjc2.libdirs for name in library_names
                for path in glob.glob(os.path.join(libdir, name)))
            tc.variables["BlocksRuntime_INCLUDE_DIR"] = Path(libobjc2.includedirs[0]).as_posix()
            tc.variables["BlocksRuntime_LIBRARIES"] = Path(libobjc2_library).as_posix()
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

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "rt"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["shlwapi", "ws2_32", "winmm", "synchronization"]

        # Let the build systems of dependents find the headers and library of this package
        self.python_requires["gnustep-helpers"].module.gnustep_register_library_paths(self)
