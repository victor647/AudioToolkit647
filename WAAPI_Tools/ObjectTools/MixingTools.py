from Libraries import WaapiTools


# 创建新的bus
def get_or_create_bus(bus_name, parent_bus):
    bus = WaapiTools.find_object_by_name_and_type(bus_name, 'Bus')
    if bus is None:
        bus = WaapiTools.create_object(bus_name, 'Bus', parent_bus, 'replace')
    return bus


# 为对象分配Bus
def set_bus(obj, bus_obj):
    WaapiTools.set_object_property(obj, 'OverrideOutput', True)
    WaapiTools.set_object_reference(obj, 'OutputBus', bus_obj)


# 为对象设定3D开关
def set_spatialization(obj, is3d: bool):
    WaapiTools.set_object_property(obj, 'OverridePositioning', True)
    WaapiTools.set_object_property(obj, '3DSpatialization', 2 if is3d else 0)

