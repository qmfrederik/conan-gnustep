cmake_minimum_required(VERSION 3.16)
project(gnustep LANGUAGES C)

find_package(gnustep-base REQUIRED)
find_package(gnustep-gui REQUIRED)

add_library(gnustep::gnustep INTERFACE IMPORTED)
target_link_libraries(gnustep::gnustep INTERFACE gnustep-base::gnustep-base)
target_link_libraries(gnustep::gnustep INTERFACE gnustep-gui::gnustep-gui)
