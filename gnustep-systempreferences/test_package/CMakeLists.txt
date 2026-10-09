cmake_minimum_required(VERSION 3.16)
project(test_package LANGUAGES C)

find_package(gnustep-systempreferences REQUIRED CONFIG)
find_package(gnustep-gui REQUIRED CONFIG)
find_package(gnustep-base REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.m)
target_link_libraries(${PROJECT_NAME} PRIVATE
    gnustep-systempreferences::gnustep-systempreferences
    gnustep-gui::gnustep-gui
    gnustep-base::gnustep-base)
