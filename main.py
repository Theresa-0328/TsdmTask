import httpx
import re
import urllib.parse
import time
import yaml
from bs4 import BeautifulSoup

from push import push


with open("config/config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

bot_token = config['push']['bot_token']
chat_id = config['push']['chat_id']

account_cookies = config.get('account', [])
first_account = account_cookies[0]
cookie = first_account.get('cookie')

def tsdm_check_in():
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding":"gzip, deflate, br",
        "Accept-Language":"zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control":"max-age=0",
        "Connection":"keep-alive",
        "Cookie":cookie,
        "Referer":"https://www.tsdm39.com/forum.php",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }

    with httpx.Client(headers=headers) as client:
        # 获得formhash
        response = client.get("https://www.tsdm39.com/forum.php")
        pattern = r'name="formhash" value="(.+?)"'
        match = re.search(pattern, response.text)
        formhash_value = match.group(1)
        print("formhash value:", formhash_value)
        encoded_formhash = urllib.parse.quote(formhash_value)

        response.headers['Content-Type'] = 'application/x-www-form-urlencoded'
        response.headers["Origin"] = 'https://www.tsdm39.com'
        # 签到
        payload = {"formhash": encoded_formhash, "qdxq": "kx","qdmode":"3","todaysay":"","fastreply":"1"}
        response = client.post("https://www.tsdm39.com/plugin.php?id=dsu_paulsign%3Asign&operation=qiandao&infloat=1&sign_as=1&inajax=1", data=payload)
        

def tsdm_work():
     # 必须要这个content-type, 否则没法接收
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'cookie': cookie,
        'connection': 'Keep-Alive',
        'x-requested-with': 'XMLHttpRequest',
        'referer': 'https://www.tsdm39.net/plugin.php?id=np_cliworkdz:work',
        'content-type': 'application/x-www-form-urlencoded'
    }

    with httpx.Client(headers=headers) as client:
        # 查询是否可以打工
        response = client.get("https://www.tsdm39.com/plugin.php?id=np_cliworkdz%3Awork&inajax=1", headers=headers)
        pattern = r"您需要等待\d+小时\d+分钟\d+秒后即可进行。"
        match = re.search(pattern, response.text)
        if match:
            result = match.group()
            print(result)
            return
        else:
            print("未找到匹配的字符串，可以打工")
        
        # 必须连续6次！
        data = {"act": "clickad"}
        for i in range(6):
            response = client.post("https://www.tsdm39.com/plugin.php?id=np_cliworkdz:work", headers=headers, data=data)
            if response.status_code == 200:
                print("Content:", response.text)
            time.sleep(3)

        # 获取奖励
        data={"act":"getcre"}
        response = client.post("https://www.tsdm39.com/plugin.php?id=np_cliworkdz:work", headers=headers, data=data)
        print("Content:", response.text)

#查询积分
def get_score():
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding":"gzip, deflate, br",
        "Accept-Language":"zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control":"max-age=0",
        "Connection":"keep-alive",
        "Cookie":cookie,
        "Referer":"https://www.tsdm39.com/forum.php",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }
    with httpx.Client(headers=headers) as client:
        response = client.get("https://www.tsdm39.com/home.php?mod=spacecp&ac=credit&showcredit=1")
        print("Response:", response.status_code)
    soup = BeautifulSoup(response.text, 'html.parser')
    ul_element = soup.find('ul', class_='creditl')

    li_element = ul_element.find('li', class_='xi1')

    # 获取天使币数量
    angel_coins = li_element.get_text(strip=True).replace("天使币:", "").strip()
    print("天使币数量:", angel_coins)
    return angel_coins

def run():
    tsdm_check_in()
    tsdm_work()
    push("已拥有天使币数量:{}".format(get_score()),bot_token,chat_id)

if __name__ == "__main__":
    run()