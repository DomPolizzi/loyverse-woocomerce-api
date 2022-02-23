
import requests
import json
import redis
from utils.vars import LOYVERSE_API_BASE, LOYVERSE_ALL_ITEMS_ENDPOINT, REDIS_HOST, REDIS_PORT
from auth.auth import Loytoken
from redis.commands.json.path import Path

# connect to our Redis instance
client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

def main():
    url = LOYVERSE_API_BASE + LOYVERSE_ALL_ITEMS_ENDPOINT
    headers = {
        'Authorization': Loytoken,
    }
    params = {
        'limit': 250
    }
    data = {}
    request = requests.get(url, params=params, headers=headers)

    if True:
        print(request.json())
    else:
        return Response(response, 404)
    


    #dumptest = json.dumps(request)
    #client.json().set('person:1', Path.rootPath(), jane)
    # print(request.text)
    # print(request.status_code)



#name = client.json().get('person:1', Path('.name'))
#print(name)


#post to redis


if __name__ == '__main__':
    main()
