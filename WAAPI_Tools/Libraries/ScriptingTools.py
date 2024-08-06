import fnmatch
import re

from Libraries import WaapiTools


# 根据条件筛选或筛除列表中对象
def filter_objects(objects: list, filter_input: str,
                   case_sensitive: bool, match_whole_word: bool, use_regular_expression: bool,
                   filter_type: str, filter_by_name: bool, inclusion: bool):
    objects_filtered = []
    for obj in objects:
        if (filter_type != '全部类型') and obj['type'] != filter_type:
            continue
        match = False

        objKey = obj['name'] if filter_by_name else obj['path']
        # 查找*和?
        if fnmatch.fnmatch(objKey, filter_input):
            match = True
        else:
            filter_input_for_match = filter_input if case_sensitive else filter_input.lower()
            objKey = objKey if case_sensitive else objKey.lower()

            if match_whole_word:
                if filter_input_for_match == objKey:
                    match = True
            elif use_regular_expression:
                filter_input_for_match = trans_to_regular_expression(filter_input_for_match)
                try:
                    if re.search(filter_input_for_match, objKey):
                        match = True
                except:
                    print("regular match except")
            else:
                if filter_input_for_match in objKey:
                    match = True

        if (inclusion and match) or (not inclusion and not match):
            objects_filtered.append(obj)

    return objects_filtered


# 在对象中筛选未启用的
def filter_objects_by_inclusion(objects: list, inclusion: bool):
    objects_filtered = []
    for obj in objects:
        # 音频资源没有inclusion选项
        if obj['type'] == 'AudioFileSource':
            continue
        if WaapiTools.get_object_property(obj, 'Inclusion') == inclusion:
            objects_filtered.append(obj)
    return objects_filtered


# 在对象中筛选特定类型的
def filter_objects_by_type(objects: list, filter_type: str):
    if filter_type == 'All':
        return objects
    remaining_objects = [obj for obj in objects if obj['type'] == filter_type]
    return remaining_objects


# 获取Originals根目录
def get_originals_folder():
    project_path = WaapiTools.get_project_directory()
    project_dir = trim_path_from_right(project_path)
    return project_dir + '\\Originals\\'


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


# 简化以支持正则表达式:
# 1. 支持&
def trans_to_regular_expression(input: str):
    # 去空格
    input.replace(' ', '')
    # 处理&
    idx = input.find('&')
    if idx != -1:
        try:
            idx_left_begin = idx_left_end = idx - 1;
            idx_right_begin = idx_right_end = idx + 1;
            # 获取&左侧的字符串下标范围
            column_right_count = 0
            while idx_left_begin > 0:
                c = input[idx_left_begin]
                if c == ')':
                    column_right_count += 1
                if c == '(':
                    column_right_count -= 1
                if (c in ")*|") and (column_right_count == 0):
                    idx_left_begin += 1
                    break
                idx_left_begin -= 1
            # 获取&右侧的字符串下标范围
            column_left_count = 0
            while idx_right_end < len(input)-1:
                c = input[idx_right_end]
                if c == ')':
                    column_left_count -= 1
                if c == '(':
                    column_left_count += 1
                if (c in "(*|") and (column_left_count == 0):
                    break
                idx_right_end += 1
            # 替换字符串
            idx_increment = 0
            str_list = list(input)
            str_list.insert(idx_left_begin + idx_increment, "(?=.*")
            idx_increment += 1
            str_list.insert(idx_left_end + idx_increment + 1, ")")
            idx_increment += 1
            str_list.pop(idx + idx_increment)
            idx_increment += -1
            str_list.insert(idx_right_begin + idx_increment, "(?=.*")
            idx_increment += 1
            str_list.insert(idx_right_end + idx_increment + 1, ")")
            input = ''.join(str_list)
            # 继续处理一下个&
            input = trans_to_regular_expression(input)
        except:
            print("trans_to_regular_expression error")
    return input


# 遍历子对象
def iterate_child_sound_objects(obj, action):
    if obj['type'] == 'Sound':
        action(obj)
    else:
        for child in WaapiTools.get_child_objects(obj, False):
            iterate_child_sound_objects(child, action)