import logging

"""日志封装"""
def getLogger( name='ROOT',
               filename=None,
               logger_level='DEBUG',
               sh_level='DEBUG',
               file_leval='INFO',
               fmt=None,

):
    """---logging日志---
       参数：
       收集处理器名：name
       日志文件名：filename
       收集器日志等级：logger_level
       输出控制台日志等级：sh_level
       输出文件日志等级：fileleval
       日志格式：fmt
    """

    """生成日志收集器"""
    mylog=logging.getLogger(name)
    mylog.handlers.clear()
    """设置收集器级别"""
    mylog.setLevel(logger_level)

    """设置控制台输出"""
    sh_handler=logging.StreamHandler()
    sh_handler.setLevel(sh_level)
    """建立关联(输出控制台添加到日志收集器中）"""
    mylog.addHandler(sh_handler)

    """设置日志展示格式"""
    logfmt = logging.Formatter(fmt)
    sh_handler.setFormatter(logfmt)


    """设置文件输出"""
    if filename:
       file_handler = logging.FileHandler(filename, 'a', encoding='utf8')
       file_handler.setLevel(file_leval)
       mylog.addHandler(file_handler)
       file_handler.setFormatter(logfmt)

    return mylog


if __name__ == '__main__':
    log=getLogger()
    log.warning('this warning msg')
    log.error('this error msg ')





