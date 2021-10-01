#!/usr/bin/env python
# coding: utf-8

import json
import requests
import secrets


CLIENT_ID = []
CLIENT_SECRET = []


# 1. Generate a new Code Verifier / Code Challenge.
def get_new_code_verifier() -> str:
    token = secrets.token_urlsafe(100)
    return token[:128]


# 2. Print the URL needed to authorise your application.
def print_new_authorisation_url(code_challenge: str):
    global CLIENT_ID

    url = f'https://myanimelist.net/v1/oauth2/authorize?response_type=code&client_id={CLIENT_ID}&code_challenge={code_challenge}'
    print(f'Authorise your application by clicking here: {url}\n')


# 3. Once you've authorised your application, you will be redirected to the webpage you've
#    specified in the API panel. The URL will contain a parameter named "code" (the Authorisation
#    Code). You need to feed that code to the application.
def generate_new_token(authorisation_code: str, code_verifier: str) -> dict:
    global CLIENT_ID, CLIENT_SECRET

    url = 'https://myanimelist.net/v1/oauth2/token'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': authorisation_code,
        'code_verifier': code_verifier,
        'grant_type': 'authorization_code'
    }

    response = requests.post(url, data)
    response.raise_for_status()  # Check whether the requests contains errors

    token = response.json()
    response.close()
    print('Token generated successfully!')

    with open('token.json', 'w') as file:
        json.dump(token, file, indent = 4)
        print('Token saved in "token.json"')

    return token


# 4. Test the API by requesting your profile information
def print_user_info(access_token: str):
    url = 'https://api.myanimelist.net/v2/users/@me'
    response = requests.get(url, headers = {
        'Authorization': f'Bearer {access_token}'
        })
    
    response.raise_for_status()
    user = response.json()
    response.close()

    print(f"\n>>> Greetings {user['name']}! <<<")


if __name__ == '__main__':
    code_verifier = code_challenge = get_new_code_verifier()
    print_new_authorisation_url(code_challenge)

    authorisation_code = input('Copy-paste the Authorisation Code: ').strip()
    token = generate_new_token(authorisation_code, code_verifier)

    print_user_info(token['access_token'])

###

#pull every anime in rankings list
#pull anime details using rankings list IDs

import requests
import pandas as pd
import time
import sys


h = {
    'Authorization': "Bearer []",
    'Accept': "application/json"
}

mal = []
details = []
batchsize = 600

url = "https://api.myanimelist.net/v2/anime/ranking?ranking_type=tv&limit=500"

while True:
    r = requests.get(url, headers = h).json()
    for node in r['data']:
        list = {
            'anime_id' : node['node']['id'],
            'anime_rank' : node['ranking']['rank'],
            'anime_title': node['node']['title']
        }
        mal.append(list)
        url = r.get('paging',{}).get('next')
    if url is None:
        break
print('Anime IDs loaded')

for i in range(0, len(mal), batchsize):
    batch = mal[i:i+batchsize]
    for ID in batch:
        i = ID['anime_id']
        r2 = requests.get('https://api.myanimelist.net/v2/anime/{}?fields=id,title,main_picture,alternative_titles,start_date,end_date,mean,rank,popularity,genres,my_list_status,num_episodes,studios,synopsis,related_anime'.format(i), headers = h).json()
        list = {
            'id': r2['id'],
            'title': r2.get('title'),
            'other_titles': r2.get('alternative_titles'),
            'genre': r2.get('genres'),
            'start_date': r2.get('start_date'),
            'end_date': r2.get("end_date"),
            'synopsis': r2.get('synopsis'),
            'mean_score': r2.get('mean'),
            'num_episodes': r2.get('num_episodes'),
            'related_anime': r2.get('related_anime'),
            'studios': r2.get('studios')
        }
        details.append(list)
        print(r2['title'] + ' ' + str(ID['anime_rank']))
    for remaining in range(300, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconds remaining.".format(remaining))
        sys.stdout.flush()
        time.sleep(1)

    sys.stdout.write("\rComplete!            \n")

mal_pd = pd.DataFrame(details,index=range(len(details)))

mal_pd.to_csv('C:/Users/akpan/Desktop/all_anime_data.csv')

###

#username scraping

from lxml import html
import requests

# details = []

while True:
    link = 'https://myanimelist.net/users.php?lucky=1'
    page = requests.get(link)
    tree = html.fromstring(page.content)
    names = tree.xpath('//td[@align="center"]/div/a/text()')
    details.extend(names)
    for remaining in range(3, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconds remaining.".format(remaining))
        sys.stdout.flush()
        time.sleep(1)


###

#user list scraping

import requests
import pandas as pd
import time
import sys
import csv

h = {
    'Authorization': "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjkwYjI1OTY4ZGQ5NTZmYjIzZDg3NjI5YTczYmNlYzBmYWQwZWQ2NjkxZmEwMWZkMDUzOTNiN2M3MGM1Y2U5NmRkMzgwZDc0NmY4ZWVjMjA2In0.eyJhdWQiOiI2M2UxMTc3MDY3OTEzZDUwODNiODQ2ZDJjY2YxYWExYiIsImp0aSI6IjkwYjI1OTY4ZGQ5NTZmYjIzZDg3NjI5YTczYmNlYzBmYWQwZWQ2NjkxZmEwMWZkMDUzOTNiN2M3MGM1Y2U5NmRkMzgwZDc0NmY4ZWVjMjA2IiwiaWF0IjoxNjMyOTc3OTQwLCJuYmYiOjE2MzI5Nzc5NDAsImV4cCI6MTYzNTU2OTk0MCwic3ViIjoiMTIwNTM4NjYiLCJzY29wZXMiOltdfQ.bCYdTk6Wmp2hAZuYG7dwZhnyduJA5x5-8C8TlRNsRc2d8dPF02ArYMqhy3P6ZyiYoW5Jydt6Ooj13saJczzYP-_WmlWkQB1tkYyJ75V2ZbLPRGQ-Zi179o3vmtINhUivEcnuLgrO4d7ieY2dkoNUODmS-d9Qs5dD3th7PWNQfJpH_M4dAPOtwpdNFd7F-YM-eK6YEyTFCRjTYVYu_lS4I0c8vqx7gQM0dN20YMKOGYq5XflXka57CePw-jq074lPz5j-sUDbb3UBrHHYDu-l75fvhc9C_34nw1397LIAIIKkpANTYYzItwsJuXRVDq20OU2tNQAbTBssJBAlb4TjSg",
    'Accept': "application/json"
}

file = open('2109029mal_users_scrape.csv', "r")
csv_reader = csv.reader(file)

batchsize = 150
user_lists = []
lists_from_csv = []

for row in csv_reader:
    lists_from_csv.append(row)
    
details = [i[1] for i in lists_from_csv]
    
for i in range(2001,4100,batchsize):
    z = details[i:i+batchsize]    
    for a in z:
        try:
            try:
                url = "https://api.myanimelist.net/v2/users/{}/animelist?fields=list_status&limit=100"
                while True:
                    r2 = requests.get(url.format(a), headers = h).json()
                    for data in r2['data']:
                        if data['list_status']['status'] == 'completed':
                            list_4 = {
                                'username': a,
                                'id': data['node']['id'],
                                'title': data['node']['title'],
                                'score': data['list_status']['score'],
                                'is_rewatching': data['list_status']['is_rewatching'],
                                'updated_at': data['list_status']['updated_at']
                            }
                            user_lists.append(list_4)
    #                         print(data['node']['title'])
                        else:
                            pass
                    url = r2.get('paging',{}).get('next')
    #             print(data['node']['title'])
                if url is None:
                    pass 
            except AttributeError:
                pass
        except KeyError:
            pass
        print(a)
    for remaining in range(300, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconds remaining.".format(remaining))
        sys.stdout.flush()
        time.sleep(1)


mal_user_lists = pd.DataFrame(user_lists,index=range(len(user_lists)))

mal_user_lists.to_csv('C:/Users/akpan/Desktop/210930_2001thru4100userslists.csv')