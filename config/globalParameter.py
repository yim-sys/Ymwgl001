import os

#项目目录
PROJECT_PATH=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#测试用例文件
FILE_PATH=os.path.join(PROJECT_PATH,'data')

#用例目录
CASES_PATH=os.path.join(PROJECT_PATH,'testcase')

#测试报告
REPORT_PATH=os.path.join(PROJECT_PATH,'reports')

#日志目录
LOG_PATH=os.path.join(PROJECT_PATH,'logs','cases.log')

#配置文件目录
CONF_PATH=os.path.join(PROJECT_PATH,'config','conf.yaml')