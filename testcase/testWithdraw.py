import ddt
import json
import unittest
from decimal import Decimal
from common.requestsHandler import doRequests
from middleware.middleHandler import MiddleHandler,CaseVar

#对象初始化
handler=MiddleHandler()
#读取测试数据
cases=MiddleHandler().execl.read_data('withdraw')
#初始化日志对象
mylog=MiddleHandler.mylog


@ddt.ddt
class TestWithdraw(unittest.TestCase):
    '''提现用例类'''
    @classmethod
    def setUpClass(cls) -> None:
        setattr(CaseVar, 'member_id', handler.login('user')['member_id'])
        setattr(CaseVar, 'token', handler.login('user')['token'])
        cls.db = MiddleHandler.getDb()
        #根据用例数据设计，数据初始化
        cls.db.query("update member set leave_amount='500100' where id=12103;")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.db.close()

    @ddt.data(*cases)
    def test_withdraw(self,case):
        '''提现用例类'''
        global result
        #替换测试数据
        member_id = getattr(CaseVar, 'member_id', "")
        token = getattr(CaseVar, 'token', "")
        # 替换测试数据
        case['data'] = handler.replace_data(case['data'])
        case['headers'] = handler.replace_data(case['headers'])
        data = json.loads(case['data'])
        headers = json.loads(case['headers'])
        excepted = json.loads(case['expected'])
        #提现前余额与提现流水记录
        before_amount=self.db.query("select leave_amount from member where id={}".format(member_id))
        before_count =self.db.query("select count(1) as cn from financelog where pay_member_id={};".format(member_id))
        mylog.info("正在测试第{}个用例，测试数据是：{}".format(case['case_id'], case))
        mylog.info('用例期望结果是：{}'.format(excepted))
        #发送请求
        res=doRequests(
            url=MiddleHandler().host+case['url'],
            method=case['method'],
            headers=headers,
            json=data
        ).json()
        mylog.info('用例实际结果是：{}'.format(res))
        #检查点
        try:
            for k, v in excepted.items():
                self.assertEqual(v, res[k])
                after_amount = self.db.query("select leave_amount from member where id={}".format(member_id))
                after_count = self.db.query("select count(1) as cn from financelog where pay_member_id={};".format(member_id))
            if res['code']==0:
                #提现成功后，判断余额是否正确并存在流水记录
                self.assertEqual(before_amount['leave_amount']-Decimal(str(data['amount'])),after_amount['leave_amount'])
                self.assertEqual(str(before_count['cn']+1),str(after_count['cn']))
                result = '通过'
            else:
                #提现异常后，判断余额是否正确
                self.assertEqual(before_amount['leave_amount'],after_amount['leave_amount'])
                result='通过'
        except AssertionError as e:
            mylog.error('异常信息{}'.format(e))
            result = '不通过'
            raise e
        finally:
            mylog.info('用例{}:测试{}，正在回写测试结果...'.format(case['case_id'],result))
            MiddleHandler.execl.write(MiddleHandler.file_name,'withdraw',case['case_id'] + 1,9,result)
            mylog.info('回写测试结果成功!')

if __name__ == '__main__':
    unittest.main()





