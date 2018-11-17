import requests
import config
import asyncio
import time
from pyppeteer import connect


# 异步连接、程序监控

def pages_num(host):
    json_message = requests.get('http://{}:9222/json/list/'.format(host))
    return len(json_message.json())


def get_redis_ws(host):
    json_message = requests.get(url='{}{}/'.format(config.REDIS_SERVER, host))
    result = json_message.json()
    ws = result.get('data')
    return ws


async def main(host):
    web_socket = get_redis_ws(host)
    browser = await connect({'browserWSEndpoint': web_socket,
                             "ignoreHTTPSErrors": True})
    page_list = await browser.pages()
    print('等待清理')
    time.sleep(config.PAGE_SLEEP_TIME)
    for page in page_list:
        try:
            await page.close()
        except Exception as e:
            pass


def clear_unactive_page(host):
    asyncio.get_event_loop().run_until_complete(main(host))


while 1:
    for ws in config.WS_LIST:
        host = ws.get('host')
        page_num = pages_num(host)
        if page_num > (ws.get('max_page')):
            # 执行清除无效页面的函数
            clear_unactive_page(host)
            print('清理完毕')

    time.sleep(config.RUN_SLEEP_TIME)

