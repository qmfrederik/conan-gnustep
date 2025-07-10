cmake_minimum_required(VERSION 3.10)

project(Tutorial)

find_package(libobjc2)
find_package(GNUstep)

add_executable(Tutorial main.m)
target_link_libraries(Tutorial GNUstep::Base)
