find_package(Boost REQUIRED COMPONENTS filesystem)

add_executable(boost-filesystem-demo main.cpp)
target_link_libraries(boost-filesystem-demo PRIVATE Boost::filesystem)

add_cpack_custom_install_target(boost-filesystem-demo)
