import ScriptingTools


def rename_to_lower_case(client):
    selected_objects = ScriptingTools.get_selected_objects(client)
    for obj in selected_objects:
        new_name = obj['name'].lower()
        if new_name != obj['name']:
            ScriptingTools.rename_object(client, obj, new_name)


def rename_to_camel_case(client):
    selected_objects = ScriptingTools.get_selected_objects(client)
    for obj in selected_objects:
        new_name = obj['name'].title()
        if new_name != obj['name']:
            ScriptingTools.rename_object(client, obj, new_name)