import json
import time

import requests

# 设置 API 的 URL
url1 = "http://192.168.124.31:10000/client/tryConnect"
url2 = "http://192.168.124.31:10000/client/GetConnectedClients"
# url1 = 'http://127.0.0.1:10000/client/tryConnect'
# url2 = 'http://127.0.0.1:10000/client/GetConnectedClients'


def get_list():
    response = requests.post(url2)

    # 解析响应内容为 JSON
    data = response.json()  # 或者使用 json.loads(response.text)
    jsonData = json.dumps(data, indent=4, ensure_ascii=False)
    # 将 JSON 字符串解析为 Python 对象
    clients = json.loads(jsonData)

    # 遍历列表，格式化输出每个客户端的信息
    for client in clients:
        print(f'{client["clientId"]}: {client["connectTime"]}')
    # 格式化（美化）输出 JSON


def test_connect(client_id):

    # 发送 POST 请求
    response = requests.post(url1, json=client_id)
    # 打印响应状态码和消息
    print(f"{client_id} : Status Code: {response.status_code} Message: {response.text}")


if __name__ == "__main__":
    while True:
        test_connect("演员 1")
        test_connect("演员 2")
        test_connect("演员 3")
        test_connect("演员 4")
        # test_connect("演员 5")
        time.sleep(5)

    #
    # for i in range(1, 7):
    #     test_connect(f'u_{i}')
    # test_connect("测试用户")
    # get_list()
