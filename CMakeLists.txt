cmake_minimum_required(VERSION 3.21)

if (UNIX)
    set(CMAKE_INSTALL_RPATH "$ORIGIN/../lib:$ORIGIN:$ORIGIN:/lib")
endif ()

project(cmake-vcpkg-demo)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_INSTALL_PREFIX "/opt/${PROJECT_NAME}")

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
list(APPEND CMAKE_PREFIX_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

include(VcpkgConfig)
include(PackagingInit)
include(PackagingSetupDependencies)

add_subdirectory(src)

