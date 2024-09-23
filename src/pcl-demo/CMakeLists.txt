find_package(PCL REQUIRED COMPONENTS common io search segmentation filters)
include_directories(${PCL_INCLUDE_DIRS})

add_executable(pcl_demo_app
        main.cpp
        pcl_point_types_demo.cpp
)

find_package(PCL CONFIG REQUIRED)
include_directories(${PCL_INCLUDE_DIRS})
link_directories(${PCL_LIBRARY_DIRS})
add_definitions(${PCL_DEFINITIONS})

set(INSTALL_BIN_DIR "${CMAKE_INSTALL_PREFIX}/bin")
set(INSTALL_LIB_DIR "${CMAKE_INSTALL_PREFIX}/lib")

target_link_libraries(pcl_demo_app PRIVATE ${PCL_LIBRARIES})

add_custom_command(TARGET pcl_demo_app
        POST_BUILD
        COMMAND /usr/bin/python3 ${CMAKE_SOURCE_DIR}/scripts/find_and_copy_libs.py pcl_demo_app ${INSTALL_LIB_DIR}
        COMMAND ${CMAKE_COMMAND} -DDEPENDENCIES_FILE=${INSTALL_LIB_DIR}/deb_dependencies.txt -P ${CMAKE_SOURCE_DIR}/cmake/set_deb_dependencies.cmake
        COMMAND ${CMAKE_COMMAND} -E echo "Running CPack to create package..."
        COMMENT "This command will be executed after building ${target}"
        VERBATIM
)
