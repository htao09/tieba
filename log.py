# __author__ ='dbl'
# -*- coding: utf-8 -*-

import logging, time, os


class Log:
    '''
    logging的初始化操作，以类封装的形式进行
    '''

    def __init__(self):
        '''
        '''
        timestr = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        # lib_path = os.path.abspath('../logs')
        filename = '../logs' + timestr + '.log'  # 日志文件的地址
        self.logger = logging.getLogger()  # 定义对应的程序模块名name，默认为root
        self.logger.setLevel(logging.INFO)  # 必须设置，这里如果不显示设置，默认过滤掉warning之前的所有级别的信息

        sh = logging.StreamHandler()  # 日志输出到屏幕控制台
        sh.setLevel(logging.ERROR)  # 设置日志等级

        fh = logging.FileHandler(filename=filename)  # 向文件filename输出日志信息
        fh.setLevel(logging.DEBUG)  # 设置日志等级

        # 设置格式对象
        formatter = logging.Formatter(
            "%(asctime)s %(filename)s[line:%(lineno)d]%(levelname)s - %(message)s")  # 定义日志输出格式

        # 设置handler的格式对象
        sh.setFormatter(formatter)
        fh.setFormatter(formatter)

        # 将handler增加到logger中
        self.logger.addHandler(sh)
        self.logger.addHandler(fh)


# log = Log().logger

if __name__ == "__main__":
    mylogger = Log().logger

    mylogger.debug("debug")
    mylogger.info("info")
    mylogger.warning("warning")
    mylogger.error("error")
    mylogger.critical("critical")
