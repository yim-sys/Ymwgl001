import ddt
import json
import unittest
from middleware.middleHandler import MiddleHandler
from common.requestsHandler import doRequests

#读取测试数据
cases=MiddleHandler.execl.read_data('login')

#初始化日志对象
mylog=MiddleHandler.mylog

@ddt.ddt
class TestLoginApi(unittest.TestCase):
    '''登录用例类'''
    @ddt.data(*cases)
       #加载测试数据
    def test_Login(self, case):
        global result
        #测试数据
        mylog.info("正在测试第{}个用例，测试数据是：{}".format(case['case_id'], case))
        data = json.loads(case['data'])
        headers = json.loads(case['headers'])
        headers['Content-Type']="application/json"
        #预期结果
        mylog.info('用例期望结果是：{}'.format(json.loads(case['expected'])))
        #实际结果
        try:
            res = doRequests(url=MiddleHandler().host+case['url'],
                             method=case['method'],
                             json=data,
                             headers=headers).json()
        except AssertionError as e:
            mylog.error('错误信息:数据返回不是json,{}'.format(e))
            raise e
        mylog.info('用例实际结果是：{}'.format(res))
        #检查点
        expected_dict = json.loads(case['expected'])
        try:
            for k, v in expected_dict.items():
                self.assertEqual(v, res[k])
            result='通过'
        #捕获异常
        except AssertionError as e:
            mylog.error('错误信息{}'.format(e))
            result ='不通过'
            raise e
        finally:
            mylog.info('用例{}:测试{}，正在回写测试结果...'.format(case['case_id'], result))
            MiddleHandler.execl.write(
                file_path=MiddleHandler.file_name,
                sheet_name='login',
                row=case['case_id'] + 1,
                col=9,
                data=result)
            mylog.info('回写测试结果成功!')



if __name__ == '__main__':
    unittest.main()
