# Cross-platform build tools for GNUstep

This repository contains [Conan](https://conan.io/) support for building [GNUstep](https://gnustep.github.io/) on Windows and Linux.

It contains:
- [Conan recipes](https://docs.conan.io/2/reference/conanfile.html) for building [libobjc2](https://github.com/gnustep/libobjc2), [libdispatch](https://github.com/apple/swift-corelibs-libdispatch/), [gnustep-make](https://github.com/gnustep/tools-make) and [gnustep-base](https://github.com/gnustep/libs-base)
- [Conan profiles](https://docs.conan.io/2/reference/config_files/profiles.html) for building using clang on Windows and Linux

On Windows, this repository takes the approach of building GNUstep using the Windows-native LLVM (clang) compiler. It uses MSYS2 to get a Bash shell, which allows running the scripts required to configure and build GNUstep, and does not use the MSYS2 compiler toolchain.

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
conan create libobjc2 --profile:a=profiles/windows-clang
conan create libdispatch --profile:a=profiles/windows-clang
conan create gnustep-make --profile:a=profiles/windows-clang
conan create gnustep-base --profile:a=profiles/windows-clang
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
conan create libobjc2 --profile:a=profiles/linux-clang
conan create libdispatch --profile:a=profiles/linux-clang
conan create gnustep-make --profile:a=profiles/linux-clang
conan create gnustep-base --profile:a=profiles/linux-clang
conan create gnustep-cmake --profile:a=profiles/linux-clang
```