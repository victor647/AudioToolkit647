from Libraries import WaapiTools


def rename_to_lower_case(obj):
    new_name = obj['name'].lower()
    if new_name != obj['name']:
        WaapiTools.rename_object(obj, new_name)


def rename_to_title_case(obj):
    new_name = obj['name'].title()
    if new_name != obj['name']:
        WaapiTools.rename_object(obj, new_name)


def rename_to_upper_case(obj):
    new_name = obj['name'].upper()
    if new_name != obj['name']:
        WaapiTools.rename_object(obj, new_name)


# 移除对象末尾_后面的名字
def remove_suffix(obj):
    old_name = obj['name']
    splits = old_name.split('_')
    suffix_length = len(splits[-1]) + 1
    new_name = old_name[:-suffix_length]
    WaapiTools.rename_object(obj, new_name)


# 在对象上添加RTPC控制
def add_rtpc(obj):
    pass
