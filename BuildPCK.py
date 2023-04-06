import os, sys, subprocess

bank_path = os.path.join(os.path.dirname(__file__), 'GeneratedSoundBanks')
pck_path = sys.argv[1]
info_path = os.path.join(bank_path, 'SoundBanksInfo.xml')
packager_path = os.path.join(os.getenv('WWISEROOT'), 'Authoring\\x64\\Release\\bin\\Tools\\FilePackager.Console.exe')
packager_command = '\"{}\" -generate -info {} '.format(packager_path, info_path)

for root_file in os.listdir(bank_path):
    full_path = os.path.join(bank_path, root_file)
    # language banks
    if os.path.isdir(full_path):
        language = root_file
        for file in os.listdir(full_path):            
            # one pck for each bank, including streamed files
            if file.endswith('.bnk'):                
                bank_name = file[:-4]
                pck_output = os.path.join(pck_path, language, bank_name + '.pck')
                command = packager_command + ' -output {} -banks {} -languages {}'.format(pck_output, bank_name, language)                
                os.system(command)        
        # one pck for all the external sources for each language
        pck_output = os.path.join(pck_path, language, 'ExternalSources.pck')        
        command = packager_command + ' -output_ext {} -languages {}'.format(pck_output, language)
        print(command)
        os.system(command)
    # SFX banks
    elif root_file.endswith('.bnk'):
        bank_name = root_file[:-4]
        pck_output = os.path.join(pck_path, bank_name + '.pck')
        command = packager_command + ' -output {} -banks {}'.format(pck_output, bank_name)                
        os.system(command)        


