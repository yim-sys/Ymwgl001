import pymysql
from pymysql.cursors import DictCursor

class MysqlHandler:
    def __init__(
            self,
            host=None,
            port=3306,
            user=None,
            password=None,
            charset='utf8',
            database='future',
            cursorclass=DictCursor
    ):
        self.conn=pymysql.connect(
             host=host,
             port=port,
             user=user,
             password=password,
             charset=charset,
             database=database,
             cursorclass=cursorclass
        )
        #创建游标
        self.cursor=self.conn.cursor()

    def query(self,sql,one=True):
        self.conn.commit()
        self.cursor.execute(sql)
        if one:
            return self.cursor.fetchone()
        return self.cursor.fetchall()

    def close(self):
        # 关闭游标
        self.cursor.close()
        # 断开连接
        self.conn.close()

    def commit(self):
        # 提交事务
        self.conn.commit()

if __name__ == '__main__':
    db=MysqlHandler(
        host='test.lemonban.com',
        port=3306,
        user='test',
        password='test',
        charset='utf8',
        database='future',
        cursorclass=DictCursor
    )

    data=db.query("select * from member limit 2;")
    db.close()


