import os
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
import sys

from Libraries import WaapiTools


class WwiseSilenceTool:
    IDString = "FFFF0000-0000-0000-0000-"
    ID = 0
    ShortID = 999920000
    parent_map = {}
    path = ''

    def __init__(self):
        self.IDString = "FFFF0000-0000-0000-0000-"
        self.ID = 0
        self.ShortID = 999920000
        self.parent_map = {}
        self.path = ''

    def Add(self):
        if self.path == '':
            self.path = WaapiTools.get_project_directory()
            index = self.path.rfind('\\')
            self.path = self.path[:index + 1]
        self.auto_add_wwise_silence(self.path + "Actor-Mixer Hierarchy\\Voice_InGame.wwu")
        self.auto_add_wwise_silence(self.path + "Actor-Mixer Hierarchy\\Voice_FrontEnd.wwu")

    def Remove(self):
        if self.path == '':
            self.path = WaapiTools.get_project_directory()
            index = self.path.rfind('\\')
            self.path = self.path[:index + 1]
        self.auto_remove_wwise_silence(self.path + "Actor-Mixer Hierarchy\\Voice_InGame.wwu")
        self.auto_remove_wwise_silence(self.path + "Actor-Mixer Hierarchy\\Voice_FrontEnd.wwu")

    # Add Silence
    def auto_add_wwise_silence(self, File):
        tree = ElementTree.parse(File)
        self.build_parent_map(tree)
        root = tree.getroot()
        for child in root:
            self.check_and_add_wwsie_silence(child)
        self.pretty_xml(root, '\t', '\n')
        tree.write(File, encoding="utf-8", xml_declaration=True)
        self.format_xml(File)

    def build_parent_map(self, tree):
        self.parent_map = {c: p for p in tree.iter() for c in p}

    def check_and_add_wwsie_silence(self, Node: Element):
        if self.meet_add_condition(Node):
            self.add_wwise_silence(self.parent_map[Node])
        else:
            for child in Node:
                self.check_and_add_wwsie_silence(child)

    def meet_add_condition(self, Node: Element):
        have_zh_cn = False
        have_zh_hans = False
        have_en = False
        for child in Node:
            language = child.find('Language')
            if language is not None:
                if language.text == 'zh-CN':
                    have_zh_cn = True
                if language.text == 'zh-Hans':
                    have_zh_hans = True
                if language.text == 'en':
                    have_en = True
        if have_zh_cn and have_zh_hans and (not have_en):
            return True
        return False

    def add_wwise_silence(self, Node: Element):
        sID = "{" + self.IDString + str(self.ID).zfill(12) + "}"
        # <SourcePlugin Name="Wwise Silence" ID="{28F00FD7-6D84-4BAE-9333-46E3BDF6446E}" ShortID="999913397" PluginName="Wwise Silence" CompanyID="0" PluginID="101">
        elem_source_plugin = ElementTree.Element("SourcePlugin")
        self.set_attribute(elem_source_plugin, 'Name', 'Auto_Create_Wwise_Silence')
        self.set_attribute(elem_source_plugin, 'ID', sID)
        self.set_attribute(elem_source_plugin, 'ShortID', str(self.ShortID))
        self.set_attribute(elem_source_plugin, 'PluginName', 'Wwise Silence')
        self.set_attribute(elem_source_plugin, 'CompanyID', '0')
        self.set_attribute(elem_source_plugin, 'PluginID', '101')
        elem_language = ElementTree.Element("Language")
        elem_language.text = "en"
        elem_source_plugin.append(elem_language)
        children_list = Node.find("ChildrenList")
        if children_list is not None:
            children_list.append(elem_source_plugin)
        # <ActiveSource Name = "Wwise Silence" ID = "{28F00FD7-6D84-4BAE-9333-46E3BDF6446E}" Platform = "Linked" / >
        elem_active_source = ElementTree.Element("ActiveSource")
        self.set_attribute(elem_active_source, 'Name', 'Auto_Create_Wwise_Silence')
        self.set_attribute(elem_active_source, 'ID', sID)
        self.set_attribute(elem_active_source, 'Platform', 'Linked')
        active_source_list = Node.find("ActiveSourceList")
        if active_source_list is not None:
            active_source_list.append(elem_active_source)
        self.ID += 1
        self.ShortID += 1

    def set_attribute(self, node, key, value):
        node.set(key, value)

    # Remove Silence
    def auto_remove_wwise_silence(self, File):
        tree = ElementTree.parse(File)
        self.build_parent_map(tree)
        root = tree.getroot()
        for child in root:
            self.check_and_remove_wwsie_silence(child)
        self.pretty_xml(root, '\t', '\n')
        tree.write(File, encoding="utf-8", xml_declaration=True)
        self.format_xml(File)

    def check_and_remove_wwsie_silence(self, Node: Element):
        if self.meet_remove_condition(Node):
            self.remove_wwise_silence(Node)
        else:
            for child in Node:
                self.check_and_remove_wwsie_silence(child)

    def meet_remove_condition(self, Node: Element):
        for child in Node:
            source_plugin = child.find('SourcePlugin')
            if source_plugin is not None:
                if source_plugin.get("Name") == "Auto_Create_Wwise_Silence":
                    return True
        return False

    def remove_wwise_silence(self, Node: Element):
        sID = "{" + self.IDString + str(self.ID).zfill(12) + "}"
        # <SourcePlugin Name="Wwise Silence" ID="{28F00FD7-6D84-4BAE-9333-46E3BDF6446E}" ShortID="999913397" PluginName="Wwise Silence" CompanyID="0" PluginID="101">
        children_list = Node.find("ChildrenList")
        if children_list is not None:
            for elem_source_plugin in children_list.findall("SourcePlugin"):
                if elem_source_plugin.get("Name") == "Auto_Create_Wwise_Silence":
                    children_list.remove(elem_source_plugin)
        # <ActiveSource Name = "Wwise Silence" ID = "{28F00FD7-6D84-4BAE-9333-46E3BDF6446E}" Platform = "Linked" / >
        active_source_list = Node.find("ActiveSourceList")
        if active_source_list is not None:
            for active_elem_source in active_source_list.findall("ActiveSource"):
                if active_elem_source.get("Name") == "Auto_Create_Wwise_Silence":
                    active_source_list.remove(active_elem_source)

    # 美化格式
    def pretty_xml(self, element, indent, newline, level=0):  # elemnt为传进来的Elment类，参数indent用于缩进，newline用于换行
        if element:  # 判断element是否有子元素
            if (element.text is None) or element.text.isspace():  # 如果element的text没有内容
                element.text = newline + indent * (level + 1)
            else:
                element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * (level + 1)
                # else:  # 此处两行如果把注释去掉，Element的text也会另起一行
                # element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * level
        temp = list(element)  # 将element转成list
        for subelement in temp:
            if temp.index(subelement) < (len(temp) - 1):  # 如果不是list的最后一个元素，说明下一个行是同级别元素的起始，缩进应一致
                subelement.tail = newline + indent * (level + 1)
            else:  # 如果是list的最后一个元素， 说明下一行是母元素的结束，缩进应该少一个
                subelement.tail = newline + indent * level
            self.pretty_xml(subelement, indent, newline, level=level + 1)  # 对子元素进行递归操作

    # 去除' />'前的空格，以保持文本格式和之前版本一致
    def format_xml(self, File):
        file_read = open(File, 'r', encoding='utf-8')  # 要去掉空行的文件
        file_write = open(File + ".new", 'w', encoding='utf-8')  # 生成没有空行的文件
        try:
            for line in file_read.readlines():
                index = line.find(' />')
                if line.find(' />') != -1:
                    line = line.replace(' />', '/>')
                file_write.write(line)
        finally:
            file_read.close()
            file_write.close()
        os.remove(File)
        os.rename(File + ".new", File)


WwiseSilenceInstance = WwiseSilenceTool()
