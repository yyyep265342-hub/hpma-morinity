import requests
import sys

PAYLOAD = {
    'client_type': 'h5',
    'act': 'recommd_by_role',
    'search_type': 'role',
    'count': '15',
    'view_loc': 'search_cond',
    'gender__or': '2',
    'card_list': '[{"card_list__id":"1198","card_list__level":15}]',
    'wand__and': '10000020',
    'rare_cloth__and': '10453621,10453821,10454011,10454025,10454059,10454122',
    'frame__or': '4101162',
    'order_by': '',
    'page': '1',
    'exter': 'cbg.163.com',
}

HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'https://hp.cbg.163.com/',
    'Origin': 'https://hp.cbg.163.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
}

URL = 'https://hp.cbg.163.com/cgi-bin/recommend.py?client_type=h5&act=recommd_by_role'

def main():
    try:
        resp = requests.post(URL, data=PAYLOAD, headers=HEADERS, timeout=15)
        print(f'HTTP状态码：{resp.status_code}')
        print(f'响应内容：{resp.text[:500]}')  # 打印前500字符
        resp.raise_for_status()
        data = resp.json()
        results = data.get('result', [])
        print(f'查询成功，找到 {len(results)} 个符合条件的账号')
        if results:
            print('有符合条件的账号，触发通知')
            sys.exit(1)
        else:
            print('暂无符合条件的账号')
            sys.exit(0)
    except Exception as e:
        print(f'查询出错：{type(e).__name__}: {e}')
        sys.exit(0)  # 出错一律返回0，不触发通知

if __name__ == '__main__':
    main()
