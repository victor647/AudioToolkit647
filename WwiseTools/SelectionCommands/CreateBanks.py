import ScriptingTools


# 为每个选中的ActorMixer创建一个SoundBank
def create_banks(client, objects):
    options = {
        'return': 'id'
    }
    for obj in objects:
        bank_name = obj['name']
        create_args = {
            'parent': '\\SoundBanks\\Default Work Unit',
            'type': 'SoundBank',
            'name': bank_name,
            'onNameConflict': 'replace'
        }
        bank_result = client.call('ak.wwise.core.object.create', create_args, options)
        obj_guid = obj['id']
        set_args = {
            'soundbank': bank_result['id'],
            'operation': 'add',
            'inclusions': [
                {
                    'object': obj_guid,
                    'filter': ['events', 'structures', 'media']
                }
            ]
        }
        client.call('ak.wwise.core.soundbank.setInclusions', set_args)


