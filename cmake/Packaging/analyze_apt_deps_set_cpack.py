import argparse
import os
import re

from common import find_libs_by_system, resolve_all_dependencies


def update_cpack_debian_package_depends(cpack_config_path, dependencies):
    if not os.path.isfile(cpack_config_path):
        raise FileNotFoundError(f"File not found: {cpack_config_path}")

    with open(cpack_config_path) as file:
        content = file.read()

    pattern = re.compile(r'(set\s*\(\s*CPACK_DEBIAN_PACKAGE_DEPENDS\s*"[^"]*"\s*\))')
    match = pattern.search(content)

    new_value = ','.join(sorted(dependencies))
    if match:
        current_value = match.group(0)
        current_value_str = re.search(r'set\s*\(\s*CPACK_DEBIAN_PACKAGE_DEPENDS\s*"([^"]*)"', current_value)
        if current_value_str:
            current_dependencies = current_value_str.group(1).strip()
            if current_dependencies:
                existing_list = set(current_dependencies.split(','))
                combined_list = existing_list.union(dependencies)
                new_value = ','.join(sorted(combined_list))
        updated_content = pattern.sub(f'set(CPACK_DEBIAN_PACKAGE_DEPENDS "{new_value}")', content)
    else:
        updated_content = content + f'\nset(CPACK_DEBIAN_PACKAGE_DEPENDS "{new_value}")'

    with open(cpack_config_path, 'w') as file:
        file.write(updated_content)


def analyze_apt_deps_set_cpack(
        executable_path, project_build_path, cpack_cmake_file_path, system_name, arch_name
):
    system_libraries, _, all_missing_libraries = resolve_all_dependencies(
        executable_path, project_build_path, system_name, arch_name
    )

    system_libs_name = find_libs_by_system(system_libraries)
    print(system_libs_name)

    update_cpack_debian_package_depends(cpack_cmake_file_path, list(system_libs_name))

    print("-----------------missing libraries start------------------")
    for lib in all_missing_libraries:
        print(f"{lib}")
    print("-----------------missing libraries end--------------------")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy dependencies to installation directory.")
    parser.add_argument("--executable", required=True, help="Path to the executable.")
    parser.add_argument("--system_name", required=True, help="System name (e.g., Linux).")
    parser.add_argument("--arch_name", required=True, help="Architecture name (e.g., x86_64).")
    parser.add_argument("--project_build_path", required=True, help="Path to the project build.")
    parser.add_argument("--cpack_config_path", required=True, help="Cpack config path")

    args = parser.parse_args()

    analyze_apt_deps_set_cpack(
        args.executable,
        args.project_build_path,
        args.cpack_config_path,
        args.system_name,
        args.arch_name
    )
