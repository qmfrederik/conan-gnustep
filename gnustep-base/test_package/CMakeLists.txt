cmake_minimum_required(VERSION 3.16)
project(test_package LANGUAGES C CXX)

find_package(gnustep-base REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.m)
target_link_libraries(${PROJECT_NAME} PRIVATE gnustep-base::gnustep-base)

# Objective C++ needs the same Objective C compiler flags as Objective C
add_executable(test_package_objcxx test_package.mm)
target_link_libraries(test_package_objcxx PRIVATE gnustep-base::gnustep-base)
