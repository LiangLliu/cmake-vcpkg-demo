# cmake-vcpkg-demo

``cmake-vcpkg-demo`` is a comprehensive example project demonstrating how to utilize modern C++ project tools. It
integrates CMake, Vcpkg, and CPack, supporting automated builds, dependency management, and packaging. The project not
only supports standard .deb package generation but also allows the creation of a fully self-contained package that
includes all dependency libraries, making it easy to run the application in different environments without installing
additional system libraries.

### Technologies Used:

* ``CMake Preset``: Utilizes CMake's Preset feature to simplify and automate project build configuration. Preset
  provides
  unified build settings, enabling developers to easily build the project across different platforms.
* ``Vcpkg Dependency Management``: Vcpkg is a popular C++ package management tool used to manage and build open-source
  libraries. The project leverages Vcpkg to handle cross-platform dependencies, ensuring consistent builds with easy
  third-party library integration.
* ``CPack Packaging Tool``: Uses CPack to package the project, with support for generating .deb packages, enabling
  distribution and installation on Debian-based systems like Ubuntu.
* ``APT Dependency Analysis``: The project includes automatic analysis of APT dependencies. When generating .deb
  packages, it analyzes the executable and libraries to determine required system dependencies, which are then
  automatically added to the Depends field of the Debian control file, ensuring the necessary libraries are installed
  during package installation.
* ``Full Package Support``: n addition to relying on system libraries, the project also supports creating "full
  packages," where all dependency libraries are bundled into the project's lib directory. This allows users to run the
  application directly without needing to install system libraries. The project recursively analyzes executable
  dependencies and copies required libraries into the package, ensuring portability.
* ``Dynamic Library Dependency Handling Script``: A Python script is used to analyze ELF files (executables and dynamic
  libraries), extracting RPATH and RUNPATH, and recursively locating and copying necessary libraries. This enables the
  creation of a fully self-contained package with all required dependencies.

### Dependencies

* ubuntu
* cmake
* ninja
* python3 && pyelftools
* patchelf

### Run

```shell
# config
cmake --preset=release

# build
cmake --build --preset=release

# packaging
cpack --preset=release
```
