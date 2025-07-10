# GNUstep Tutorial application

The GNUstep Tutorial application shows how you can use the GNUstep Conan packages to build a GNUstep application
on Windows and Linux, using CMake and Conan.

Use the following script to build and run the tutorial application from the Liux command line.  This script:
- Runs `conan install` to create a CMake toolchain (`conan_toolchain.cmake`) which enables CMake to find Conan packages
- Configures the application with CMake and builds it
- Uses `. conanrun.sh` to source the environment variables (such as `LD_LIBRARY_PATH`) required to run the application
- And finally runs the application

```bash
conan install conanfile.txt --profile:a=../profiles/windows-clang --output-folder=build/ --conf="tools.env.virtualenv:powershell=pwsh.exe"
cd build/
cmake .. -DCMAKE_TOOLCHAIN_FILE="conan_toolchain.cmake" -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_POLICY_DEFAULT_CMP0091="NEW" -GNinja
cmake --build .
. conanrun.sh
./Tutorial
```
