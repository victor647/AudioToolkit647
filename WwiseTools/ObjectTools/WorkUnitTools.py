from ObjectTools import WaapiTools, ScriptingTools


# 将选取的每一个对象转换成单独的WorkUnit
def convert_to_work_unit(client, obj):
    create_path = ScriptingTools.trim_path_from_right(obj['path'])
    new_work_unit = WaapiTools.create_object(client, obj['name'], 'WorkUnit', create_path, False)
    WaapiTools.move_object(client, obj, new_work_unit)
