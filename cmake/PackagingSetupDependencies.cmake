function(check_package_dependencies)
    # 检查python3解释器是否存在
    find_program(PYTHON3_EXECUTABLE python3)
    if (NOT PYTHON3_EXECUTABLE)
        message(FATAL_ERROR "Python3 is required but was not found. Please install it using \n apt install python3 \n")
    endif ()

    # 检查pyyaml和pyelftools是否已安装
    execute_process(
            COMMAND ${PYTHON3_EXECUTABLE} -c "import elftools"
            RESULT_VARIABLE _PYTHON_MODULES_CHECK
            OUTPUT_QUIET ERROR_QUIET)
    if (_PYTHON_MODULES_CHECK)
        message(
                FATAL_ERROR
                "Python modules 'pyyaml' and 'pyelftools' are required but were not found. Please install them using \n pip install pyelftools \n"
        )
    endif ()

    # 检查patchelf工具是否存在
    find_program(PATCHELF_EXECUTABLE patchelf)
    if (NOT PATCHELF_EXECUTABLE)
        message(FATAL_ERROR "patchelf is required but was not found. Please install it using \n apt install patchelf \n")
    endif ()
endfunction()

function(package_full_deps target)
    add_custom_command(
            TARGET ${target}
            POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E echo
            "Recursively query all dependencies and prepare to copy them to the installation directory"
            COMMAND
            /usr/bin/python3 ${CMAKE_SOURCE_DIR}/cmake/Packaging/copy_all_deps_to_install.py --executable
            $<TARGET_FILE:${target}> --system_name ${CMAKE_SYSTEM_NAME} --arch_name ${CMAKE_SYSTEM_PROCESSOR} --cmake_sysroot
            ${CMAKE_SYSROOT} --project_build_path ${CMAKE_BINARY_DIR} --temp_dir packaging/${target}/libs
            COMMENT "Recursively query all dependencies and prepare to copy them to the installation directory"
            VERBATIM)

    set(CUSTOM_INSTALL_PATH "${CMAKE_INSTALL_PREFIX}/lib")
    set(DEPENDENCY_FILE_PATH "${CMAKE_BINARY_DIR}/packaging/${target}/libs")

    configure_file(${CMAKE_SOURCE_DIR}/cmake/Packaging/custom_install.cmake.in
            ${CMAKE_BINARY_DIR}/packaging/${target}/custom_${target}_install.cmake @ONLY)

    install(SCRIPT ${CMAKE_BINARY_DIR}/packaging/${target}/custom_${target}_install.cmake)
endfunction()

function(package_apt_managed_system_deps target)
    add_custom_command(
            TARGET ${target}
            POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E echo "Analyze all dependencies and let apt manage system dependencies"
            COMMAND
            /usr/bin/python3 ${CMAKE_SOURCE_DIR}/cmake/Packaging/analyze_apt_deps_set_cpack.py --executable
            $<TARGET_FILE:${target}> --system_name ${CMAKE_SYSTEM_NAME} --arch_name ${CMAKE_SYSTEM_PROCESSOR} --cmake_sysroot
            ${CMAKE_SYSROOT} --project_build_path ${CMAKE_BINARY_DIR} --cpack_config_path
            ${CMAKE_BINARY_DIR}/CPackConfig.cmake
            COMMENT "Analyze all dependencies and let apt manage system dependencies"
            VERBATIM)
endfunction()

function(add_cpack_custom_install_target target)
    if (CONFIG_ENABLE_PACKAGING)

        check_package_dependencies()

        install(
                TARGETS ${target}
                RUNTIME DESTINATION bin # if the target is executable file
                LIBRARY DESTINATION lib # if the target is shared(*.so) library
                ARCHIVE DESTINATION lib # if the target is static(*.a) library
        )

        if (CONFIG_ENABLE_FULL_PACKAGING)
            package_full_deps(${target})
        else ()
            package_apt_managed_system_deps(${target})
        endif ()

    endif ()
endfunction()
