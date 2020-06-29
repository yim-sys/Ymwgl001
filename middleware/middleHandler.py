import os
from jsonpath import jsonpath
from pymysql.cursors import DictCursor
from config import globalParameter
from common.excelHandler import ExcelHandler
from common.loggerHandler import getLogger
from common.yamlHandler import read_yaml
from common.dbHandler import MysqlHandler
from config.globalParameter import FILE_PATH, CONF_PATH, LOG_PATH
from common.requestsHandler import doRequests

#项目功能中间相关操作
class MidMysqlHandler(MysqlHandler):
    def __init__(self):
        __config = read_yaml(CONF_PATH)
        super().__init__(
            # 读取配置文件
            host=__config['mysql']['host'],
            port=__config['mysql']['port'],
            user=__config['mysql']['user'],
            password=__config['mysql']['password'],
            charset=__config['mysql']['charset'],
            database=__config['mysql']['database'],
            cursorclass=DictCursor
        )

class CaseVar:
  '''存储测试中临时变量'''
  pass

class MiddleHandler:
    '''初始化其他模块中需要重复使用的对象'''
    # 读取配置文件
    __config = read_yaml(CONF_PATH)
    #加载路径配置项
    conf=globalParameter
    #excel操作，获取测试用例文件
    file_name=os.path.join(FILE_PATH, __config['excel']['file'])
    execl=ExcelHandler(file_name)
    #读取HOST
    host=__config['host']

    #加载日志对象
    mylog=getLogger(name=__config['log']['mylogname'],
                     logger_level=__config['log']['loglevel'],
                     sh_level=__config['log']['loglevel'],
                     file_leval=__config['log']['fileleval'],
                     fmt=__config['log']['fmt'],
                     filename=LOG_PATH)

    #加载MysqlHandlerMid类，方便管理
    getDb=MidMysqlHandler

    def login(self,user):
        """封装登录，用于接口依赖"""
        __config = read_yaml(CONF_PATH)
        res=doRequests(
            url=__config['host']+'/member/login',
            method='post',
            json=__config[user],
            headers={'X-Lemonban-Media-Type':'lemonban.v2'}
        ).json()
        #通过jsonpath，提取json数据中的指定数据，$代表根节点,.or[]代表子节点..代表子孙节点
        token_value=jsonpath(res,"$..token")[0]
        token_type=jsonpath(res,"$..token_type")[0]
        member_id=jsonpath(res,"$..id")[0]
        token = ' '.join([token_type, token_value])
        return {'token':token,'member_id':member_id}


    def add_loan(self,type=1,loan_term=None):
        """新增项目"""
        token = getattr(CaseVar, 'token', "")
        data={"member_id":12103,
              "title":"财富自由",
              "amount":2000,
              "loan_rate":18.0,
              "loan_term":loan_term,
              "loan_date_type":type,
              "bidding_days":5}
        #发送请求，添加项目,返回项目id
        res=doRequests(
            url=MiddleHandler().__config['host']+'/loan/add',
            method='post',
            json=data,
            headers={"X-Lemonban-Media-Type":"lemonban.v2","Authorization":token}
        )
        res=res.json()
        return jsonpath(res,"$..id")[0]

    def audit_loan(self, loan_id):
        admin_token = getattr(CaseVar, 'admin_token', "")
        data = {"loan_id": loan_id,
                "approved_or_not": True
                }
        # 发送请求，审核项目
        res = doRequests(
            url=MiddleHandler().__config['host'] + '/loan/audit',
            method='patch',
            json=data,
            headers={"X-Lemonban-Media-Type": "lemonban.v2", "Authorization": admin_token}
        )
        return data['loan_id']

    def recharge(self):
        invest_member_id = getattr(CaseVar, 'invest_member_id', "")
        invest_token= getattr(CaseVar, 'invest_token', "")
        data = {"member_id": invest_member_id,
                "amount": 2200}
        res = doRequests(
            url=MiddleHandler().__config['host'] + '/member/recharge',
            method='post',
            json=data,
            headers={"X-Lemonban-Media-Type": "lemonban.v2", "Authorization": invest_token}
        )


    def replace_data(self,data):
        """替换函数"""
        import re
        # 匹配规则{"member_id":#member_id#, "amount":0}--》#member_id#
        patten=r'#(.*?)#'
        #循环替换
        while re.search(patten,data):
            # 提取要替换的字段
            key=re.search(patten,data).group(1)
            # 通过提取的字段来获取对应同名属性值，CaseVar类名
            value=getattr(CaseVar,key,"")
            # 替换数据
            data=re.sub(patten,str(value),data,1)
        return data



if __name__ == '__main__':
    a=MiddleHandler()
    test_str='{"member_id":#member_id#,"token":"#token#"}'
    print(a.replace_data(test_str))



