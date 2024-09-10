from Libraries import WaapiTools


# 创建新的bus
def get_or_create_bus(bus_name: str, parent_bus: dict):
    bus = WaapiTools.find_object_by_name_and_type(bus_name, 'Bus')
    if bus is None:
        bus = WaapiTools.create_object(bus_name, 'Bus', parent_bus, 'replace')
    return bus


# 为对象分配Bus
def set_output_bus(obj: dict, bus_obj: dict):
    WaapiTools.set_object_property(obj, 'OverrideOutput', True)
    WaapiTools.set_object_reference(obj, 'OutputBus', bus_obj)


# 为对象设定3D开关
def set_sound_3d(sound: dict, is3d: bool):
    WaapiTools.set_object_property(sound, 'OverridePositioning', True)
    WaapiTools.set_object_property(sound, '3DSpatialization', 2 if is3d else 0)


# 检查是否分配了Bus
def is_bus_unassigned(obj: dict):
    bus = WaapiTools.get_object_property(obj, 'OutputBus')
    if bus is None:
        return False
    is_master = bus['name'] == 'Master Audio Bus'
    override = WaapiTools.get_object_property(obj, 'OverrideOutput')
    if override:
        return is_master
    # 非override的对象需要检查是否上级已经检查过了
    parent = WaapiTools.get_parent_objects(obj, False)
    if parent and not WaapiTools.get_object_property(parent, 'OutputBus'):
        return is_master
    return False


# 对象的音量等参数是否有调整
def has_fader_edits(obj: dict):
    volume = WaapiTools.get_object_property(obj, 'Volume')
    pitch = WaapiTools.get_object_property(obj, 'Pitch')
    lowpass = WaapiTools.get_object_property(obj, 'Lowpass')
    highpass = WaapiTools.get_object_property(obj, 'Highpass')
    if 'Bus' not in obj['type']:
        gain = WaapiTools.get_object_property(obj, 'MakeUpGain')
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
    param_delta = WaapiTools.get_object_property(obj, param_name)
    WaapiTools.set_object_property(obj, param_name, 0)
    children = WaapiTools.get_child_objects(obj, False)
    for child in children:
        param_base = WaapiTools.get_object_property(child, param_name)
        WaapiTools.set_object_property(child, param_name, param_base + param_delta)
        # 递归应用编辑
        if child['type'] != 'Sound':
            down_mix_fader_param(child, param_name)
