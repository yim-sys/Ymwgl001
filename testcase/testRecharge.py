import ddt
import json
import unittest
from decimal import Decimal
from common.requestsHandler import doRequests
from middleware.middleHandler import MiddleHandler
from middleware.middleHandler import CaseVar

#对象初始化
handler=MiddleHandler()
#读取测试数据
cases=MiddleHandler().execl.read_data('recharge')
#初始化日志对象
mylog=MiddleHandler.mylog


@ddt.ddt
class TestRecharge(unittest.TestCase):
    '''充值用例类'''
    @classmethod
    def setUpClass(cls) -> None:
        setattr(CaseVar, 'member_id', handler.login('user')['member_id'])
        setattr(CaseVar, 'token', handler.login('user')['token'])
        cls.db = MiddleHandler.getDb()

    def setUp(self) -> None:
        pass

    @classmethod
    def tearDownClass(cls) -> None:
        cls.db.close()

    @ddt.data(*cases)
    def test_recharge(self,case):
        '''充值用例类'''
        global result
        member_id = getattr(CaseVar, 'member_id', "")
        #替换测试数据
        case['data'] = handler.replace_data(case['data'])
        case['headers'] = handler.replace_data(case['headers'])
        data=json.loads(case['data'])
        headers =json.loads(case['headers'])
        excepted = json.loads(case['expected'])
        before_money=self.db.query("select leave_amount from member where id={}".format(member_id))
        mylog.info("正在测试第{}个用例，测试数据是：{}".format(case['case_id'], case))
        mylog.info('用例期望结果是：{}'.format(excepted))
        #发送请求
        res=doRequests(
            url=MiddleHandler().host+case['url'],
            method=case['method'],
            headers=headers,
            json=data
        )
        res=res.json()
        mylog.info('用例实际结果是：{}'.format(res))
        #检查点
        try:
            for k, v in excepted.items():
                self.assertEqual(v, res[k])
                after_amount = self.db.query("select leave_amount from member where id={}".format(member_id))
            if res['code']==0:
                #判断余额是否正确
                self.assertEqual(before_money['leave_amount']+Decimal(str(data['amount'])),after_amount['leave_amount'])
                financeLog = self.db.query("select 1 from financelog where income_member_id='12103' and amount={}".format(Decimal(str(data['amount']))))
                self.assertIsNotNone(financeLog)
                result = '通过'
            else:
                #充异常后，判断余额是否不变
                self.assertEqual(before_money['leave_amount'],after_amount['leave_amount'])
                result='通过'
        except AssertionError as e:
            mylog.error('错误信息{}'.format(e))
            result = '不通过'
            raise e
        finally:
            mylog.info('用例{}:测试{}，正在回写测试结果...'.format(case['case_id'], result))
            MiddleHandler.execl.write(
                file_path=MiddleHandler.file_name,
                sheet_name='recharge',
                row=case['case_id'] + 1,
                col=9,
                data=result)
            mylog.info('回写测试结果成功!')

if __name__ == '__main__':
    unittest.main()







