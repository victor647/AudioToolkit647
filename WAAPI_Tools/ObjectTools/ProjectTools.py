import os
from Libraries import WAAPI, ProjectConventions


# 获取工程路径
def get_project_path():
    return WAAPI.get_project_property('filePath')


# 判断工程是否带有特定名称的平台
def has_platform(platform_name: str):
    platforms = WAAPI.get_project_info('platforms')
    for platform in platforms:
        if platform['name'] == platform_name:
            return True
    return False


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
