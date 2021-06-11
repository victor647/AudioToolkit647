import sys
import os
from shutil import copyfile

plugin_name = 'Guitar'
source_dir = 'P:\\WwiseUnreal\\MoreFunAudioLab\\Plugins\\Wwise\\ThirdParty'
destination_dir = 'U:\\R6Game\\Plugins\\Wwise\\ThirdParty'


if __name__ == '__main__':
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if plugin_name in file:
                original_file = os.path.join(root, file)
                destination_file = original_file.replace(source_dir, destination_dir)
                print(destination_file)
                copyfile(original_file, destination_file)
