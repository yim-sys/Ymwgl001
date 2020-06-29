import random
from common.yamlHandler import read_yaml
from config.globalParameter import CONF_PATH
from middleware.middleHandler import MiddleHandler

#读取配置文件
config=read_yaml(CONF_PATH)

def randomPhoneNumb():
    '''动态生成手机号码'''
    while True:
        phone = '138'
        for i in range(8):
            num = random.randint(0, 9)
            phone += str(num)

    # 数据库操作
        db = MiddleHandler.getDb()
        phone_data = db.query("select * from member where mobile_phone='{}'".format(phone))
        if not phone_data:
            db.close()
            return phone
        db.close()



if __name__ == '__main__':
    phoneNumber = randomPhoneNumb()
    print(phoneNumber)
