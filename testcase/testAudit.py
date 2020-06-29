import ddt
import json
import unittest
from common.requestsHandler import doRequests
from middleware.middleHandler import MiddleHandler,CaseVar

#对象初始化
handler=MiddleHandler()
#读取测试数据
cases=MiddleHandler().execl.read_data('audit')
#初始化日志对象
mylog=MiddleHandler.mylog


@ddt.ddt
class TestAudit(unittest.TestCase):
    '''审核用例类'''
    @classmethod
    def setUpClass(cls) -> None:
        #普通用户登录
        setattr(CaseVar,'member_id', handler.login('user')['member_id'])
        setattr(CaseVar,'token', handler.login('user')['token'])
        #管理员用户登录
        setattr(CaseVar,'admin_token',handler.login('admin_user')['token'])
        cls.db = MiddleHandler.getDb()
        pass_loan = cls.db.query("select id from loan where member_id='12103' and status=2 order by id desc LIMIT 1;")
        setattr(CaseVar,'pass_loan_id',pass_loan['id'])

    def setUp(self) -> None:
        self.loan_id=handler.add_loan(type=1,loan_term=3)
        setattr(CaseVar,'loan_id',self.loan_id)
    @classmethod
    def tearDownClass(cls) -> None:
        cls.db.close()

    @ddt.data(*cases)
    def test_audit(self,case):
        global result
        case['data'] = handler.replace_data(case['data'])
        case['headers'] = handler.replace_data(case['headers'])
        data = eval(case['data'])
        headers = json.loads(case['headers'])
        expected = json.loads(case['expected'])
        mylog.info("正在测试第{}个用例，测试数据是：{}".format(case['case_id'], case))
        mylog.info('用例期望结果是：{}'.format(expected))
          #替换headers
        res=doRequests(
            url=MiddleHandler().host+case['url'],
            method=case['method'],
            headers=headers,
            json=data
        ).json()
        mylog.info('用例实际结果是：{}'.format(res))
        try:
            self.assertEqual(expected['code'],res['code'])
            self.assertEqual(expected['msg'],res['msg'])
            if res['code']==0:
                loan_data=self.db.query(
                    'select * from loan where id={}'.format(self.loan_id)
                )
                self.assertEqual(expected['status'],loan_data['status'])
                result = '通过'
        except AssertionError as e:

            mylog.error('错误信息{}'.format(e))
            result = '不通过'
            raise e
        finally:
            mylog.info('用例{}:测试{}，正在回写测试结果...'.format(case['case_id'], result))
            MiddleHandler.execl.write(MiddleHandler.file_name,'audit', case['case_id'] + 1,9,result)
            mylog.info('回写测试结果成功!')


if __name__ == '__main__':
    unittest.main()



