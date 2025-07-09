conan install conanfile.txt --profile:a=../profiles/linux-clang --output-folder=build/
cd build/
CC=clang CXX=clang++ LDFLAGS="-fuse-ld=lld" cmake .. -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Release
cmake --build .
