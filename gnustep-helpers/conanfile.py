from conan import ConanFile
import package_version

def get_package_version(repository, package_name):
    return package_version.get_package_version(repository, package_name)

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

class Pkg(ConanFile):
    name = "gnustep-helpers"
    version = "0.1"
    package_type = "python-require"
    exports = "*.py"