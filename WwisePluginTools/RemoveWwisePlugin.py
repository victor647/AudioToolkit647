import sys
import os
from shutil import copyfile

plugin_names = ['Guitar']
plugin_dir = 'U:\\R6Game\\Plugins\\Wwise\\ThirdParty'


if __name__ == '__main__':
    for root, dirs, files in os.walk(plugin_dir):
        for file in files:
            for plugin_name in plugin_names:
                if plugin_name in file:
                    full_file = os.path.join(root, file)
                    os.remove(full_file)
                    print(full_file)
