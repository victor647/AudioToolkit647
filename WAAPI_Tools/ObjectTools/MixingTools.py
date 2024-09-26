from Libraries import WAAPI, ProjectConventions


# 判断一个对象是否是最上层可混音对象
def is_mixing_root(obj: dict):
    parent = WAAPI.get_parent_object(obj)
    if parent:
        parent_type = parent['type']
        if parent_type == 'WorkUnit' or parent_type == 'Folder':
            return is_mixing_root(parent)
        return False
    return True


# 创建新的bus
def get_or_create_bus(bus_name: str, parent_bus: dict):
    bus = WAAPI.find_object_by_name_and_type(bus_name, 'Bus')
    if bus is None:
        bus = WAAPI.create_object(bus_name, 'Bus', parent_bus, 'replace')
    return bus


# 为对象分配Bus
def set_output_bus(obj: dict, bus_obj: dict):
    print(f"Set output bus of {obj['type']} [{obj['name']}] to {bus_obj['name']}")
    WAAPI.set_object_property(obj, 'OverrideOutput', True)
    return WAAPI.set_object_reference(obj, 'OutputBus', bus_obj)


# 根据对象类别自动分配Bus
def auto_assign_bus_by_category(obj: dict):
    category = ProjectConventions.get_object_category(obj)
    if category:
        bus = WAAPI.find_object_by_name_and_type(category, 'Bus')
        if bus:
            return set_output_bus(obj, bus)
    return False


# 为对象设定3D开关
def set_sound_3d(sound: dict, is3d: bool):
    WAAPI.set_object_property(sound, 'OverridePositioning', True)
    WAAPI.set_object_property(sound, '3DSpatialization', 2 if is3d else 0)


# 对象的音量等参数是否有调整
def has_fader_edits(obj: dict):
    volume = WAAPI.get_object_property(obj, 'Volume')
    pitch = WAAPI.get_object_property(obj, 'Pitch')
    lowpass = WAAPI.get_object_property(obj, 'Lowpass')
    highpass = WAAPI.get_object_property(obj, 'Highpass')
    if 'Bus' not in obj['type']:
        gain = WAAPI.get_object_property(obj, 'MakeUpGain')
    else:
        gain = 0
    return volume != 0 or pitch != 0 or lowpass != 0 or highpass != 0 or gain != 0


# 将混音参数传递到下一层
def down_mix_fader(obj: dict):
    down_mix_fader_param(obj, 'Volume')
    down_mix_fader_param(obj, 'Pitch')
    down_mix_fader_param(obj, 'Lowpass')
    down_mix_fader_param(obj, 'Highpass')
    # Bus类对象不包含MakeUpGain属性
    if 'Bus' not in obj['type']:
        down_mix_fader_param(obj, 'MakeUpGain')


def down_mix_fader_param(obj: dict, param_name: str):
    param_delta = WAAPI.get_object_property(obj, param_name)
    WAAPI.set_object_property(obj, param_name, 0)
    children = WAAPI.get_child_objects(obj, False)
    for child in children:
        param_base = WAAPI.get_object_property(child, param_name)
        WAAPI.set_object_property(child, param_name, param_base + param_delta)
        # 递归应用编辑
        if child['type'] != 'Sound':
            down_mix_fader_param(child, param_name)
