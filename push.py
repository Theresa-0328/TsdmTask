import httpx

def telegram(send_title, push_message,bot_token,chat_id):
    httpx.post(
        url="https://api.telegram.org/bot{}/sendMessage".format(bot_token),
        data={
            "chat_id": chat_id,
            "text": send_title + "\r\n" + push_message
        }
    )

def push(data,bot_token,chat_id):
    func = globals().get("telegram")
    func("【天使动漫论坛签到推送】",data,bot_token,chat_id)

if __name__ == "__main__":
    push("test")