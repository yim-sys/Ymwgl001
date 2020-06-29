import ddt
import json
import unittest
from common.requestsHandler import doRequests
from middleware.middleHandler import MiddleHandler,CaseVar

#对象初始化
handler=MiddleHandler()
#读取测试数据
cases=handler.execl.read_data('invest')
#初始化日志对象
mylog=MiddleHandler.mylog


@ddt.ddt
class TestInvest(unittest.TestCase):
    '''投资用例类'''
    @classmethod
    def setUpClass(cls) -> None:
        #普通用户
        setattr(CaseVar, 'token', handler.login('user')['token'])
        setattr(CaseVar, 'member_id', handler.login('user')['member_id'])
        #管理员用户登录
        setattr(CaseVar, 'admin_token', handler.login('admin_user')['token'])
        #投资人登录
        setattr(CaseVar, 'invest_member_id', handler.login('invest_user')['member_id'])
        setattr(CaseVar, 'invest_token', handler.login('invest_user')['token'])
        #初始化数据库对象
        cls.db = MiddleHandler.getDb()
        #审核中
        audit_loan_id = cls.db.query("select id from loan where member_id='12103' and status=1 order by id desc LIMIT 1;")
        setattr(CaseVar, 'audit_loan_id', audit_loan_id['id'])
        #还款中
        repay_loan_id= cls.db.query("select id from loan where member_id='12103' and status=3 order by id desc LIMIT 1;")
        setattr(CaseVar, 'repay_loan_id', repay_loan_id['id'])
        ##还款完成
        repayall_loan_id = cls.db.query("select id from loan where member_id='12103' and status=4 order by id desc LIMIT 1;")
        setattr(CaseVar, 'repayall_loan_id', repayall_loan_id['id'])

    def setUp(self) -> None:
        self.loan_id = handler.add_loan(type=1, loan_term=3)
        setattr(CaseVar, 'loan_id', self.loan_id)
        handler.audit_loan(CaseVar.loan_id)
        handler.recharge()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.db.close()


    @ddt.data(*cases)
    def test_invest(self,case):
        '''投资用例类'''
        global result
        member_id = getattr(CaseVar, 'member_id', "")
        #增加日投资项目，type=1,月期限（默认），type=2,天期限
        if case['flag'] == 2:
            setattr(CaseVar, 'day_loan_id', handler.add_loan(type=2,loan_term=10))
            handler.audit_loan(CaseVar.day_loan_id)
        case['data']=handler.replace_data(case['data'])
        case['headers']=handler.replace_data(case['headers'])
        data = json.loads(case['data'])
        headers = json.loads(case['headers'])
        mylog.info("正在测试第{}个用例，测试数据是：{}".format(case['case_id'], case))
        expected = json.loads(case['expected'])
        mylog.info('用例期望结果是:{}'.format(expected))
        if expected['code']==0:
            member_id = data['member_id']
            before_invest = self.db.query('select count(1) as cn  from invest where member_id={};'.format(member_id))
            before_log = self.db.query('select count(1) as cn from financelog where pay_member_id={};'.format(member_id))
            before_amount = self.db.query('select leave_amount from member where id={}'.format(member_id))
        #替换headers
        res=doRequests(
            url=handler.host+case['url'],
            method=case['method'],
            headers=headers,
            json=data
        ).json()
        mylog.info('用例实际结果是：{}'.format(res))
        try:
            self.assertEqual(expected['code'],res['code'])

            if res['code']==0:
                #验证数据库状态
                after_amount = self.db.query('select leave_amount from member where id={}'.format(member_id))
                after_log = self.db.query(
                    'select count(1) as cn  from financelog where pay_member_id={};'.format(member_id))
                after_invest = self.db.query(
                    'select count(1) as cn from invest where member_id={};'.format(member_id))
                self.assertEqual(before_log['cn']+1,after_log['cn'])
                self.assertEqual(before_invest['cn']+1,after_invest['cn'])
                self.assertEqual(before_amount['leave_amount']-data['amount'],after_amount['leave_amount'])
                self.assertEqual(expected['msg'], res['msg'])
            if case['flag']:
                #月投资项目，当可投金额为0时，会自动为该项目的所有的投资记录生成对应的回款计划列表
                sum_invest=self.db.query('select sum(amount) as sum from invest where member_id={} and loan_id={};'.format(member_id,data['loan_id']))
                loan_msg=self.db.query('select amount ,status from loan  where id={};'.format(data['loan_id']))
                repayment_data=self.db.query(' select count(b.id) as cn from invest a ,repayment b where  a.id=b.invest_id and loan_id= {};'.format(data['loan_id']))
                self.assertEqual(sum_invest['sum'],loan_msg['amount'])
                self.assertEqual(loan_msg['status'],expected['status'])
                if case['flag']==1:
                    self.assertEqual(repayment_data['cn'],3)
                if case['flag']==2:
                    self.assertEqual(repayment_data['cn'],1)
                #天投资项目当可投金额为0时，会自动为该项目的所有的投资记录生成对应的回款计划列表
            result= '通过'

        except AssertionError as e:
            mylog.error('错误信息{}'.format(e))
            result= '不通过'
            raise e
        finally:
            mylog.info('用例{}:测试{}，正在回写测试结果...'.format(case['case_id'], result))
            MiddleHandler.execl.write(MiddleHandler.file_name,'invest', case['case_id'] + 1, 10, result)
            mylog.info('回写测试结果成功!')


if __name__ == '__main__':
    unittest.main()



