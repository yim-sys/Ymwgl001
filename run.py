import os
import unittest
from datetime import datetime
from libs.HTMLTestRunnerNew import HTMLTestRunner
from config.globalParameter import REPORT_PATH, CASES_PATH


#初始化一个加装器
loader=unittest.TestLoader()
suite=loader.discover(CASES_PATH)

#设置报告文件名格式
now=datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
reports_filename='reports-{}.html'.format(now)
reports_path=os.path.join(REPORT_PATH,reports_filename)

#生成测试报告
with open (reports_path,'wb') as fb:
    runner=HTMLTestRunner(stream=fb,
                          verbosity=2,
                          title='自动化测试报告',
                          # description='',
                          tester='miyi')
    runner.run(suite)

