from conan import ConanFile
import package_version

def get_package_version(repository, package_name):
    return package_version.get_package_version(repository, package_name)

class Pkg(ConanFile):
    name = "gnustep-helpers"
    version = "0.1"
    package_type = "python-require"
    exports = "*.py"