import os
import xml.dom.minidom as xml

codec = 'Voice_Vorbis'
# 第一个参数为源文件路径
originals_dir = os.path.dirname(__file__)
# 创建固定的根节点
doc = xml.Document()
xml_root = doc.createElement('ExternalSourcesList')
xml_root.setAttribute('SchemaVersion', str(1))
xml_root.setAttribute('Root', originals_dir)
doc.appendChild(xml_root)
total_count = 0
for root, dirs, files in os.walk(originals_dir):
    for file in files:
        if file.endswith(".wav"):
            source = doc.createElement('Source')
            # 缓存原始文件名
            source_path = file
            # 存在语言子文件夹，包含到源路径中
            if root != originals_dir:
                source_path = root.replace(originals_dir + '\\', '') + '\\' + file
            source.setAttribute('Path', source_path)
            source.setAttribute('Conversion', codec)
            # 去除中途多余的子文件夹作为目标路径
            destination_path = os.path.join(source_path.split('\\')[0], file)
            source.setAttribute('Destination', destination_path)
            # 添加xml节点
            xml_root.appendChild(source)
            total_count += 1
# 导出的xml文件名
output_file_path = os.path.join(originals_dir, 'ExternalSourceList.wsources')
doc.writexml(open(output_file_path, 'w+'), indent='', addindent='\t', newl='\n', encoding='utf-8')
print("External File List Generation Complete, found " + str(total_count) + " Audio Files!")

