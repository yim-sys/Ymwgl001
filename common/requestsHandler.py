import requests

def doRequests(url,method='post',params=None,data=None,json=None,**kwargs):
    """函数二次封装request"""
    # 调用request
    res=requests.request(method.lower(),
                     url,
                     params=params,
                     data=data,
                     json=json,
                     **kwargs
    )
    return res

if __name__ == '__main__':
    #准备测试数据
    url = 'http://api.keyou.site:8000/user/login/'
    data={
        'username':'lemon1',
        'password':'123456'
    }
     #发送请求（调用封装的request函数）
    res=doRequests(url,method='post',data=data).json()
    print(res)


