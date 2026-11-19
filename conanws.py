import importlib.util
import os
import sys
from types import SimpleNamespace

import yaml
from conan import Workspace


# Packages which only make sense on Windows; they're left out of the workspace on other platforms.
WINDOWS_ONLY_PACKAGES = {"gnustep-back", "gnustep-winuxtheme"}


class MyWorkspace(Workspace):
   """
   More info: https://docs.conan.io/2/incubating.html#workspaces
   """
   def name(self):
      return "conan-gnustep"

   def packages(self):
      # Compute the reference (including the build and prerelease version) using the same code as
      # gnustep-helpers, because the recipes can't be asked for it: Conan loads them without python_requires.
      path = os.path.join(self.folder, "gnustep-helpers", "package_version.py")
      spec = importlib.util.spec_from_file_location("package_version", path)
      package_version = importlib.util.module_from_spec(spec)
      spec.loader.exec_module(package_version)

      packages = []
      for package in super().packages():
         package = dict(package)

         if sys.platform != "win32" and os.path.basename(os.path.normpath(package["path"])) in WINDOWS_ONLY_PACKAGES:
            continue

         if "ref" not in package:
            recipe_folder = os.path.normpath(os.path.join(self.folder, package["path"]))
            name = os.path.basename(recipe_folder)

            with open(os.path.join(recipe_folder, "conandata.yml")) as stream:
               base_version = next(iter(yaml.safe_load(stream)["sources"]))

            package_stub = SimpleNamespace(name=name, version=base_version, recipe_folder=recipe_folder)
            version = package_version.get_package_version(package_stub) or base_version
            package["ref"] = f"{name}/{version}"

         packages.append(package)

      return packages
