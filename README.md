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
conan config install global.conf
conan create gnustep-helpers --profile:a=profiles/windows-clang
conan create libobjc2 --profile:a=profiles/windows-clang
conan create libdispatch --profile:a=profiles/windows-clang
conan create gnustep-make --profile:a=profiles/windows-clang
conan create gnustep-base --profile:a=profiles/windows-clang
conan create gnustep-gui --profile:a=profiles/windows-clang
conan create gnustep-headless --profile:a=profiles/windows-clang
conan create gnustep-cmake --profile:a=profiles/windows-clang
```

This will configure GNUstep Base and all of its dependencies.

## Getting started on Linux

```bash
apt-get install -y clang lld curl zip unzip tar git pkg-config make python3-venv cmake libffi-dev libxml2-dev libxslt-dev gnutls-dev libicu-dev libcurl4-gnutls-dev

git clone https://github.com/qmfrederik/conan-gnustep/
cd conan-gnustep

python3 -m venv .python3/
.python3/bin/pip install conan==2.18.1
. .python3/bin/activate
conan config install global.conf
conan create gnustep-helpers --profile:a=profiles/linux-clang
conan create libobjc2 --profile:a=profiles/linux-clang
conan create libdispatch --profile:a=profiles/linux-clang
conan create gnustep-make --profile:a=profiles/linux-clang
conan create gnustep-base --profile:a=profiles/linux-clang
conan create gnustep-gui --profile:a=profiles/linux-clang
conan create gnustep-headless --profile:a=profiles/linux-clang
conan create gnustep-cmake --profile:a=profiles/linux-clang
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