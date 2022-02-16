import sys
import os
from shutil import copyfile

plugin_names = ['Auro', 'Resonance']
source_dir = 'C:\\Users\\mwj\\Documents\\Unreal Projects\\MyProject\\Plugins\\Wwise\\ThirdParty'
destination_dir = 'D:\\ssjj_next\\battle\\Plugins\\Wwise\\ThirdParty'


if __name__ == '__main__':
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            for plugin_name in plugin_names:
                if plugin_name in file:
                    original_file = os.path.join(root, file)
                    destination_file = original_file.replace(source_dir, destination_dir)
                    print(destination_file)
                    copyfile(original_file, destination_file)
