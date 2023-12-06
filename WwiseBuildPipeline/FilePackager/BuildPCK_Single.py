import os, sys, subprocess

pck_output_dir = sys.argv[1]
bank_name = sys.argv[2]
language = ''
if len(sys.argv) > 3:
    language = sys.argv[3]
file_dir = os.path.dirname(__file__)
project_path = os.path.join(file_dir, 'Wwise_生死狙击2.wproj')
language_arg = ' --language ' + language if language != '' else ''
os.system('WwiseConsole generate-soundbank {} --bank {} {}'.format(project_path, bank_name, language_arg))

bank_path = os.path.join(file_dir, 'GeneratedSoundBanks')
info_path = os.path.join(bank_path, 'SoundBanksInfo.xml')
packager_path = os.path.join(os.getenv('WWISEROOT'), 'Authoring\\x64\\Release\\bin\\Tools\\FilePackager.Console.exe')
packager_command = '\"{}\" -generate -info {}'.format(packager_path, info_path)
pck_output = os.path.join(pck_output_dir, language, bank_name + '.pck')
language_arg = ' -languages ' + language if language != '' else ''
command = packager_command + ' -output {} -banks {} {}'.format(pck_output, bank_name, language_arg)
os.system(command)