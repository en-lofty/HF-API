import requests
import json
import sys
"""
The aim of this program is to check for a new post of one or more threads, and to check the inbox for new PM's.
If new post or PM's are found then the program will create a push notification using PushBullet to all devices on your
PushBullet account. Can be run as a CronJob, Windows Task Scheduler, or equivalent. 
"""

HF_API_KEY = "YOURKEY"
HF_URL = "https://" + HF_API_KEY + ":@hackforums.net/api/v1/{}/{}/"
PB_URL = 'https://api.pushbullet.com/v2/{}'
PB_ACCESS_TOKEN = 'YOURPUSHBULLETTOKENHERE'
THREAD_LIST = {"THREADID","THREADID2"} # You can watch as many threads as necessary


def api_query(method, id=None):
    request_url = HF_URL.format(method, id)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    return requests.get(request_url,
                        headers=headers).json()


def check_threads():
    json_data = open_json()
    for id in THREAD_LIST:
        thread_data = api_query("thread", id)["result"]
        current_count = thread_data['numreplies']
        try:
            old_count = json_data["threads"][id]
        except Exception:
            json_data["threads"][id] = current_count
            continue
        data = {}
        if current_count > old_count:
            data["title"] = "HackForums Alert"
            data["body"] = "https://hackforums.net/showthread.php?tid=" + id
            data["type"] = "note"
            push_bullet("pushes", data)
            json_data["threads"][id] = current_count
    write_json(json_data)


def check_pms():
    pms = api_query("inbox")["result"]
    json_data = open_json()
    current_id = pms['pms'][0]["pmid"]
    try:
        last_id = json_data["inbox"]["pmid"]
    except Exception:
        json_data["inbox"] = {"pmid": current_id}
        write_json(json_data)
        return
    json_data["inbox"] = {"pmid": current_id}
    data = {}
    if not current_id == last_id:
        data["title"] = "HackForums Alert"
        data["body"] = "New Private Message from {}".format(pms["pms"][0]["senderusername"])
        data["type"] = "note"
        json_data["inbox"]["pmid"] = current_id
        write_json(json_data)
        push_bullet("pushes", data)

def check():
    json_data = open_json()
    if len(json_data) == 0:
        json_data['threads'] = {}
        json_data['inbox'] = {}
        write_json(json_data)

def open_json():
    with open("config.json") as file:
        try:
            return json.load(file)
        except Exception:
            data = {}
            write_json(data)
            return json.load(file)


def write_json(data):
    with open("config.json", 'w') as file:
        json.dump(data, file, indent=2)


def push_bullet(method, options=None):
    headers = {"Access-Token": PB_ACCESS_TOKEN}
    requests_url = 'https://api.pushbullet.com/v2/{}'
    requests_url = requests_url.format(method)
    return requests.post(requests_url,headers=headers, data=options).json()

if __name__ == '__main__':
    options = sys.argv
    check()
    check_pms()
    check_threads()