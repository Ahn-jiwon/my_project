import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbproject
# 타겟 URL을 읽어서 HTML를 받아오고, (지상파>뉴스>예능>영화>스포츠>드라마 순
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
urls=['https://search.daum.net/search?nil_suggest=sugsch&w=tot&DA=GIQ&sq=%EB%B0%A9%EC%86%A1&o=2&sugo=15&q=%EB%B0%A9%EC%86%A1%ED%8E%B8%EC%84%B1%ED%91%9C',
                 'https://search.daum.net/search?DA=B3T&w=tot&rtmaxcoll=B3T&q=%EC%A2%85%ED%95%A9%ED%8E%B8%EC%84%B1%20%ED%8E%B8%EC%84%B1%ED%91%9C',
                'https://search.daum.net/search?DA=B3T&w=tot&rtmaxcoll=B3T&q=%EC%BC%80%EC%9D%B4%EB%B8%94%20%EC%97%B0%EC%98%88%2F%EC%98%A4%EB%9D%BD%20%ED%8E%B8%EC%84%B1%ED%91%9C',
                'https://search.daum.net/search?DA=B3T&w=tot&rtmaxcoll=B3T&q=%EC%BC%80%EC%9D%B4%EB%B8%94%20%EC%98%81%ED%99%94%20%ED%8E%B8%EC%84%B1%ED%91%9C',
                'https://search.daum.net/search?DA=B3T&w=tot&rtmaxcoll=B3T&q=%EC%BC%80%EC%9D%B4%EB%B8%94%20%EC%8A%A4%ED%8F%AC%EC%B8%A0%20%ED%8E%B8%EC%84%B1%ED%91%9C',
                'https://search.daum.net/search?DA=B3T&w=tot&rtmaxcoll=B3T&q=%EC%BC%80%EC%9D%B4%EB%B8%94%20%EB%93%9C%EB%9D%BC%EB%A7%88%20%ED%8E%B8%EC%84%B1%ED%91%9C']

for url in urls:
    data= requests.get(url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    channels_P = soup.select('#onProgram>td')
    channels_B = soup.select('div.wrap_tbl>div.tbl_head.head_type1>span')
    list_B = []
    for channel in channels_B:
        broad_tag = channel.select_one("a")
        if broad_tag:
            list_B.append(broad_tag.text)
    list_P = []
    for channel in channels_P:
        name_tag = channel.select("dl>dd.cont>a")
        name_tag2 = channel.select("dl>dd.cont")
        if name_tag:
            # list_temp = [tag.text for tag in name_tag]
            list_P.append(name_tag)
        else:
            list_P.append(name_tag2)
    for i in range(len(list_P)):
        broad_name = list_B[i]
        list_program = list_P[i]
        for tag in list_program:
            print(broad_name,':',tag.text)
            chan=broad_name
            prog=tag.text
            db.Tiri.insert_one({"채널": chan, "프로그램": prog})



# HTML을 BeautifulSoup이라는 라이브러리를 활용해 검색하기 용이한 상태로 만듦
# soup이라는 변수에 "파싱 용이해진 html"이 담긴 상태가 됨
# 이제 코딩을 통해 필요한 부분을 추출하면 된다.

#old_content > table > tbody > tr:nth-child(2)

# channels=soup.select("#onProgram > td > dl > dd.cont")
# channels=soup.select("#b3tColl>div>div>div.wrap_tbl")


# print(channels_B)

# print(len(channels))
# rank=0




# print(list_B)
# print(list_P)





    # P_tag=channel.select_one("td.point")
    # print(a_tag)
    # if name_tag is not None:
    #     # rank=rank+1
    #     print(broad_tag.text,name_tag.text)