import win32api, os
from ObjectTools import WaapiTools, ScriptingTools


# 为每个选中的对象创建一个SoundBank
def create_sound_bank(obj):
    # 创建同名bank
    work_unit = WaapiTools.get_object_from_path('\\SoundBanks\\Default Work Unit')
    new_bank = WaapiTools.create_object(obj['name'], 'SoundBank', work_unit, False)
    # 为bank添加内容
    set_args = {
        'soundbank': new_bank['id'],
        'operation': 'add',
        'inclusions': [
            {
                'object': obj['id'],
                'filter': ['events', 'structures', 'media']
            }
        ]
    }
    WaapiTools.Client.call('ak.wwise.core.soundbank.setInclusions', set_args)


# 获取选中的Bank的大小
def get_bank_size(objects):
    banks = ScriptingTools.filter_objects_by_type(objects, 'SoundBank')
    total_wav_size = total_wem_size = generated_file_count = total_file_count = 0
    unused_files = ''
    for obj in banks:
        get_args = {
            'soundbank': obj['id']
        }
        result = WaapiTools.Client.call('ak.wwise.core.soundbank.getInclusions', get_args)
        for inclusion in result['inclusions']:
            if 'media' in inclusion['filter']:
                get_args = {
                    'from': {
                        'id': [inclusion['object']]
                    },
                    'options': {
                        'return': ['name', 'sound:originalWavFilePath', 'sound:convertedWemFilePath', 'audioSource:language']
                    },
                    'transform': [
                        {
                            'select': ['descendants']
                        },
                        {
                            'where': ['type:isIn', ['AudioFileSource']]
                        }
                    ]
                }
                result = WaapiTools.Client.call('ak.wwise.core.object.get', get_args)
                for audio_source in result['return']:
                    language = audio_source['audioSource:language']['name']
                    if language == 'SFX' or language == 'Chinese':
                        total_file_count += 1
                        wav_path = audio_source['sound:originalWavFilePath']
                        wav_size = os.path.getsize(wav_path) / 1024
                        total_wav_size += wav_size
                        wem_path = audio_source['sound:convertedWemFilePath']
                        if os.path.exists(wem_path):
                            wem_size = os.path.getsize(wem_path) / 1024
                            total_wem_size += wem_size
                            generated_file_count += 1
                        else:
                            unused_files += '  ' + os.path.basename(wav_path) + '\n'
    total_wav_size = round(total_wav_size / 1024, 2)
    total_wem_size = round(total_wem_size / 1024, 2)
    message = f'Original Wav: {total_file_count} files, {total_wav_size}MB\nConverted Wem: {generated_file_count} files, {total_wem_size}MB'
    if unused_files != '':
        message += f'\nFiles or not used or haven\'t been generated:\n{unused_files}'
    win32api.MessageBox(0, message, 'Query Completed!')