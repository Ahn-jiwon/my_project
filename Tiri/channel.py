from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
app = Flask(__name__)
client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbproject



# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'apple'

# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)
import jwt

# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime

# 회원가입 시엔, 비밀번호를 암호화하여 DB에 저장해두는 게 좋습니다.
# 그렇지 않으면, 개발자(=나)가 회원들의 비밀번호를 볼 수 있으니까요.^^;
import hashlib

#################################
##  HTML을 주는 부분             ##
#################################
@app.route('/')
def home():
   return render_template('index1.html')

@app.route('/login')
def login():
   return render_template('Login.html')

@app.route('/register')
def register():
   return render_template('register.html')

#################################
##  로그인을 위한 API            ##
#################################

# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/api/register', methods=['POST'])
def api_register():
   id_receive = request.form['id_give']
   pw_receive = request.form['pw_give']
   nickname_receive = request.form['nickname_give']

   pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

   db.userinf.insert_one({'id':id_receive,'pw':pw_hash,'nick':nickname_receive})

   return jsonify({'result': 'success'})

# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    print(id_receive, pw_receive)

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.userinf.find_one({'id':id_receive,'pw':pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
         'id': id_receive,
         'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        print(token)
        # token을 줍니다.
        return jsonify({'result': 'success','token':token})
    # 찾지 못하면
    else:
        print("no info")
        return jsonify({'result': 'fail', 'msg':'아이디/비밀번호가 일치하지 않습니다.'})

# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
# 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)
@app.route('/api/nick', methods=['GET'])
def api_valid():
   # 토큰을 주고 받을 때는, 주로 header에 저장해서 넘겨주는 경우가 많습니다.
   # header로 넘겨주는 경우, 아래와 같이 받을 수 있습니다.
   token_receive = request.headers['token_give']

   # try / catch 문?
   # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.

   try:
      # token을 시크릿키로 디코딩합니다.
      # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
      payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
      print(payload)

      # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
      # 여기에선 그 예로 닉네임을 보내주겠습니다.
      userinfo = db.userinf.find_one({'id':payload['id']},{'_id':0})
      return jsonify({'result': 'success','nickname':userinfo['nick']})
   except jwt.ExpiredSignatureError:
      # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
      return jsonify({'result': 'fail', 'msg':'로그인 시간이 만료되었습니다.'})




## Tiri API 역할을 하는 부분
@app.route('/tiris')
def home1():
    return render_template('index.html')

@app.route('/tiri', methods=['GET'])
def tiri_scrap():
    # 타겟 URL을 읽어서 HTML를 받아오고, (지상파>뉴스>예능>영화>스포츠>드라마 순
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    urls = [
        'https://search.daum.net/search?nil_suggest=sugsch&w=tot&DA=GIQ&sq=%EB%B0%A9%EC%86%A1&o=2&sugo=15&q=%EB%B0%A9%EC%86%A1%ED%8E%B8%EC%84%B1%ED%91%9C',
        'https://search.daum.net/search?DA=B3T&w=tot&rtmaxcoll=B3T&q=%EC%A2%85%ED%95%A9%ED%8E%B8%EC%84%B1%20%ED%8E%B8%EC%84%B1%ED%91%9C',
        'https://search.daum.net/search?DA=B3T&w=tot&rtmaxcoll=B3T&q=%EC%BC%80%EC%9D%B4%EB%B8%94%20%EC%97%B0%EC%98%88%2F%EC%98%A4%EB%9D%BD%20%ED%8E%B8%EC%84%B1%ED%91%9C',
        'https://search.daum.net/search?DA=B3T&w=tot&rtmaxcoll=B3T&q=%EC%BC%80%EC%9D%B4%EB%B8%94%20%EC%98%81%ED%99%94%20%ED%8E%B8%EC%84%B1%ED%91%9C',
        'https://search.daum.net/search?DA=B3T&w=tot&rtmaxcoll=B3T&q=%EC%BC%80%EC%9D%B4%EB%B8%94%20%EC%8A%A4%ED%8F%AC%EC%B8%A0%20%ED%8E%B8%EC%84%B1%ED%91%9C',
        'https://search.daum.net/search?DA=B3T&w=tot&rtmaxcoll=B3T&q=%EC%BC%80%EC%9D%B4%EB%B8%94%20%EB%93%9C%EB%9D%BC%EB%A7%88%20%ED%8E%B8%EC%84%B1%ED%91%9C']
    list_ind = ['방송3사', '뉴스', '예능', '영화', '스포츠', '드라마']
    TV_list = []
    for ind, url in zip(list_ind, urls):
        print(ind)
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
                # a태그가 없을 경우에도 출력가능
                list_P.append(name_tag2)
        for i in range(len(list_P)):
            broad_name = list_B[i]
            list_program = list_P[i]
            for tag in list_program:
                print(broad_name,':',tag.text)
                if (broad_name=='KBS1') or (broad_name=='KBS2') or (broad_name=='MBC') or (broad_name=='SBS') or (broad_name=='EBS1') or (broad_name=='EBS2') or (broad_name=='OBS 경인TV'):
                    TV_list.append({'카테고리': list_ind[0], "채널": broad_name, "프로그램": tag.text})
                if (broad_name=='JTBC') or (broad_name=='MBN') or (broad_name=='TV 조선') or (broad_name=='채널A'):
                    TV_list.append({'카테고리': list_ind[1], "채널": broad_name, "프로그램": tag.text})
                if (broad_name == '코미디TV') or (broad_name == 'KBS Joy') or (broad_name == 'tvN') or (broad_name == 'MBC every1') or (broad_name == 'E채널') or (broad_name == 'JTBC2') or (broad_name == 'O tvN') or (broad_name=='CH W'):
                    TV_list.append({'카테고리': list_ind[2], "채널": broad_name, "프로그램": tag.text})
                if (broad_name=='월드 클래식 무비') or (broad_name=='OCN') or (broad_name=='OCN Movies') or (broad_name=='OCN Thrills') or (broad_name=='Asia M') or (broad_name=='Mplex') or (broad_name=='THE MOVIE') or (broad_name=='UXN'):
                    TV_list.append({'카테고리': list_ind[3], "채널": broad_name, "프로그램": tag.text})
                if (broad_name=='Golf Channel Korea') or (broad_name=='KBS N 스포츠') or (broad_name=='MBC스포츠 플러스') or (broad_name=='SBS스포츠') or (broad_name=='JTBC GOLF') or (broad_name=='JTBC GOLF&SPORTS') or (broad_name=='OGN') or (broad_name=='SBS골프'):
                    TV_list.append({'카테고리': list_ind[4], "채널": broad_name, "프로그램": tag.text})
                if (broad_name=='KBS 드라마') or (broad_name=='드라맥스') or (broad_name=='MBC 드라마넷') or (broad_name=='SBS플러스') or (broad_name=='MBC ON') or (broad_name=='AXN') or (broad_name=='Asia N') or (broad_name=='CH.U'):
                    TV_list.append({'카테고리': list_ind[5], "채널": broad_name, "프로그램": tag.text})
    return jsonify({'result': 'success', 'msg': '불러오기 성공!','TV_list': TV_list})

# @app.route('/cal')
# def home2():
#     return render_template('cal.html')

# @app.route('/tiri', methods=['POST'])
# def post_info():
#     # 1. 클라이언트로부터 데이터를 받기
#     # 2. meta tag를 스크래핑하기
#     # 3. mongoDB에 데이터 넣기
#     return jsonify({'result': 'success', 'msg': 'POST 연결되었습니다!'})




if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

# HTML을 BeautifulSoup이라는 라이브러리를 활용해 검색하기 용이한 상태로 만듦
# soup이라는 변수에 "파싱 용이해진 html"이 담긴 상태가 됨
# 이제 코딩을 통해 필요한 부분을 추출하면 된다.

#old_content > table > tbody > tr:nth-child(2)
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
