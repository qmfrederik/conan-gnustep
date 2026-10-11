import package_version
from conan import ConanFile
from conan.tools.files import load, save
import os
import re

_ABSOLUTE_PATH_FLAG = re.compile(r"\s(?:-[IL]|-Wl,-rpath(?:-link)?[=,])(?:/|[A-Za-z]:)\S*")

def strip_absolute_paths(pkg, *relative_files):
    # configure bakes absolute -I/-L/-rpath paths (Conan cache folders of the dependencies) into generated files.
    # Strip them all so a relocated package fails visibly instead of silently using the builder's paths.
    for rel in relative_files:
        path = os.path.join(pkg.package_folder, rel)
        save(pkg, path, _ABSOLUTE_PATH_FLAG.sub("", load(pkg, path)))

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

def msys_path(pkg, path):
    # unix_path() can't be used in package_info(): it relies on win_bash, which is only set while building the package.
    # Only needed for values that embed a path (flags, space-separated lists); append_path() converts on its own.
    if pkg.settings.os == "Windows":
        return path.replace('\\', '/').replace('C:', '/c')
    return path

def gnustep_register_additional_makefiles(pkg, makefile):
    # Have the child build systems pick up the package's additional makefile.  By default, GNUstep expects all additional
    # Makefiles to be in the same location (e.g. /usr/share/GNUstep/Makefiles/Additional/ on Ubuntu).  When using Conan,
    # these files live in the various packages.  Each package can declare their own extra package-specific Makefiles
    # by adding to GNUSTEP_BUILD_ADDITIONAL_MAKEFILES (a space-separated list, so append_path() can't be used).
    path = os.path.join(pkg.package_folder, "share", "GNUstep", "Makefiles", "Additional", makefile)
    pkg.buildenv_info.append("GNUSTEP_BUILD_ADDITIONAL_MAKEFILES", msys_path(pkg, path))

def gnustep_register_library_paths(pkg):
    # By default, most GNUstep-related libraries live in the same folder.  The build system isn't expecting to
    # be looking for libraries in non-standard locations.  We provide the necessary flags to help the build system find them.
    lib_dir = msys_path(pkg, os.path.join(pkg.package_folder, "lib"))
    include_dir = os.path.join(pkg.package_folder, "include")

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
