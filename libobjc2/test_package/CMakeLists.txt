cmake_minimum_required(VERSION 3.16)
project(test_package LANGUAGES C)

find_package(libobjc2 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE libobjc2::libobjc2)
