import os
from Libraries import WAAPI, ProjectConventions


# 获取工程路径
def get_project_path():
    return WAAPI.get_project_property('filePath')


# 获取工程所在文件夹
def get_project_directory():
    return os.path.dirname(get_project_path())


# 获取Originals所在目录
def get_originals_folder():
    directory = get_project_directory()
    return os.path.join(directory, 'Originals')


# 获取项目的Wwise版本
def get_project_version():
    if not ProjectConventions.Conventions:
        return 2023
    return ProjectConventions.Conventions['WwiseVersion']
