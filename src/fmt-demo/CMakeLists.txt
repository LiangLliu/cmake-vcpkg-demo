find_package(fmt CONFIG REQUIRED)

add_executable(fmt-demo main.cpp)
target_link_libraries(fmt-demo PRIVATE fmt::fmt)

add_cpack_custom_install_target(fmt-demo)