# Cross-platform build tools for GNUstep

This repository contains [Conan](https://conan.io/) support for building [GNUstep](https://gnustep.github.io/) on Windows and Linux.

It contains:
- [Conan recipes](https://docs.conan.io/2/reference/conanfile.html) for building [libobjc2](https://github.com/gnustep/libobjc2), [libdispatch](https://github.com/apple/swift-corelibs-libdispatch/), [gnustep-make](https://github.com/gnustep/tools-make) and [gnustep-base](https://github.com/gnustep/libs-base)
- [Conan profiles](https://docs.conan.io/2/reference/config_files/profiles.html) for building using clang on Windows and Linux

On Windows, this repository takes the approach of building GNUstep using the Windows-native LLVM (clang) compiler. It uses MSYS2 to get a Bash shell, which allows running the scripts required to configure and build GNUstep, and does not use the MSYS2 compiler toolchain.

## Using Conan packages for GNUstep

Prebuilt binary Conan packages containing GNUstep for Windows are available at https://cloudsmith.io/~qmfrederik/repos/gnustep:

| Package       | Status
|---------------|---------------
| gnustep-make  | [![Latest version of 'gnustep-make'](https://api.cloudsmith.com/v1/badges/version/qmfrederik/gnustep/conan/gnustep-make/latest/a=x86_64/?render=true&show_latest=true)](https://cloudsmith.io/~qmfrederik/repos/gnustep/packages/detail/conan/gnustep-make/latest/a=x86_64/)
| gnustep-base  | [![Latest version of 'gnustep-base'](https://api.cloudsmith.com/v1/badges/version/qmfrederik/gnustep/conan/gnustep-base/latest/a=x86_64/?render=true&show_latest=true)](https://cloudsmith.io/~qmfrederik/repos/gnustep/packages/detail/conan/gnustep-base/latest/a=x86_64/)
| gnustep-gui   | [![Latest version of 'gnustep-gui'](https://api.cloudsmith.com/v1/badges/version/qmfrederik/gnustep/conan/gnustep-gui/latest/a=x86_64/?render=true&show_latest=true)](https://cloudsmith.io/~qmfrederik/repos/gnustep/packages/detail/conan/gnustep-gui/latest/a=x86_64/)
| gnustep-headless | [![Latest version of 'gnustep-headless'](https://api.cloudsmith.com/v1/badges/version/qmfrederik/gnustep/conan/gnustep-headless/latest/a=x86_64/?render=true&show_latest=true)](https://cloudsmith.io/~qmfrederik/repos/gnustep/packages/detail/conan/gnustep-headless/latest/a=x86_64/)

Due to download constraints on CloudSmith, these packages are mirrored on [GitLab](https://gitlab.com/qmfrederik/conan/-/packages).

To get started, run:

```bash
conan remote add gnustep https://gitlab.com/api/v4/projects/72962159/packages/conan
```

## Getting started on Windows
On Windows, you'll need to download the Windows SDK and the LLVM toolchain. Optionally, you can use Visual Studio Code as an editor and Git for source code interations.

- [Visual Studio 2022 Build Tools (Windows SDK)](https://visualstudio.microsoft.com/downloads/)
- [LLVM 20.0 or later](https://releases.llvm.org/download.html)
- [Git for Windows](https://git-scm.com/download/win)
- [Conan](https://conan.io/downloads)

To get started, run the following commands:

```bash
git clone https://github.com/qmfrederik/conan-gnustep/
cd conan-gnustep

python3.14 -m venv .python3/
.\.python3\Scripts\activate
pip install conan==2.33.0 pygit2

conan config install global.conf
conan create gnustep-helpers --profile:a=profiles/windows-clang-vs2026
conan create libdispatch --profile:a=profiles/windows-clang-vs2026
conan create libobjc2 --profile:a=profiles/windows-clang-vs2026
conan create gnustep-make --profile:a=profiles/windows-clang-vs2026
conan create gnustep-base --profile:a=profiles/windows-clang-vs2026 -c tools.build:skip_test=True --build=icu/* --build=gnustep-base/*
conan create gnustep-gui --profile:a=profiles/windows-clang-vs2026
conan create gnustep-headless --profile:a=profiles/windows-clang-vs2026
```

This will configure GNUstep Base and all of its dependencies.

## Getting started on Linux

```bash
apt-get install -y clang lld curl zip unzip tar git pkg-config make python3-venv cmake libffi-dev libxml2-dev libxslt-dev gnutls-dev libicu-dev libcurl4-gnutls-dev

git clone https://github.com/qmfrederik/conan-gnustep/
cd conan-gnustep

python3 -m venv .python3/
.python3/bin/pip install conan==2.33.0
. .python3/bin/activate
conan config install global.conf
conan create gnustep-helpers --profile:a=profiles/linux-clang
conan create libdispatch --profile:a=profiles/linux-clang
conan create libobjc2 --profile:a=profiles/linux-clang
conan create gnustep-make --profile:a=profiles/linux-clang
conan create gnustep-base --profile:a=profiles/linux-clang -c tools.build:skip_test=True --build=icu/* --build=gnustep-base/*
conan create gnustep-gui --profile:a=profiles/linux-clang
conan create gnustep-headless --profile:a=profiles/linux-clang
```

## Tips & Tricks

There's a couple of tips & tricks which help when you're building GNUstep on a Windows platform:

- libobjc2 works best when used with LLVM/clang on Windows and Linux.
- The GNUstep build system relies on a bash shell.  On Windows, you can use MSYS2 to get a bash prompt.  There's support
  for MSYS2 in both [Conan](https://docs.conan.io/2/examples/tools/autotools/create_your_first_package_windows.html) and
  [vcpkg](https://learn.microsoft.com/en-us/vcpkg/maintainers/functions/vcpkg_acquire_msys).
- The build tools will assume you're targetting an MSYS2 environment when running `./configure` in a MSYS2 environment.
  To make it target a 'native' Windows environment, specify `--host=x86_64-pc-windows` and `--target=x86_64-pc-windows`.
- You can aquire [`pkgconf`](https://github.com/pkgconf/pkgconf) as a build tool: `self.tool_requires("pkgconf/[>=2.2]")`.
  Set the `PKG_CONFIG` variable to override the path to the `pkg-config` tool.
- Running the tests for the various GNUstep projects will require you to add the path of the main output (e.g. `gnustep-gui.dll`) to be in the Windows path.

These tips may help when debugging:

- Conan recipes are Python scripts.  You can debug them using VS Code.
- Because Conan copies scripts before executing them, breakpoints you've set may not be hit.  But you can add a `breakpoint()`
  call to the script, forcing the debugger to pause.
- If a build fails, you can enter an MSYS2 session by running `C:\Users\vagrant\.conan2\p\msys2f33247fcfc934\p\bin\msys64\usr\bin\bash.exe --login -i`.
  From within that session, you can run `./configure`, `make`,... --- just make sure to environment variables such as `PATH`.

# Good to know

## File system layout
GNUstep assumes that the file system layout is fixed, and the paths like `GNUSTEP_SYSTEM_LIBRARY`, `GNUSTEP_SYSTEM_LIBRARIES`, `GNUSTEP_SYSTEM_HEADERS`,
`GNUSTEP_SYSTEM_TOOLS` and `GNUSTEP_SYSTEM_APPS` are predictable.

That isn't true when shipping GNUstep as Conan packages.  To work around this, the `0005-Locate-GNUstep-system-paths-relative-to-the-library.patch`
patch updates these values at runtime, and they always respect the Conan package layout.

## ICU libraries

GNUstep uses ICU for working with time zones.  ICU reads some of this data from files, such as the `tzdata` files.  When using an operating-system
provided copy of ICU, this usually works.  When using the ICU Conan package, a similar problem arises: GNUstep doesn't know where to find this data.

When using the ICU Conan package:
- The `data_packaging` option should be set to `static`.  This ensures ICU data is embedded in the gnustep-base library.
- Other resources, such as tzdata, are shipped as GNUstep bundle resources, and the file system layout patch (mentioned above) is required.
