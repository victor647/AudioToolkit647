import sys
import os
import getopt
import xml.dom.minidom as xml


def main():
    # 第一个参数为源文件路径
    originals_dir = os.path.join(os.path.dirname(__file__), 'ExternalSources')
    # 创建固定的根节点
    doc = xml.Document()
    xml_root = doc.createElement('ExternalSourcesList')
    xml_root.setAttribute('SchemaVersion', str(1))
    xml_root.setAttribute('Root', originals_dir)
    doc.appendChild(xml_root)
    for root, dirs, files in os.walk(originals_dir):
        for file in files:
            if file.endswith(".wav"):
                source = doc.createElement('Source')
                # 存在语言子文件夹，包含到destination中
                if root != originals_dir:
                    file = root.replace(originals_dir + '\\', '') + '\\' + file
                source.setAttribute('Path', file)
                source.setAttribute('Conversion', 'Voice_Vorbis')
                source.setAttribute('Destination', file)
                # 添加xml节点
                xml_root.appendChild(source)
    # 导出的xml文件名
    output_file_path = os.path.join(originals_dir, 'ExternalSourceList.wsources')
    doc.writexml(open(output_file_path, 'w+'), indent='', addindent='\t', newl='\n', encoding='utf-8')


if __name__ == '__main__':
    main()
