import glob
import json
import os
import re
import shutil
import subprocess
import threading
from pathlib import Path

from elftools.elf.elffile import ELFFile

lock = threading.Lock()


def parse_config(system_name, arch_name):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(script_dir, 'config.json')

    # 打开并读取配置文件
    with open(config_path) as file:
        data = json.load(file)

    # 创建一个字典，按 system_name 和 arch_name 进行索引
    config_dict = {}
    for system in data['configs']:
        system_processors = {}
        for processor in system['system_processor']:
            system_processors[processor['arch_name']] = processor['configs']
        config_dict[system['system_name']] = system_processors

    # 直接获取对应 system_name 和 arch_name 的配置信息
    try:
        configs = config_dict[system_name][arch_name]
        ld_config_file = configs.get('ld_config_file', '')
        default_rpaths = configs.get('default_rpaths', [])
        return ld_config_file, default_rpaths
    except KeyError:
        return None, None


# 从环境变量中读取 LD_LIBRARY_PATH
def get_ld_library_path():
    ld_library_path = os.environ.get('LD_LIBRARY_PATH', '')
    # LD_LIBRARY_PATH 可能包含多个路径，用 : 分隔
    print(ld_library_path)
    paths = ld_library_path.split(':') if ld_library_path else []
    return [path for path in paths if path and os.path.isdir(path)]  # 去掉空路径和无效目录


# 从配置文件 /etc/ld.so.conf 读取额外的库路径
def read_ld_so_conf(ld_config_file):
    paths = []

    if os.path.exists(ld_config_file):
        with open(ld_config_file) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):  # 忽略空行和注释行
                    continue
                if line.startswith('include'):
                    # 处理 include 的情况
                    pattern = line.split()[1]
                    for file in glob.glob(pattern):
                        with open(file) as inc_f:
                            included_paths = [
                                p.strip() for p in inc_f.read().splitlines() if p.strip() and not p.startswith('#')
                            ]
                            paths.extend(included_paths)
                else:
                    paths.append(line)

    return [path for path in paths if os.path.isdir(path)]


def get_library_paths(system_name, arch_name):
    _ld_config_file, _default_rpaths = parse_config(system_name, arch_name)
    result = []

    library_paths = get_ld_library_path()
    for path in library_paths:
        if path not in result:
            result.append(path)

    if _ld_config_file:
        ld_so_conf_path = read_ld_so_conf(_ld_config_file)
        for path in ld_so_conf_path:
            if path not in result:
                result.append(path)

    if _default_rpaths and len(_default_rpaths) > 0:
        for path in _default_rpaths:
            rpath = os.path.join(path)
            if os.path.exists(rpath) and rpath != '/' and rpath not in result:
                result.append(rpath)

    # 去重并保留有效的目录路径
    return result


def scan_library_by_path(path):
    all_libraries = {}
    if os.path.exists(path):
        for root, _dirs, files in os.walk(path):
            for file in files:
                if re.match(r'(lib.*\.so(\.\d+)*|ld-linux-.*\.so(\.\d+)*)', file):
                    lib_path = os.path.join(root, file)
                    all_libraries[file] = lib_path
    return all_libraries


def scan_library_paths(library_paths):
    all_libraries = {}

    for path in library_paths:
        libraries = scan_library_by_path(path)
        all_libraries.update(libraries)

    return all_libraries


def show_cached_libraries(libraries):
    print(f"Total libraries found: {len(libraries)}")
    for lib, path in libraries.items():
        print(f"{lib} => {path}")


def insert_data(filename, data):
    with lock:
        if os.path.exists(filename):
            # 读取现有数据
            with open(filename) as file:
                existing_data = set(file.read().splitlines())
        else:
            existing_data = set()

        # 添加新数据并去重
        new_data = set(data)
        combined_data = existing_data.union(new_data)
        sorted_data = sorted(combined_data)

        # 将去重后的数据写回文件
        with open(filename, 'w') as file:
            file.write('\n'.join(sorted_data))


def resolve_symlink(file_path):
    """递归解析符号链接并记录链接关系"""
    links = []
    while os.path.islink(file_path):
        link_target = os.readlink(file_path)
        links.append((os.path.basename(file_path), os.path.basename(link_target)))
        file_path = os.path.join(os.path.dirname(file_path), link_target)
    return links, file_path


def create_file_links(links, source_file):
    if not os.path.exists(source_file):
        return
    if len(links) < 1:
        return
    target_dir = os.path.dirname(source_file)
    previous_target = os.path.basename(source_file)

    for link, _target in reversed(links):
        link_path = os.path.join(target_dir, link)
        # 使用相对路径创建符号链接
        relative_target = os.path.relpath(os.path.join(target_dir, previous_target), os.path.dirname(link_path))
        if os.path.exists(link_path):
            print(f"symlink existed: {link_path}")
        else:
            os.symlink(relative_target, link_path)
            print(f"Created symlink: {link_path} -> {relative_target}")
        previous_target = link


def copy_file_and_create_links(file_path, target_dir):
    """复制文件并在目标目录内创建符号链接关系"""
    # 解析符号链接，获取链接关系和最终文件路径
    links, original_file = resolve_symlink(file_path)
    # 复制最终的实际文件到目标目录

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    shutil.copy2(original_file, target_dir)
    subprocess.run(
        ['patchelf', '--set-rpath', '$ORIGIN', os.path.join(target_dir, os.path.basename(original_file))], check=True
    )

    if len(links) > 0:
        # 递归创建links关系
        source_file_path = os.path.join(target_dir, os.path.basename(original_file))
        create_file_links(links, source_file_path)


def read_elf_rpath_or_runpath(filename):
    rpaths = []
    dynamic_libraries = set({})
    try:
        with filename.open("rb") as f:
            elf = ELFFile(f)
            dynamic_section = elf.get_section_by_name(".dynamic")
            if not dynamic_section:
                return rpaths, dynamic_libraries

            for tag in dynamic_section.iter_tags():
                if tag.entry.d_tag in ("DT_RPATH", "DT_RUNPATH"):
                    path = None
                    if hasattr(tag, "runpath"):
                        path = tag.runpath
                    if hasattr(tag, "rpath"):
                        path = tag.rpath
                    if path:
                        origin_dir = str(filename.parent.resolve().absolute())
                        expanded_paths = [p.replace("$ORIGIN", origin_dir) for p in path.split(":")]
                        rpaths.extend(expanded_paths)
                for tag in dynamic_section.iter_tags():
                    if tag.entry.d_tag == "DT_NEEDED":
                        dynamic_libraries.add(tag.needed)

    except Exception as e:
        print(f"Error reading {filename}: {e}")
    return list(set(rpaths)), dynamic_libraries


def the_path_is_under_another_path(path, another_path):
    # 先将路径标准化以防有符号链接或相对路径
    another_path = os.path.abspath(another_path)
    path = os.path.abspath(path)
    return path.startswith(another_path)


def find_libs_by_system(all_system_libraries):
    system_libs_name = set({})
    for _lib_name, lib_path in all_system_libraries.items():
        try:
            # 使用 dpkg-query 命令查找库文件所属的包名
            result = subprocess.run(['dpkg-query', '-S', lib_path], capture_output=True, text=True)

            # 检查命令是否成功执行
            if result.returncode == 0:
                output = result.stdout.strip()
                # 提取并返回包名（格式为 '包名:架构'）
                package_name = output.split(':')[0]
                system_libs_name.add(package_name)
        except Exception as e:
            print(f"Package query error : {str(e)}")

    return system_libs_name


def find_libraries_in_paths(current_libraries, _system_libraries_map, _project_libraries_map):
    found_system_libraries_map = {}
    found_project_libraries_map = {}
    missing_libraries_set = set()

    _system_libraries_map_keys = _system_libraries_map.keys()
    _project_libraries_map_keys = _project_libraries_map.keys()

    for lib in current_libraries:
        if lib in _system_libraries_map_keys:
            found_system_libraries_map[lib] = _system_libraries_map[lib]
        elif lib in _project_libraries_map_keys:
            found_project_libraries_map[lib] = _project_libraries_map[lib]
        else:
            missing_libraries_set.add(lib)

    return found_system_libraries_map, found_project_libraries_map, missing_libraries_set


def resolve_all_dependencies(_executable_path, project_build_path, system_name, arch_name):
    library_rpaths = get_library_paths(system_name, arch_name)
    print(f"Total libraries found: {library_rpaths}")
    libraries_map = scan_library_paths(library_rpaths)

    to_process = {_executable_path}
    all_found_project_libraries = {}
    all_found_system_libraries = {}
    all_missing_libraries = set()
    _system_libraries_map = libraries_map
    _project_libraries_map = {}
    _library_rpaths = library_rpaths

    while to_process:
        current_file = to_process.pop()
        current_rpaths, current_libraries = read_elf_rpath_or_runpath(Path(current_file))

        project_rpaths = set({})
        new_rpaths = set({})

        filter_libraries = set()
        _found_project_libraries_keys = all_found_project_libraries.keys()
        _found_system_libraries_keys = all_found_system_libraries.keys()
        for lib in current_libraries:
            if lib not in _found_project_libraries_keys and lib not in _found_system_libraries_keys:
                filter_libraries.add(lib)

        if len(current_rpaths) > 0:
            for rpath in current_rpaths:
                if rpath not in _library_rpaths:
                    if the_path_is_under_another_path(rpath, project_build_path):
                        project_rpaths.add(rpath)
                    else:
                        new_rpaths.add(rpath)

            if len(new_rpaths) > 0:
                new_libraries = scan_library_paths(new_rpaths)
                if len(new_libraries) > 0:
                    _system_libraries_map.update(new_libraries)
                    _library_rpaths = _library_rpaths + list(new_rpaths)

        if len(project_rpaths) > 0:
            new_libraries = scan_library_paths(project_rpaths)
            if len(new_libraries) > 0:
                _project_libraries_map.update(new_libraries)

        found_system_libraries_map, found_project_libraries_map, missing_libraries = find_libraries_in_paths(
            filter_libraries, _system_libraries_map, _project_libraries_map
        )

        all_found_system_libraries.update(found_system_libraries_map)
        all_found_project_libraries.update(found_project_libraries_map)
        all_missing_libraries = all_missing_libraries.union(missing_libraries)
        found_libraries = set(found_system_libraries_map.values()).union(found_project_libraries_map.values())
        to_process.update(found_libraries)

    return all_found_system_libraries, all_found_project_libraries, all_missing_libraries


def gen_dep_file(installed_libs_dir, all_project_libraries, all_system_libraries, deb_dependencies_txt):
    all_project_libraries_paths = set(all_project_libraries.values())

    for lib in all_project_libraries_paths:
        copy_file_and_create_links(lib, installed_libs_dir)

    system_libs_name = find_libs_by_system(all_system_libraries)
    insert_data(deb_dependencies_txt, system_libs_name)


def list_files(directory):
    file_paths = []  # 创建一个空列表来存储文件路径
    for root, _dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(os.path.abspath(file_path))  # 获取文件的绝对路径并添加到列表中
    return file_paths
