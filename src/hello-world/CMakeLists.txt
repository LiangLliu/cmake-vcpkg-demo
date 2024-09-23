find_package(fmt CONFIG REQUIRED)

add_executable(HelloWorld main.cpp)
target_link_libraries(HelloWorld PRIVATE fmt::fmt)

add_cpack_custom_install_target(HelloWorld)