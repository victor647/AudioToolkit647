import logging
from logging import handlers
import win32api, win32con

LogInstance = None


def init_log():
    global LogInstance
    LogInstance = Logger('log.txt', level='debug')


def safe_log(msg, level='debug'):
    if level == 'debug':
        LogInstance.logger.debug(msg)
    elif level == 'info':
        LogInstance.logger.info(msg)
    elif level == 'warning':
        LogInstance.logger.warning(msg)
    elif level == 'error':
        LogInstance.logger.error(msg)
        win32api.MessageBox(0, msg, "Error", win32con.MB_ICONWARNING)
    elif level == 'crit':
        LogInstance.logger.error(msg)
        win32api.MessageBox(0, msg, "Error", win32con.MB_ICONWARNING)
    else:
        LogInstance.logger.debug(msg)


class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

    def __init__(self, filename, level='info', when='D', backCount=3,
                 fmt='%(asctime)s - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)  # 设置日志格式
        self.logger.setLevel(self.level_relations.get(level))  # 设置日志级别
        sh = logging.StreamHandler()  # 往屏幕上输出
        sh.setFormatter(format_str)  # 设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount,
                                               encoding='utf-8')  # 往文件里写入#指定间隔时间自动生成文件的处理器
        th.setFormatter(format_str)  # 设置文件里写入的格式
        self.logger.addHandler(sh)  # 把对象加到logger里
        self.logger.addHandler(th)
