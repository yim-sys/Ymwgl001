import ddt
import json
import unittest
from common.requestsHandler import doRequests
from middleware.middleHandler import MiddleHandler,CaseVar

#对象初始化
handler=MiddleHandler()
#读取测试数据
cases=MiddleHandler().execl.read_data('add')
#初始化日志对象
mylog=MiddleHandler.mylog


@ddt.ddt
class TestAdd(unittest.TestCase):
    '''加标用例类'''
    @classmethod
    def setUpClass(cls) -> None:
        setattr(CaseVar, 'member_id', handler.login('user')['member_id'])
        setattr(CaseVar, 'token', handler.login('user')['token'])
        cls.db = MiddleHandler.getDb()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.db.close()

    @ddt.data(*cases)
    def test_add(self,case):
        global result
        member_id = getattr(CaseVar, 'member_id', "")
        #替换测试数据
        case['data'] = handler.replace_data(case['data'])
        case['headers'] = handler.replace_data(case['headers'])
        data = eval(case['data'])
        excepted = json.loads(case['expected'])
        before_count=self.db.query("select count(1) as cn from loan where member_id={}".format(member_id))
        mylog.info("正在测试第{}个用例，测试数据是：{}".format(case['case_id'], case))
        mylog.info('用例期望结果是：{}'.format(excepted))
        #发送请求
        res=doRequests(
            url=MiddleHandler().host+case['url'],
            method=case['method'],
            headers=json.loads(case['headers']),
            json=data
        )
        res=res.json()
        mylog.info('用例实际结果是：{}'.format(res))
        #检查点
        try:
            for k, v in excepted.items():
                self.assertEqual(v, res[k])
                after_count = self.db.query("select count(1) as cn from loan where member_id={}".format(member_id))
                if res['code']==0:
                    #判断是否新增1条项目记录
                    self.assertEqual(str(before_count['cn']+1),str(after_count['cn']))
                    result = '通过'
        except AssertionError as e:
            mylog.error('错误信息{}'.format(e))
            result = '不通过'
            raise e
        finally:
            mylog.info('用例{}:测试{}，正在回写测试结果...'.format(case['case_id'], result))
            MiddleHandler.execl.write(MiddleHandler.file_name, 'add', case['case_id'] + 1, 9, result)
            mylog.info('回写测试结果成功!')


if __name__ == '__main__':
    unittest.main()






