import os, sys, subprocess

bank_path = os.path.join(os.path.dirname(__file__), 'GeneratedSoundBanks')
pck_path = sys.argv[1] if len(sys.argv) > 1 else bank_path
packager_path = os.path.join(os.getenv('WWISEROOT'), 'Authoring\\x64\\Release\\bin\\FilePackager.Console.exe')

for platform in os.listdir(bank_path):
    platform_path = os.path.join(bank_path, platform)
    info_path = os.path.join(platform_path, 'SoundBanksInfo.xml')
    packager_command = f'\"{packager_path}\" -generate -info {info_path}'
    if os.path.isfile(platform_path):
        continue
    for root_file in os.listdir(platform_path):
        full_path = os.path.join(platform_path, root_file)
        # language banks
        if os.path.isdir(full_path):
            language = root_file
            for file in os.listdir(full_path):
                # one pck for each bank, including streamed files
                if file.endswith('.bnk'):
                    bank_name = file[:-4]
                    pck_output = os.path.join(pck_path, platform, language, bank_name + '.pck')
                    command = f'{packager_command} -output {pck_output} -banks {bank_name} -languages {language}'
                    os.system(command)
            # one pck for all the external sources for each language
            # pck_output = os.path.join(pck_path, platform, language, 'ExternalSources.pck')
            # command = f'{packager_command} -output_ext {pck_output} -languages {language}'
            # print(command)
            # os.system(command)
        # SFX banks
        elif root_file.endswith('.bnk'):
            bank_name = root_file[:-4]
            pck_output = os.path.join(pck_path, platform, bank_name + '.pck')
            command = f'{packager_command} -output {pck_output} -banks {bank_name}'
            os.system(command)


