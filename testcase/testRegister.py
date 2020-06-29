import ddt
import json
import unittest
from middleware.middleHandler import MiddleHandler
from middleware.getPhoneNumber import randomPhoneNumb
from common.requestsHandler import doRequests

#读取测试数据
Register_cases=MiddleHandler.execl.read_data('register')

#初始化日志对象
mylog=MiddleHandler.mylog


@ddt.ddt
class TestRegisterApi(unittest.TestCase):
    '''注册用例类'''
    @classmethod
    def setUpClass(cls):
        mylog.info('---------开始执行测试用例------------')
    @classmethod
    def tearDownClass(cls):
        mylog.info('-----------用例执行结束-------------')

    @ddt.data(*Register_cases)
    def test_register(self,case):
        '''注册用例类'''
        global result
        #判断需要动态生成手机号码的用例数据，进行替换
        if '#phoneNumber#' in case['data']:
            phone=randomPhoneNumb()
            case['data']=case['data'].replace('#phoneNumber#',phone)
        mylog.info("正在测试第{}个用例，测试数据是：{}".format(case['case_id'], case))
        data = json.loads(case['data'])
        headers = json.loads(case['headers'])
        #预期结果
        mylog.info('用例期望结果是：{}'.format(json.loads(case['expected'])))
        #实际结果
        try:
            res= doRequests(url=MiddleHandler().host+case['url'],
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
            # 判断是否需要进行SQL校验
            if res['code']==0:
                # 数据库操作
                db=MiddleHandler.getDb()
                sqldata = db.query("select * from member where mobile_phone={}".format(data['mobile_phone']))
                db.close()
                mylog.info('插入的数据为{}'.format(data))
                try:
                    #是否存在注册数据
                    self.assertTrue(sqldata)
                    #注册的手机号码是否与数据库一致
                    self.assertEqual(sqldata['mobile_phone'],data['mobile_phone'])
                    result = '通过'
                except AssertionError as error:
                    result = '不通过'
                    raise error
            #不需要校验SQL
            else:
                result = '通过'
                #捕获异常
        except AssertionError as e:
            mylog.error('错误信息{}'.format(e))
            result = '不通过'
            raise e
        finally:
            mylog.info('用例{}:测试{}，正在回写测试结果...'.format(case['case_id'], result))
            MiddleHandler.execl.write(MiddleHandler.file_name,'register',case['case_id'] + 1,9,result)
            mylog.info('回写测试结果成功!')



if __name__ == '__main__':
    unittest.main()
