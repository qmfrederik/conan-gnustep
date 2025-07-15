import package_version
from conan import ConanFile
from conan.tools.gnu import PkgConfigDeps
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
        # The copy of MSYS2 in conancentral doesn't include pkg-config, but we acquired it as a built
        # tool, so use that
        env.define("PKG_CONFIG", os.path.join(pkg.dependencies.build["pkgconf"].package_folder, "bin", "pkgconf.exe"))

        # Generate pkg-config data for dependencies, which we can inject into the configure process.
        print(f"Generating pkg-config data in {pkg.generators_folder}")
        deps = PkgConfigDeps(pkg)
        deps.generate()
        env.define("PKG_CONFIG_PATH", pkg.generators_folder)

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
    package_type = "python-require"
    exports = "*.py"
