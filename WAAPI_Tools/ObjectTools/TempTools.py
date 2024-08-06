from Libraries import WaapiTools
from ObjectTools import EventTools
from Threading.BatchProcessor import BatchProcessor


def temp_tool(objects: list):
    batch_processor = BatchProcessor(objects, temp_action, '临时操作')
    batch_processor.start()


def temp_action(obj):
    if obj['type'] == 'Event' and obj['name'].endswith('_1P'):
        actions = WaapiTools.get_child_objects(obj, False)
        for action in actions:
            old_target = WaapiTools.get_object_property(action, 'Target')
            new_target_name = old_target['name'].replace('_3P', '_1P')
            new_targets = WaapiTools.find_all_objects_by_name(new_target_name)
            if len(new_targets) > 0:
                EventTools.change_action_target(action, new_targets[0])




