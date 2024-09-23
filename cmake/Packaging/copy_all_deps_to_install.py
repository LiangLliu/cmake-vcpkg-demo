import argparse
import os

from common import copy_file_and_create_links, resolve_all_dependencies


def copy_all_lib(installed_libs_dir, all_project_libraries, all_system_libraries):
    all_project_libraries_paths = set(all_project_libraries.values())
    all_system_libraries_paths = set(all_system_libraries.values())

    all_libs = all_project_libraries_paths.union(all_system_libraries_paths)
    print("installed_libs_dir: ", installed_libs_dir)
    for lib in all_libs:
        copy_file_and_create_links(lib, installed_libs_dir)


def copy_all_deps_to_install(bin_file_path, libs_to_temp_dir, build_path, system_name, arch_name, cmake_sysroot):
    system_libraries, project_libraries, missing_libraries = resolve_all_dependencies(
        bin_file_path, build_path, system_name, arch_name, cmake_sysroot
    )

    print("-----------------all_missing_libraries------------------")
    for lib in missing_libraries:
        print(f"{lib}")

    copy_all_lib(libs_to_temp_dir, system_libraries, project_libraries)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy dependencies to installation directory.")
    parser.add_argument("--executable", required=True, help="Path to the executable.")
    parser.add_argument("--system_name", required=True, help="System name (e.g., Linux).")
    parser.add_argument("--arch_name", required=True, help="Architecture name (e.g., x86_64).")
    parser.add_argument(
        "--cmake_sysroot", required=False, nargs='?', const=None, default=None, help="CMake sysroot path (optional)."
    )
    parser.add_argument("--project_build_path", required=True, help="Path to the project build.")
    parser.add_argument("--temp_dir", required=True, help="Temporary directory for copying libs.")

    args = parser.parse_args()

    copy_libs_to_temp_dir = os.path.join(args.project_build_path, args.temp_dir)

    copy_all_deps_to_install(
        args.executable,
        copy_libs_to_temp_dir,
        args.project_build_path,
        args.system_name,
        args.arch_name,
        args.cmake_sysroot,
    )
