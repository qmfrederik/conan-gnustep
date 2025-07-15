find_package(PkgConfig)

find_package(libobjc2 REQUIRED)
find_package(gnustep-base REQUIRED)
find_package(libdispatch REQUIRED)

# These variables should always be set when using GNUstep
list(APPEND GNUSTEP_COMPILE_DEFINITIONS "GNUSTEP=1")
list(APPEND GNUSTEP_COMPILE_DEFINITIONS "GNUSTEP_BASE_LIBRARY=1")
list(APPEND GNUSTEP_COMPILE_DEFINITIONS "GNUSTEP_RUNTIME=1")

list(APPEND GNUSTEP_COMPILE_DEFINITIONS $<$<CONFIG:Debug>:GSWARN>)
list(APPEND GNUSTEP_COMPILE_DEFINITIONS $<$<CONFIG:Debug>:GSDIAGNOSE>)

# On Windows, GNUSTEP_WITH_DLL is always set
if(WIN32)
    list(APPEND GNUSTEP_COMPILE_DEFINITIONS "GNUSTEP_WITH_DLL=1")
endif()

message(STATUS "GNUstep configuration:")

set(GNUSTEP_BASE_PKG_CONFIG "${gnustep-base_LIB_DIRS_RELEASE}/pkgconfig/gnustep-base.pc")
file(STRINGS ${GNUSTEP_BASE_PKG_CONFIG} GNUSTEP_BASE_CFLAGS REGEX "Cflags")

# Make sure we are using native Objective C exceptions
if ("${GNUSTEP_BASE_CFLAGS}" MATCHES "-D_NATIVE_OBJC_EXCEPTIONS")
    message(STATUS "  Using native Objective-C exceptions")
    list(APPEND GNUSTEP_COMPILE_DEFINITIONS "_NATIVE_OBJC_EXCEPTIONS=1")
    list(APPEND GNUSTEP_COMPILE_OPTIONS "-fexceptions")
    list(APPEND GNUSTEP_COMPILE_OPTIONS "-fobjc-exceptions")
else()
    message(FATAL_ERROR " GNUstep is not configured to use native Objective-C exceptions")
endif()

# Make sure we are using the non-fragile ABI
if ("${GNUSTEP_BASE_CFLAGS}" MATCHES "-D_NONFRAGILE_ABI")
    message(STATUS "  Using the non-fragile ABI")
    list(APPEND GNUSTEP_COMPILE_DEFINITIONS "_NONFRAGILE_ABI=1")
else()
    message(FATAL_ERROR " GNUstep is not configured to use the non-fragile ABI")
endif()

# Make sure we are using objective C runtime 2.0 or later
string(REGEX MATCH "-fobjc-runtime=gnustep-([0-9\.]*)" OBJECTIVE_C_RUNTIME "${GNUSTEP_BASE_CFLAGS}")
if(OBJECTIVE_C_RUNTIME)
    set(GNUSTEP_OBJECTIVE_C_RUNTIME "${CMAKE_MATCH_1}")

    if (GNUSTEP_OBJECTIVE_C_RUNTIME VERSION_GREATER_EQUAL 2.0)
        message(STATUS "  Runtime ABI gnustep-${GNUSTEP_OBJECTIVE_C_RUNTIME}")
        list(APPEND GNUSTEP_COMPILE_OPTIONS "${OBJECTIVE_C_RUNTIME}")
    else ()
        message(FATAL_ERROR "  Using outdated GNUstep runtime ABI gnustep-${GNUSTEP_OBJECTIVE_C_RUNTIME}")
    endif()
else()
    message(FATAL_ERROR "  Could not determine the Objective C runtime.")
endif()

# Make sure we are using a constant string class
string(REGEX MATCH "-fconstant-string-class=([a-zA-Z]*)" CONSTANT_STRING_CLASS "${GNUSTEP_BASE_CFLAGS}")
if(CONSTANT_STRING_CLASS)
    set(GNUSTEP_CONSTANT_STRING "${CMAKE_MATCH_1}")
    message(STATUS "  Constant string class ${GNUSTEP_CONSTANT_STRING}")
    list(APPEND GNUSTEP_COMPILE_OPTIONS "${CONSTANT_STRING_CLASS}")
else()
    message(WARNING "  Could not identify the constant string class, defaulting to NSConstantString")
    list(APPEND GNUSTEP_COMPILE_OPTIONS "-fconstant-string-class=NSConstantString")
endif()

# Make sure we are using the blocks runtime
if ("${GNUSTEP_BASE_CFLAGS}" MATCHES "-fblocks")
    message(STATUS "  Blocks support enabled")
    list(APPEND GNUSTEP_COMPILE_OPTIONS "-fblocks")
else()
    message(FATAL_ERROR " GNUstep is not configured with blocks support")
endif()

# Find the Objective-C and libs-base headers
add_library(GNUstep::ObjC INTERFACE IMPORTED)
target_include_directories(GNUstep::ObjC INTERFACE ${libobjc2_INCLUDE_DIRS})
target_link_libraries(GNUstep::ObjC INTERFACE ${libobjc2_LIBRARIES})

add_library(GNUstep::Base INTERFACE IMPORTED)
target_link_libraries(GNUstep::Base INTERFACE gnustep-base::gnustep-base libdispatch::libdispatch libobjc2::libobjc2)
target_compile_options(GNUstep::Base INTERFACE ${GNUSTEP_COMPILE_OPTIONS})
target_compile_definitions(GNUstep::Base INTERFACE ${GNUSTEP_COMPILE_DEFINITIONS})
target_include_directories(GNUstep::Base INTERFACE ${gnustep-base_INCLUDE_DIRS})
target_link_libraries(GNUstep::Base INTERFACE GNUstep::ObjC)
