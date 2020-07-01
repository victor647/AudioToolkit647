from ObjectTools import WaapiTools, ScriptingTools


# 将选取的每一个对象转换成单独的WorkUnit
def convert_to_work_unit(obj):
    parent = WaapiTools.get_parent_objects(obj, False)[0]
    # 先创建一个不同名的临时文件夹
    work_unit_name = obj['name']
    temp_folder = WaapiTools.create_object(work_unit_name + '_temp', 'Folder', parent, False)
    # 把原有的移动上去
    WaapiTools.move_object(obj, temp_folder)
    # 创建WorkUnit
    new_work_unit = WaapiTools.create_object(work_unit_name, 'WorkUnit', parent, False)
    # 把对象移回来
    WaapiTools.move_object(obj, new_work_unit)
    # 删除临时文件夹
    WaapiTools.delete_object(temp_folder)
