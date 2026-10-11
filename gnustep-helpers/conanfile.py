import package_version
from conan import ConanFile
import os

def get_package_version(package):
    try:
        return package_version.get_package_version(package)
    except Exception as inst:
        # We're building outside of a Git repository.
        # Return None so the package version is set from metadata.
        package.output.warning(f"Couldn't determine version number: {inst}")
        return None

def configure_windows_host(pkg, autotools):
    if pkg.settings.os == "Windows":
        # On Windows, force targetting native Windows, even when building in an MSYS2 shell (we're somewhat cross-compiling
        # from MSYS2 to native Windows, even though we're using the _native_ tooling within MSYS2).
        # If these variables are not set, gnustep-make will include -lm in the libs used when compiling, resulting in a
        # compiler error when building gnustep-base.
        #
        # The output in configure logs for tools-make should be like this:
        # checking build system type... x86_64-w64-mingw32
        # checking host system type... x86_64-pc-windows
        # checking target system type... x86_64-pc-windows
        autotools.configure_args.append(f"--host=x86_64-pc-windows")
        autotools.configure_args.append(f"--target=x86_64-pc-windows")

def configure_windows_pkgconf(pkg, env):
    if pkg.settings.os == "Windows":
        # The copy of MSYS2 in conancentral doesn't include pkg-config, but we acquired it as a build
        # tool, so use that
        env.define("PKG_CONFIG", os.path.join(pkg.dependencies.build["pkgconf"].package_folder, "bin", "pkgconf.exe"))

def gnustep_register_additional_makefiles(pkg, makefile):
    # Have the child build systems pick up the package's additional makefile.  By default, GNUstep expects all additional
    # Makefiles to be in the same location (e.g. /usr/share/GNUstep/Makefiles/Additional/ on Ubuntu).  When using Conan,
    # these files live in the various packages.  Each package can declare their own extra package-specific Makefiles
    # by adding to GNUSTEP_BUILD_ADDITIONAL_MAKEFILES.
    path = os.path.join(pkg.package_folder, "share", "GNUstep", "Makefiles", "Additional", makefile)
    if pkg.settings.os == "Windows":
        path = path.replace('\\', '/').replace('C:', '/c')
    pkg.buildenv_info.append("GNUSTEP_BUILD_ADDITIONAL_MAKEFILES", path)

def gnustep_register_library_paths(pkg):
    # By default, most GNUstep-related libraries live in the same folder.  The build system isn't expecting to
    # be looking for libraries in non-standard locations.  We provide the necessary flags to help the build system find them.
    lib_dir = os.path.join(pkg.package_folder, "lib")
    include_dir = os.path.join(pkg.package_folder, "include")
    if pkg.settings.os == "Windows":
        lib_dir = lib_dir.replace('\\', '/').replace('C:', '/c')
        include_dir = include_dir.replace('\\', '/').replace('C:', '/c')

    # Set the lib dir through ADDITIONAL_LDFLAGS so bundles can find the package's library during linking.
    pkg.buildenv_info.append("ADDITIONAL_LDFLAGS", f"-L{lib_dir}")

    # The compiler only searches OBJC_INCLUDE_PATH for Objective-C headers (<Foundation/...>) when
    # the include paths from CPPFLAGS are not passed through (e.g. when building bundles).
    pkg.buildenv_info.append_path("OBJC_INCLUDE_PATH", include_dir)

def windows_build_requirements(pkg):
    # Require a MSYS2 shell on Windows (for Autotools support)
    if pkg.settings.os == "Windows":
        pkg.win_bash = True
        if not pkg.conf.get("tools.microsoft.bash:path", check_type=str):
            pkg.tool_requires("msys2/cci.latest")
            pkg.tool_requires("pkgconf/[>=2.2]")

class Pkg(ConanFile):
    name = "gnustep-helpers"
    version = "0.1"
    if os.getenv("CI"):
        revision_mode = "scm"
    package_type = "python-require"
    exports = "*.py"
