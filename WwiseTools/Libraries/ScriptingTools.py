import fnmatch
from Libraries import WaapiTools


# 在对象中筛选特定类型的
def filter_objects_by_type(objects: list, filter_type: str):
    if filter_type == 'All':
        return objects
    remaining_objects = [obj for obj in objects if obj['type'] == filter_type]
    return remaining_objects


# 在对象中排除特定类型的
def exclude_objects_by_type(objects: list, filter_type: str):
    if filter_type == 'All':
        return []
    remaining_objects = [obj for obj in objects if obj['type'] != filter_type]
    return remaining_objects


# 在对象中筛选名称包含特定字符的
def filter_objects_by_name(objects: list, filter_name: str, case_sensitive: bool):
    objects_filtered = []
    for obj in objects:
        # 查找*和?
        if fnmatch.fnmatch(obj['name'], filter_name):
            objects_filtered.append(obj)
        elif case_sensitive:
            if filter_name in obj['name']:
                objects_filtered.append(obj)
        else:
            if filter_name.lower() in obj['name'].lower():
                objects_filtered.append(obj)
    return objects_filtered


# 在对象中筛选名称包含特定字符的
def exclude_objects_by_name(objects: list, filter_name: str, case_sensitive: bool):
    if filter_name == '':
        return []
    objects_filtered = []
    for obj in objects:
        match = False
        # 查找*和?
        if fnmatch.fnmatch(obj['name'], filter_name):
            match = True
        elif case_sensitive:
            if filter_name in obj['name']:
                match = True
        else:
            if filter_name.lower() in obj['name'].lower():
                match = True
        # 全部不满足才加入
        if not match:
            objects_filtered.append(obj)

    return objects_filtered


# 获取Originals根目录
def get_originals_folder():
    project_path = WaapiTools.get_project_directory()
    project_dir = trim_path_from_right(project_path)
    return project_dir + '\\Originals\\SFX\\'


# 从右侧截取路径
def trim_path_from_right(path: str, levels=1):
    for index in range(levels):
        path = path[:path.rindex('\\')]
    return path


# 从左侧截取路径
def trim_path_from_left(path: str, levels=1):
    for index in range(levels + 1):
        path = path[path.index('\\') + 1:]
    return path


# 从右侧保留路径
def get_path_from_right(path: str, levels=1):
    while path.count('\\') > levels:
        path = path[path.rindex('\\'):]
    return path


# 从左侧保留路径
def get_path_from_left(path: str, levels=1):
    while path.count('\\') > levels:
        path = path[:path.index('\\') + 1]
    return path




