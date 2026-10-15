from conan import ConanFile
from conan.tools.files import load, save
import os
import tempfile

GNUSTEP_CONFIG = """\
case "$1" in
--variable=CPPFLAGS) echo "-DNDEBUG -I/home/user/.conan2/p/abc/p/include";;
--variable=LDFLAGS)  echo "-m64 -fuse-ld=lld -L/home/user/.conan2/p/abc/p/lib";;
--variable=MIDDLE)   echo "-DNDEBUG -I/home/user/include -m64";;
--variable=RPATH)    echo "-m64 -Wl,-rpath,/home/user/lib";;
esac
"""

EXPECTED = """\
case "$1" in
--variable=CPPFLAGS) echo "-DNDEBUG";;
--variable=LDFLAGS)  echo "-m64 -fuse-ld=lld";;
--variable=MIDDLE)   echo "-DNDEBUG -m64";;
--variable=RPATH)    echo "-m64";;
esac
"""

class HelpersTestConan(ConanFile):
    python_requires = "gnustep-helpers/0.2"

    def test(self):
        with tempfile.TemporaryDirectory() as folder:
            self.folders.set_base_package(folder)
            save(self, os.path.join(folder, "bin", "gnustep-config"), GNUSTEP_CONFIG)

            self.python_requires["gnustep-helpers"].module.strip_absolute_paths(self, "bin/gnustep-config")

            actual = load(self, os.path.join(folder, "bin", "gnustep-config"))
            if actual != EXPECTED:
                raise AssertionError(f"strip_absolute_paths produced unexpected output.\n--- expected ---\n{EXPECTED}\n--- actual ---\n{actual}")
