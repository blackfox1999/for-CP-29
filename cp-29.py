import threading
import time
import hashlib
import requests
import json

# 登陆获取COOKIE
def login(account, password):
    url = 'https://user.allcpp.cn/api/login/normal'
    data = {
        'account': account,
        'password': password,
        'phoneAccountBindToken': 'undefined',
        'thirdAccountBindToken': 'undefined'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Origin': 'https://cp.allcpp.cn',
        'Referer': 'https://cp.allcpp.cn/'
    }
    response = requests.post(url, data=data, headers=headers)
    response_obj = json.loads(response.text)
    if t := response_obj.get('token'):
        print(f"token={t}")
        return t
    else:
        return ""

# 获取购票人信息
def get_purchaser(token):
    url = "https://www.allcpp.cn/allcpp/user/purchaser/getList.do"
    headers = {
        "Host": "www.allcpp.cn",
        "Cookie": f"token={token};",
        "Sec-Ch-Ua": '"Chromium";v="112", "Microsoft Edge";v="112", "Not:A-Brand";v="99"',
        "Accept": "application/json, text/plain, */*",
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Origin": "https://cp.allcpp.cn",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://cp.allcpp.cn/",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
    }
    ids = []
    response = requests.get(url, headers=headers)
    info = response.json()
    if len(info) != 0:
        for i in info:
            ids.append(i['id'])
            print(f"info->{i}")
        return ids
    else:
        return []

## 获取票的类别
def get_TicketType(token,eventMainId):
    url = f"https://www.allcpp.cn/allcpp/ticket/getTicketTypeList.do?eventMainId={eventMainId}"
    headers = {
        "Host": "www.allcpp.cn",
        "Cookie": f"token={token};",
        "Sec-Ch-Ua": '"Chromium";v="112", "Microsoft Edge";v="112", "Not:A-Brand";v="99"',
        "Accept": "application/json, text/plain, */*",
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Origin": "https://cp.allcpp.cn",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://cp.allcpp.cn/",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
    }

    response = requests.get(url, headers=headers)
    resText = response.json()
    if info:=resText.get("ticketTypeList"):
        return info
    else:
        return []

# 尝试提交订单  这里是支付宝购买 可能有bug  看到成功字样后 自己手动往个人订单里面
def commit(token, ticket_type_id, count, purchaser_ids,rtime=30):
    base_url = "https://www.allcpp.cn/allcpp/ticket/buyTicketAlipay.do"
    # # 定义请求头
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Content-Length": "2",
        "Content-Type": "application/json;charset=UTF-8",
        "Cookie": f"token={token};",
        "Host": "www.allcpp.cn",
        "Origin": "https://cp.allcpp.cn",
        "Referer": "https://cp.allcpp.cn/",
        "Sec-Ch-Ua": '"Chromium";v="112", "Microsoft Edge";v="112", "Not:A-Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48"
    }
    timestamp = str(int(time.time())) ##"1682074579"
    ## 貌似并不校验 sign: a()(t + r + i + e + n)
    nonce="jcFFFK4pPz2eNGBND3xDxTEyZ7PGCyzm" ## 随机值即可
    sign=hashlib.md5(f"2x052A0A1u222{timestamp}{nonce}{ticket_type_id}2sFRs".encode('utf-8')).hexdigest()
    # print(f"ticket_type_id={ticket_type_id}")
    # print(f"nonce={nonce}")
    # print(f"timestamp={timestamp}")
    # print(f"sign={sign}")

    num_TRY=0
    while True:
    # 拼接完整URL
        num_TRY += 1
        print('-------尝试次数：',num_TRY，'次--------')
        
        try:
            url = f"{base_url}?ticketTypeId={ticket_type_id}&count={count}&nonce={nonce}&timeStamp={timestamp}&sign={sign}&purchaserIds={purchaser_ids}"
            response = requests.post(url, json={},timeout=30,headers=headers)
            if response.status_code!=200:
                ## 几乎就是失败
                print("请求抢票失败")
                print(response.text)
            else:
                # print(response.text)
                res = response.json()
                if res.get('isSuccess'):
                    print("抢票成功")
                else:
                    print("抢票失败")
                    print(response.text)
            print('--------',rtime , "秒后开始下一次--------")
            time.sleep(rtime)
        except Exception as e:
            print(f"发生异常: {e}")
            time.sleep(rtime)

def run_at_time():
    # 你要执行的代码
    print("开始操作")
    commit(token,tid,count,purchaser_ids,time_wait)
    print("持续操作")
#--------------------------------------------------------------------


# 手动登录
account = input("请输入登陆号：")
password = input("请输入登陆密码：")
token = login(account, password)
# print(token)

# # 自动登录一：固定用户名与密码
# account = ""
# password = ""

# # 自动登录二：固定token
# token=""

ids = get_purchaser(token)
if len(ids)==0:
    print("请在账号中添加购票人信息。")
    exit(0)
TicketType = get_TicketType(token,1074) ## 1074 为cp29
if len(TicketType) == 0:
    print("请求票种信息失败，尝试是手动获取或者重试")
    exit(0)
idlist = []
print("----------------------------")
print("票种信息如下：")
for i in TicketType:
    print(f"ID:{i['id']}---Name:{i['ticketName']}")
    idlist.append(str(i['id']))
print("-----------------------")
## 网络不好的话 请固定tid VIPDay1 1904
# tid = '1904'
while True:
    tmp = input("请输入需要抢票的票种ID: ")
    if tmp in idlist:
        tid= tmp
        break
    else:
        print("ID输入错误")

print("Start ...")
count = len(ids) ## 抢票的数量 几个人几张 
purchaser_ids=''
for i in ids:
    purchaser_ids += str(i)+","
if purchaser_ids.endswith(","):
    purchaser_ids = purchaser_ids[:-1]

# 自定义抢票间隔
strWait = input("请输入抢票间隔时间（单位：秒）：")
time_wait = int(strWait)

#自定义开始抢票的时刻
time_St = input("请输入开始时间（例：13:15:00，时间里的冒号用英文的冒号。中英文的冒号不一样！）：")

# 获取当前时间
now = time.time()

# 获取抢票时间的时间戳
target_time = time.mktime(time.strptime(time.strftime("%Y-%m-%d") + " " +time_St, "%Y-%m-%d %H:%M:%S"))

# 如果现在时间已经过了抢票时间，则明天再执行
if now > target_time:
    target_time += 24 * 60 * 60

# 计算延迟时间
delay = target_time - now
print(delay , "秒后开始--------")

# 设置定时器
timer = threading.Timer(delay, run_at_time)

# 启动定时器
timer.start()
