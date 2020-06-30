from ObjectTools import WaapiTools, ScriptingTools


def rename_to_lower_case(client, obj):
    new_name = obj['name'].lower()
    if new_name != obj['name']:
        WaapiTools.rename_object(client, obj, new_name)


def rename_to_title_case(client, obj):
    new_name = obj['name'].title()
    if new_name != obj['name']:
        WaapiTools.rename_object(client, obj, new_name)


def rename_to_upper_case(client, obj):
    new_name = obj['name'].upper()
    if new_name != obj['name']:
        WaapiTools.rename_object(client, obj, new_name)