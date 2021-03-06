import re, time
from selenium.webdriver.common.keys import Keys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import mongo
import ssl
from urllib.request import urlopen
import message
from selenium import webdriver
# driver = webdriver.Chrome('C:/chromedriver')

today = datetime.now()

# ---------------------------- 동적인 웹 -----------------------
'''
    msit, 
    kstartup
    seoul
    venture
    ccei
'''


def msit_scan(driver):
    name = '과학기술정보통신부'
    try:
        # 과학기술정보통신부 신청사업 url
        url = 'https://msit.go.kr/web/msipContents/contents.do?mId=MTE5'

        # 드라이버로 웹 열기
        driver.get(url)
        driver.implicitly_wait(3)

        # 공지목록 가져오기
        boards_list = driver.find_elements_by_xpath('//*[@id="result"]/div[2]/div/table/tbody/tr')

        # 지난번 저장했던 포스트 가져오기
        check_point = mongo.check_point_read(name)['title']

        # 기준이될 point  저장
        mongo.check_point_save(name, boards_list[0].find_element_by_class_name('title').text)

        for x in boards_list:
            title = x.find_element_by_class_name('title').text
            if check_point != title:
                date = '20' + x.find_element_by_xpath('./td[3]/span/span[3]').text + '.' + x.find_element_by_xpath(
                    './td[3]/span/span[2]').text
                link = x.find_element_by_tag_name('a').get_attribute('href')
                mongo.post_save(name, title, link, date, '')
                print('이름: ' + name + '\n제목:' + title + '\n링크: ' + link + '\n등록일: ' + date + '\n')
            else:
                break
    except Exception:
        message.site_error_push(name)


def kstartup_scan(driver):
    name = 'kstartup'
    # k- startup 신청게시판 url
    url = 'http://www.k-startup.go.kr/common/announcement/announcementList.do?mid=30004&bid=701&searchAppAt=A'
    board_url = 'http://www.k-startup.go.kr/common/announcement/announcementDetail.do?mid=30004&bid=701&searchPrefixCode=BOARD_701_001&searchPostSn='

    # 드라이버로 웹 열기
    driver.get(url)
    driver.implicitly_wait(3)
    driver.find_element_by_tag_name('body').send_keys(Keys.END)

    # 지난번 저장했던 포스트 가져오기
    check_point = mongo.check_point_read(name)['title']
    point_flag = False

    # 페이지 5회 이동
    pagecount=0
    while pagecount < 5:
        driver.find_element_by_xpath('//*[@id="listPlusAdd"]/a').click()
        driver.find_element_by_tag_name('body').send_keys(Keys.END)
        time.sleep(1)
        pagecount += 1

    try:
        # 중요 공지 가져오기
        impo_board = driver.find_element_by_class_name('ann_list_impor')
        boards_list = impo_board.find_elements_by_xpath('./li')

        # 중요공지는 10개내외로 순차적이지않으므로, 제목을 비교하여 이전에것들을 제외시킨다.
        for x in boards_list:
            # 제목
            title = x.find_element_by_tag_name('a').text.strip()
            if mongo.is_saved(title) is None:
                # 날짜 -  있는것과 없는것 구분처리
                try:
                    due_date = re.findall("\d{4}-\d{2}-\d{2}", x.find_element_by_xpath('./ul/li[3]').text.strip())
                    date = due_date[0]
                except Exception:
                    date = "상시모집"

                # link - bi.net_url, kstartup_url 구분처리
                params = re.findall("\d+", x.find_element_by_tag_name('a').get_attribute('href'))
                if len(params) == 2:  # bi-net 이동하는 함수일때, 파라미터가 2개임
                    link = "http://www.bi.go.kr/board/editView.do?boardVO.viewFlag=view&boardID=NOTICE&postSeq=" + \
                           params[0] + "&registDate=" + params[1]
                elif len(params) > 2:
                    link = board_url + params[2]
                else:
                    link = "링크오류"
                mongo.post_save(name, title, link, '', date)
                print('이름: ' + name + '\n제목:' + title + '\n링크: ' + link + '\n마감일: ' + date + '\n')

    except Exception:
        message.site_error_push(name + " < 중요공지부분 > ")
        pass

    try:
        # 페이지별 공지 가져오기
        ann_board = driver.find_element_by_class_name('ann_list')
        boards_list2 = ann_board.find_elements_by_xpath('./li')

        for x in boards_list2:
            title = x.find_element_by_tag_name('a').text.strip()
            if mongo.is_saved(title) is None and title != "":
                # 날짜 있는것과 없는것 구분처리
                try:
                    due_date = re.findall("\d{4}-\d{2}-\d{2}", x.find_element_by_xpath('./ul/li[3]').text.strip())
                    date = due_date[0]
                except Exception:
                    date = "상시모집"

                #  bi.net_url, kstartup_url 구분처리
                params = re.findall("\d+", x.find_element_by_tag_name('a').get_attribute('href'))
                if len(params) == 2:  # bi-net 이동하는 함수일때, 파라미터가 2개임
                    link = "http://www.bi.go.kr/board/editView.do?boardVO.viewFlag=view&boardID=NOTICE&postSeq=" + \
                           params[0] + "&registDate=" + params[1]
                elif len(params) > 2:
                    link = board_url + params[2]
                else:
                    link = "링크오류"
                mongo.post_save(name, title, link, '', date)
                print('이름: ' + name + '\n제목:' + title + '\n링크: ' + link + '\n마감일: ' + date + '\n')
            else:
                break
    except Exception:
        message.site_error_push(name + " < 일반 공지 부분 > ")
        pass


def seoul_scan(driver):
    names = ['서울특별시_고시공고']
    try:
        urls = ['http://www.seoul.go.kr/news/news_notice.do']

        for i in range(1):
            # 드라이버로 웹 열기
            driver.get(urls[i])
            driver.implicitly_wait(3)

            # 공지목록 가져오기
            boards_list = driver.find_elements_by_xpath('//*[@id="seoul-integrated-board"]/table/tbody/tr')

            # 지난번 저장했던 포스트 가져오기
            check_point = mongo.check_point_read(names[i])['title']

            # 기준이될 point  저장
            mongo.check_point_save(names[i], boards_list[0].find_element_by_tag_name('a').text.strip())

            for x in boards_list:
                title = x.find_element_by_tag_name('a').text.strip()
                if check_point != title:
                    date = x.find_element_by_xpath('./td[4]').text
                    link = urls[i] + '#view/' + x.find_element_by_tag_name('a').get_attribute('data-nttgroup')
                    mongo.post_save(names[i], title, link, date, '')
                    print('이름: ' + names[i] + '\n제목:' + title + '\n링크: ' + link + '\n등록일: ' + date + '\n')
                else:
                    break
    except Exception:
        message.site_error_push(names)


def venture_scan(driver):
    # 벤처기업협회
    names = ['벤처기업협회_사업공고']
    try:

        urls = ['https://www.venture.or.kr/#/home/bizNotice/h020101']
        # 벤처기업협회_사업공고
        driver.get(urls[0])
        driver.implicitly_wait(3)

        # 공지목록 가져오기
        boards_list = driver.find_elements_by_xpath('//*[@id="contents"]/ui-view/div/div[2]/div[2]/div[1]/ul/li')
        check_point = mongo.check_point_read(names[0])['title']
        mongo.check_point_save(names[0], boards_list[0].find_element_by_tag_name('a').text)

        for x in boards_list:
            title = x.find_element_by_tag_name('a').text
            if check_point != title:
                link = x.find_element_by_tag_name('a').get_attribute('href')
                date = x.find_element_by_css_selector('dd.info > span:nth-child(1)').text
                try:
                    sdate = date.split(" ~ ").pop(0)
                    edate = date.split(" ~ ").pop(1)
                except Exception: # 상시모집인 경우
                    sdate = date
                    edate = ''

                mongo.post_save(names[0], title, link, sdate,edate)
                print('이름: ' + names[0] + '\n제목:' + title + '\n링크: ' + link + '\n날짜: ' + date + '\n')
            else:
                break
    except Exception:
        message.site_error_push(names)


def ccei_scan(driver):
    # 창조경제혁신센터
    name = '창조경제혁신센터'
    try:
        url = 'https://ccei.creativekorea.or.kr/service/business_list.do'
        urls = ['https://ccei.creativekorea.or.kr/service/business_view.do?seq=']
        # pn=1&sPtime=now&pagePerContents=10&seq=3614&rownum=36
        # 드라이버로 웹 열기
        driver.get(url)
        driver.implicitly_wait(3)

        # 공지목록 가져오기
        boards_list = driver.find_elements_by_xpath('//*[@id="list_body"]/tr')

        # 지난번 저장했던 포스트 가져오기
        check_point = mongo.check_point_read(name)['title']

        # 기준이될 point  저장
        mongo.check_point_save(name, boards_list[0].find_element_by_tag_name('a').text)

        for x in boards_list:
            title = x.find_element_by_tag_name('a').text
            if check_point != title:
                seq = re.findall('\d+', x.find_element_by_tag_name('a').get_attribute('onclick'))
                link = urls[0] + seq[0]+"&rownum=" + seq[1]
                date = x.find_element_by_xpath('./td[5]').text  # 기간 (시작일 - 마감일)
                try:
                    edate = date.split("~").pop(1)
                    sdate = date.split("~").pop(0)
                    # 형식이 다른경우
                except Exception:
                    sdate = ''
                    edate = date
                mongo.post_save(name, title, link, sdate, edate)
                print('이름: ' + name + '\n제목:' + title + '\n링크: ' + link + '\n기간: ' + date + '\n')
            else:
                break
    except Exception:
        message.site_error_push(name)

# ----------------- 정적인 웹 크롤링 ---------------------------
''' 
kotra, nipa, sba, kisa, nia, kdata, moel, bepa
'''


def kotra_scan():
    # 코트라 사이트
    name = 'Kotra'
    try:

        url = 'http://www.kotra.or.kr'
        # 신청가능 사업 공지
        req = requests.get(
            'http://www.kotra.or.kr/kh/business/busiList.do?&MENU_CD=T0503&TOP_MENU_CD=T0500&LEFT_MENU_CD=T0503&PARENT_MENU_CD=&CO_TYPE=undefined&boardType=0')
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')

        # selector 로 데이터가저오기
        titles = soup.select('td > a')
        dates = soup.select('tr > td:nth-child(3)')

        # 체크포인트 불러오기, 저장하기
        mongo.check_point_save(name, titles[0].text.strip())

        # 데이터 변수로 받아서 txt 저장
        for i in range(len(titles)):
            title = titles[i].text
            link = url + titles[i].get('href').split('\'').pop(1)
            date = dates[i].text
            try:
                sdate = date.split(" ~ ").pop(0)
                edate = date.split(" ~ ").pop(1)
            except Exception:  # 상시모집인 경우
                sdate = date
                edate = ''

            if mongo.is_saved(title) is None:
                mongo.post_save(name, title, link, sdate, edate)
                print('이름: ' + name + '\n제목: ' + title + '\n링크: ' + link + '\n신청기간: ' + date + '\n')

    except Exception:
        message.site_error_push(name)

def nipa_scan():
    # 정보통신 산업진흥원 url
    names = ['정보통신산업진흥원1', '정보통신산업진흥원2']
    try:
        url = 'http://www.nipa.kr'
        uris = ['', '/biz/']
        urls = ['http://www.nipa.kr/board/boardList.it?boardNo=103&menuNo=32&page=1',
                'http://www.nipa.kr/biz/bizNotice.it?menuNo=18&page=1']

    # 신청가능 사업 공지
        for j in range(2):
            req = requests.get(urls[j])
            html = req.text
            soup = BeautifulSoup(html, 'html.parser')

            # selector 로 데이터가저오기
            titles = soup.select('td > a')
            dates = soup.select('tr > td.date')

            # 체크포인트 불러오기, 저장하기
            check_point = mongo.check_point_read(names[j])['title']
            mongo.check_point_save(names[j], titles[0].text)

            # 데이터 변수로 받아서 txt 저장
            for i in range(len(titles)):
                title = titles[i].text
                link = url + uris[j] + titles[i].get('onclick').split('\'').pop(1)
                date = dates[i].text

                if mongo.is_saved(title) is None:
                    mongo.post_save(names[j], title, link, date, '')
                    print('이름: ' + names[j] + '\n제목: ' + title + '\n링크: ' + link + '\n등록일: ' + date + '\n')
    except Exception:
        message.site_error_push(names[0])

def sba_scan():
    name = '서울산업진흥원'
    try:
        # 서울 산업 산업진흥원 url
        url = 'http://www.sba.seoul.kr/kr/sbcu01l1'
        # 신청가능 사업 공지
        req = requests.get(url)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')

        # selector 로 데이터가저오기
        titles = soup.select('td > a')
        dates = soup.select('tr > td:nth-child(3)')

        # 체크포인트 불러오기, 저장하기
        check_point = mongo.check_point_read(name)['title']
        mongo.check_point_save(name, titles[0].text.strip())

        # 데이터 변수로 받아서 txt 저장
        for i in range(len(titles)):
            title = titles[i].text.strip()
            seq = re.findall("\d+", titles[i].get('onclick'))
            link = "http://www.sba.seoul.kr/kr/sbcu01s1?bseq=" + seq[0]
            date = dates[i].text

            if check_point == title:
                break
            else:
                mongo.post_save(name, title, link, date, '')
                print('이름: ' + name + '\n제목: ' + title + '\n링크: ' + link + '\n등록일: ' + date + '\n')

    except Exception:
        message.site_error_push(name)


def kisa_scan():
    # 한국인터넷진흥원 사이트
    name = '한국인터넷진흥원'
    try:
        url = "https://www.kisa.or.kr"
        # 신청가능 사업 공지
        req = requests.get('https://www.kisa.or.kr/notice/notice_List.jsp')
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')

        # selector 로 데이터가저오기
        titles = soup.select('td > a')
        dates = soup.select('tr > td:nth-child(3)')

        # 체크포인트 불러오기, 저장하기
        check_point = mongo.check_point_read(name)['title']
        mongo.check_point_save(name, titles[0].text.strip())

        # 데이터 변수로 받아서 txt 저장
        for i in range(len(titles)):
            title = titles[i].text.strip()
            link = url + titles[i].get('href')
            date = dates[i].text.strip()

            if check_point == title:
                break
            else:
                mongo.post_save(name, title, link, date, '')
                print('이름: ' + name + '\n제목: ' + title + '\n링크: ' + link + '\n등록일: ' + date + '\n')
    except Exception:
        message.site_error_push(name)

def nia_scan():
    name = '한국정보화진흥원'
    try:
        # 한국 정보화 진흥원 url
        url = 'https://www.nia.or.kr/site/nia_kor/ex/bbs/List.do?cbIdx=99835'

        req = requests.get(url)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')

        # selector 로 데이터가저오기
        titles = soup.select('#sub_contentsArea > div.board_type01 > ul > li > a > span.subject')
        params = soup.select('#sub_contentsArea > div.board_type01 > ul > li > a')
        dates = soup.select('a > span.src > em:nth-child(1)')

        # 체크포인트 불러오기, 저장하기
        check_point = mongo.check_point_read(name)['title']
        mongo.check_point_save(name, " ".join(titles[0].text.split()))  # join과 split으로 중복 공백 제거

        # 데이터 변수로 받아서 txt 저장
        for i in range(len(titles)):
            title = " ".join(titles[i].text.split())  # join과 split으로 중복 공백 제거
            seq = re.findall('\d+', str(params[i].get('onclick')))
            link = "https://www.nia.or.kr/site/nia_kor/ex/bbs/View.do?cbIdx=" + seq[0] + "&bcIdx=" + seq[
                1] + "&parentSeq=" + seq[3]
            date = dates[i].text

            if check_point == title:
                break
            else:
                mongo.post_save(name, title, link, date, '')
                print('이름: ' + name + '\n제목: ' + title + '\n링크: ' + link + '\n등록일: ' + date + '\n')

    except Exception:
        message.site_error_push(name)


def kdata_scan():
    name = '한국데이터산업진흥원'
    try:
        url = 'https://www.kdata.or.kr/board/notice_01.html'

        context = ssl._create_unverified_context()
        result = urlopen(url, context=context)
        soup = BeautifulSoup(result.read(), "html.parser")

        # selector 로 데이터가저오기
        titles = soup.select('td > a')
        dates = soup.select('tr > td.date')

        # 체크포인트 불러오기, 저장하기
        check_point = mongo.check_point_read(name)['title']
        mongo.check_point_save(name, titles[0].text.strip())

        # 데이터 변수로 받아서 txt 저장
        for i in range(len(titles)):
            title = titles[i].text.strip()
            link = 'https://www.kdata.or.kr/board/' + titles[i].get('href')
            date = dates[i].text

            if check_point == title:
                break
            else:
                mongo.post_save(name, title, link, date, '')
                print('이름: ' + name + '\n제목: ' + title + '\n링크: ' + link + '\n등록일: ' + date + '\n')
    except Exception:
        message.site_error_push(name)

def moel_scan():
    # 고용노동부 사이트
    name = '고용노동부'
    try:

        url = 'http://www.moel.go.kr'
        # 신청가능 사업 공지
        req = requests.get('http://www.moel.go.kr/news/notice/noticeList.do')
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')

        # selector 로 데이터가저오기
        titles = soup.select('td > a')
        dates = soup.select('tr > td:nth-child(5)')

        # 체크포인트 불러오기, 저장하기
        check_point = mongo.check_point_read(name)['title']
        mongo.check_point_save(name, titles[0].text.split("]").pop(1).strip())

        # 데이터 변수로 받아서 txt 저장
        for i in range(len(titles)):
            title = titles[i].text.split("]").pop(1).strip()
            link = url + titles[i].get('href')
            date = dates[i].text

            if check_point == title:
                break
            else:
                mongo.post_save(name, title, link, date, '')
                print('이름: ' + name + '\n제목: ' + title + '\n링크: ' + link + '\n등록일: ' + date + '\n')
    except Exception:
        message.site_error_push(name)

def bepa_scan():
    name = '부산경제진흥원'
    try:
        url = 'https://www.bepa.kr/kor/view.do?no=209'

        context = ssl._create_unverified_context()
        result = urlopen(url, context=context)
        soup = BeautifulSoup(result.read(), "html.parser")

        # selector 로 데이터가저오기
        titles = soup.select('td > a')
        dates = soup.select('tr > td.date')
        num = soup.select('td.num')

        # 체크포인트 불러오기
        check_point = mongo.check_point_read(name)['title']

        # 데이터 변수로 받아서 txt 저장
        for i in range(len(titles)):
            if (num[i].text != "NOTICE"):
                # 공지사항이 아닌 체크포인트 저장하기
                if (num[i - 1].text == "NOTICE"):
                    mongo.check_point_save(name, titles[i].text.strip().split('\n').pop(0))

                title = titles[i].text.strip().split("\n").pop(0)
                link = 'https://www.bepa.kr' + titles[i].get('href')
                date = dates[i].text

                if check_point == title:
                    break
                else:
                    mongo.post_save(name, title, link, date, '')
                    print('이름: ' + name + '\n제목: ' + title + '\n링크: ' + link + '\n등록일: ' + date + '\n')
    except Exception:
        message.site_error_push(name)

def bi_scan():
    # 창업보육센터 네트워크시스템 사이트
    name = '창업보육센터 네트워크시스템'
    try:

        url = ["http://www.bi.go.kr/board/editView.do?boardID=RECRUIT&frefaceCode=ANNOUNCE&boardVO.postSeq=",
               "&boardVO.registDate=", "&boardVO.viewFlag=view"]
        # 신청가능 사업 공지
        req = requests.get('http://www.bi.go.kr/board/list.do?boardID=RECRUIT&frefaceCode=ANNOUNCE')
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')

        # selector 로 데이터가저오기
        titles = soup.select('td > a')
        dates = soup.select('tr > td:nth-child(5)')

        # 체크포인트 불러오기, 저장하기
        check_point = mongo.check_point_read(name)['title']
        mongo.check_point_save(name, titles[0].text.strip())

        # 데이터 변수로 받아서 txt 저장
        for i in range(len(titles)):
            title = titles[i].text.strip()
            params = re.findall("\d+", titles[i].get('href'))
            link = url[0] + params[0] + url[1] + params[1] + url[2]
            date = dates[i].text
            try:
                sdate = date.split(" ~ ").pop(0)
                edate = date.split(" ~ ").pop(1)
            except Exception:  # 상시모집인 경우
                sdate = date
                edate = ''

            if check_point == title:
                break
            else:
                mongo.post_save(name, title, link, sdate, edate)
                print('이름: ' + name + '\n제목: ' + title + '\n링크: ' + link + '\n신청기간: ' + date + '\n')
    except Exception:
        message.site_error_push(name)

def kised_scan():
    # 창업진흥원 사이트
    name = '창업진흥원'
    try:
        # 신청가능 사업 공지
        req = requests.get('https://www.kised.or.kr/not/notice2.asp')
        req.encoding = 'euc-kr'
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')

        # selector 로 데이터가저오기
        titles = soup.select('td > a')
        dates = soup.select('tr > td:nth-child(4)')

        # 체크포인트 불러오기, 저장하기
        check_point = mongo.check_point_read(name)['title']
        mongo.check_point_save(name, titles[0].text.strip())

        # 데이터 변수로 받아서 txt 저장
        for i in range(len(titles)):
            title = titles[i].text.strip()
            link = titles[i].get('href')
            date = dates[i].text
            if check_point == title:
                break
            else:
                mongo.post_save(name, title, link, date, '')
                print('이름: ' + name + '\n제목: ' + title + '\n링크: ' + link + '\n등록일: ' + date + '\n')
    except Exception:
        message.site_error_push(name)

def busanit_scan():
    try:
        for j in range(2):
            names = ['부산정보산업진흥원_공지사항', '부산정보산업진흥원_사업공고']
            urls = ['http://busanit.or.kr/board/list.asp?bcode=notice_e',
                    'http://busanit.or.kr/board/list.asp?bcode=notice']

            # 신청가능 사업 공지
            req = requests.get(urls[j])
            req.encoding = 'utf-8'
            html = req.text
            soup = BeautifulSoup(html, 'html.parser')

            # selector 로 데이터가저오기
            titles = soup.select('td > a')
            dates = soup.select('tr > td:nth-child(3)')

            # 체크포인트 불러오기, 저장하기
            check_point = mongo.check_point_read(names[j])['title']
            mongo.check_point_save(names[j], titles[0].text.strip())

            # 데이터 변수로 받아서 txt 저장
            for i in range(len(titles)):
                title = titles[i].text.strip()
                link = 'http://busanit.or.kr/board/' + titles[i].get('href')
                date = dates[i].text
                if check_point == title:
                    break
                else:
                    mongo.post_save(names[j], title, link, date, '')
                    print('이름: ' + names[j] + '\n제목: ' + title + '\n링크: ' + link + '\n등록일: ' + date + '\n')
    except Exception:
        message.site_error_push(name="부산정보산업진흥원")


def motie_scan():
    name = '산업통상자원부'
    try:
        # 신청가능 사업 공지
        req = requests.get('http://www.motie.go.kr/motie/ne/Notice/bbs/bbsList.do?bbs_cd_n=83&cate_n=1')
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')

        # selector 로 데이터가저오기
        titles = soup.select('div.ellipsis > a')
        dates = soup.select('tr > td:nth-child(5)')

        # 체크포인트 불러오기, 저장하기
        check_point = mongo.check_point_read(name)['title']
        mongo.check_point_save(name, titles[0].get('title'))

        # 데이터 변수로 받아서 txt 저장
        for i in range(len(titles)):
            title = titles[i].get('title')
            link = "http://www.motie.go.kr/motie/ne/Notice/bbs/"+titles[i].get('href')
            date = dates[i].text
            if check_point == title:
                break
            else:
                mongo.post_save(name, title, link, date, '')
                print('이름: ' + name + '\n제목: ' + title + '\n링크: ' + link + '\n등록일: ' + date + '\n')
    except Exception:
        message.site_error_push(name)

def seoulstartuphub_scan():
    name = '서울창업허브'
    try:
        # 신청가능 사업 공지
        url = 'http://seoulstartuphub.com/policy/supportList.do'
        context = ssl._create_unverified_context()
        result = urlopen(url, context=context)
        soup = BeautifulSoup(result.read(), "html.parser")

        # selector 로 데이터가저오기
        titles = soup.select('td.left> a')
        dates = soup.select('tr > td:nth-child(5)')

        # 체크포인트 불러오기, 저장하기
        check_point = mongo.check_point_read(name)['title']
        mongo.check_point_save(name, titles[0].text.strip())

        # 데이터 변수로 받아서 txt 저장
        for i in range(len(titles)):
            title = titles[i].text.strip()
            link = titles[i].get('href').strip()
            date = dates[i].text
            try:
                sdate = date.split(" ~ ").pop(0)
                edate = date.split(" ~ ").pop(1)
            except Exception:  # 상시모집인 경우
                sdate = date
                edate = ''

            sdate = sdate[0:4] + '.' + sdate[4:6] + '.' + sdate[6:8]
            edate = edate[0:4] + '.' + edate[4:6] + '.' + edate[6:8]

            if check_point == title:
                break
            else:
                mongo.post_save(name, title, link, sdate, edate)
                print('이름: ' + name + '\n제목: ' + title + '\n링크: ' + link + '\n신청기간: ' + date + '\n')

    except Exception:
        message.site_error_push(name)

def koita_scan():
    try:

        # 한국산업진흥협회
        names = ['한국산업진흥협회_공지사항', '한국산업진흥협회_사업공고', '한국산업진흥협회_정부 R&D 사업공고']
        urls = ['https://www.koita.or.kr/notice/notice_list.aspx', 'https://www.koita.or.kr/notice/gov_list.aspx?q=1',
                'https://www.koita.or.kr/certificate/prnd_board2_list.aspx']
        url = ['https://www.koita.or.kr/notice/notice_view.aspx?no=',
               'https://www.koita.or.kr/notice/gov_view.aspx?q=1&no=',
               'https://www.koita.or.kr/certificate/prnd_board4_view.aspx?no=']

        for j in range(3):

            # 신청가능 사업 공지
            req = requests.get(urls[j])
            html = req.text
            soup = BeautifulSoup(html, 'html.parser')

            # selector 로 데이터가저오기
            titles = soup.select('td > a')
            dates = soup.select('tr > td:nth-child(5)')

            # 체크포인트 불러오기, 저장하기
            check_point = mongo.check_point_read(names[j])['title']
            mongo.check_point_save(names[j], titles[0].text.strip())

            # 데이터 변수로 받아서 txt 저장
            for i in range(len(titles)):
                title = titles[i].text.strip()
                link = url[j] + re.findall("\d+", titles[i].get('href')).pop()
                date = dates[i].text
                if check_point == title:
                    break
                else:
                    mongo.post_save(names[j], title, link, date, '')
                    print('이름: ' + names[j] + '\n제목: ' + title + '\n링크: ' + link + '\n등록일: ' + date + '\n')
    except Exception:
        message.site_error_push(name="한국산업진훙협회")


def kisdi_scan():
    # 정보통신정책연구원 - 링크 수정
    name = '정보통신정책연구원'
    try:
        # 신청가능 사업 공지
        req = requests.get(
            'http://www.kisdi.re.kr/kisdi/fp/kr/board/listSingleBoard.do?cmd=listSingleBoard&sBoardId=GPK_NOTICE&sEntDate=&eEntDate=&searchValue=&listScale=10&curPage=1&ordTxt=M001005')
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')

        # selector 로 데이터가저오기
        titles = soup.select('td.board-title > a')
        dates = soup.select('tr > td:nth-child(4)')

        # 체크포인트 불러오기, 저장하기
        mongo.check_point_read(name)
        check_point = mongo.check_point_read(name)['title']
        mongo.check_point_save(name, titles[0].text.strip())

        # 데이터 변수로 받아서 txt 저장
        for i in range(len(titles)):
            title = titles[i].text.strip()
            tmp = titles[i].get('href')
            link = 'http://www.kisdi.re.kr/' + "".join(tmp.split())
            date = dates[i].text.strip()

            if check_point == title:
                break
            else:
                mongo.post_save(name, title, link, date, '')
                print('이름: ' + name + '\n제목: ' + title + '\n링크: ' + link + '\n등록일: ' + date + '\n')
    except Exception:
        message.site_error_push(name)

def kai_scan():
    # 지능정보산업협회
    name = '지능정보산업협회'
    try:
        # 신청가능 사업 공지
        req = requests.get('http://www.k-ai.or.kr/kr/information/notice.php')
        req.encoding = 'utf-8'
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')

        # selector 로 데이터가저오기
        top_count = soup.select('span.notice-icon')
        titles = soup.select('td > a')
        dates = soup.select('tr > td:nth-child(3)')

        # 체크포인트 불러오기, 저장하기
        check_point = mongo.check_point_read(name)['title']
        # top_count 공지갯수를 세서 공지를 제외하고 check_point를 저장
        mongo.check_point_save(name, titles[len(top_count)].text.strip())

        # 데이터 변수로 받아서 txt 저장
        for i in range(len(titles)):
            title = titles[i].text.strip()
            if check_point != title:
                link = 'http://www.k-ai.or.kr' + titles[i].get('href')
                date = dates[i].text
                try:
                    edate = date.split("~").pop(1)
                    sdate = date.split("~").pop(0)
                # 형식이 다른경우
                except Exception:
                    sdate = date
                    edate = ''
                # 상단고정 공지때문에 저장된건 중복 걸러주기
                if mongo.is_saved(title) is None:
                    mongo.post_save(name, title, link, sdate, edate)
                    print('이름: ' + name + '\n제목:' + title + '\n링크: ' + link + '\n날짜: ' + date + '\n')
            else:
                break
    except Exception:
        message.site_error_push(name)

def busan_scan():
    # 부산광역시 사이트
    name = '부산광역시'
    try:
        # 신청가능 사업 공지
        req = requests.get('http://www.busan.go.kr/nbgosi')
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')

        # selector 로 데이터가저오기
        titles = soup.select('td > a')
        dates = soup.select('tr > td:nth-child(4)')

        # 체크포인트 불러오기, 저장하기
        check_point = mongo.check_point_read(name)['title']
        mongo.check_point_save(name, titles[0].text.strip())

        # 데이터 변수로 받아서 txt 저장
        for i in range(len(titles)):
            title = titles[i].text.strip()
            if check_point != title:
                link = 'http://www.busan.go.kr' + titles[i].get('href')
                date = dates[i].text.strip()
                mongo.post_save(name, title, link, date, '')
                print('이름: ' + name + '\n제목: ' + title + '\n링크: ' + link + '\n등록일: ' + date + '\n')
            else:
                break
    except Exception:
        message.site_error_push(name)


def koraia_scan():
    name = '한국인공지능협회'
    try:
        # 신청가능 사업 공지
        req = requests.get('https://www.koraia.org/board/index.html?id=bizalim&page=1')
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        # selector 로 데이터가저오기
        titles = soup.select('td.wz_subject > a')
        dates = soup.select('tr > td:nth-child(3)')
        dates.pop(0)
        dates.pop(0)

        # 체크포인트 불러오기, 저장하기
        check_point = mongo.check_point_read(name)['title']
        mongo.check_point_save(name, titles[0].text.strip())

        # 데이터 변수로 받아서 txt 저장
        for i in range(len(titles)):
            title = titles[i].text.strip()
            if check_point != title:
                link = 'https://www.koraia.org/board/' + titles[i].get('href')
                date = dates[i].text
                mongo.post_save(name, title, link, date, '')
                print('이름: ' + name + '\n제목: ' + title + '\n링크: ' + link + '\n등록일: ' + date + '\n')
            else:
                break
    except Exception:
        message.site_error_push(name)


def ideamaru_scan():
    name = '아이디어마루'
    try:
        # 신청가능 사업 공지
        req = requests.get('https://www.ideamaru.or.kr/business/sch/notice')
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')

        # selector 로 데이터가저오기
        titles = soup.select('td > span > a')
        dates = soup.select('tr > td:nth-child(4)')

        # 체크포인트 불러오기, 저장하기
        check_point = mongo.check_point_read(name)['title']
        mongo.check_point_save(name, titles[0].text.strip())

        # 데이터 변수로 받아서 txt 저장
        for i in range(len(titles)):
            title = titles[i].text.strip()
            if check_point != title:
                param = re.findall("\d+", titles[i].get('href'))
                link = 'https://www.ideamaru.or.kr/business/sch/notice/view?ATCL_NUM=' + param[0]
                date = dates[i].text
                mongo.post_save(name, title, link, date, '')
                print('이름: ' + name + '\n제목: ' + title + '\n링크: ' + link + '\n등록일: ' + date + '\n')
            else:
                break
    except Exception:
        message.site_error_push(name)


def btp_scan():
    try:
        names = ['부산테크노파크_사업공고', '부산테크노파크_공지사항']
        urls = ['http://www.btp.or.kr/index.php?action=BD0000M&pagecode=P000000010&language=KR',
                'http://www.btp.or.kr/index.php?action=BD0000M&pagecode=P000000013&language=KR']
        for j in range(2):
            for pageindex in range(1, 3):       # 1-2페이지까지 돌림
                # 신청가능 사업 공지
                req = requests.get(urls[j]+"&pageIndex="+str(pageindex))
                req.encoding = 'utf-8'
                html = req.text
                soup = BeautifulSoup(html, 'html.parser')

                # selector 로 데이터가저오기
                titles = soup.select(' tr > td.ui-pleft20 > a')
                if j == 0:
                    dates = soup.select('tr > td:nth-child(3)')
                else:
                    dates = soup.select('tr > td:nth-child(4)')
                # 데이터 변수로 받아서 txt 저장
                for i in range(len(titles)):
                    title = titles[i].text.strip()
                    if mongo.is_saved(title) is None:
                        param = re.findall("\d+", titles[i].get('href'))
                        link = urls[j] + '&command=View&idx=' + param[0]
                        date = dates[i].text.split("(").pop(0).strip()
                        try:
                            edate = date.split("~").pop(1)
                            sdate = date.split("~").pop(0)
                        # 형식이 다른경우
                        except Exception:
                            sdate = ''
                            edate = date
                        # 상단고정 공지때문에 저장된건 중복 걸러주기
                        mongo.post_save(names[j], title, link, sdate, edate)
                        print('이름: ' + names[j]+ '\n제목:' + title + '\n링크: ' + link + '\n날짜: ' + sdate + edate + '\n')
    except Exception:
        message.site_error_push(name="부산테크노파트")

def sbsc_scan():

    # 서울시 지원사업
    name = '서울시 지원사업'
    try:
        urls = ['https://sbsc.seoul.go.kr/fe/support/seoul/NR_view.do?bbsCd=1&bbsSeq=','&currentPage=1&searchVals=&bbsGrpCds_all=on&orgCd=']
        req = requests.get('https://sbsc.seoul.go.kr/fe/support/seoul/NR_list.do?bbsCd=1')
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')

        # selector 로 데이터가저오기
        titles = soup.select('td > a')
        dates = soup.select('tr > td:nth-child(4)')

        # 체크포인트 불러오기, 저장하기
        check_point = mongo.check_point_read(name)['title']
        mongo.check_point_save(name, titles[0].text.strip())

        # 데이터 변수로 받아서 txt 저장
        for i in range(len(titles)):
            title = titles[i].text.strip()
            seq = re.findall("\d+", titles[i].get('onclick'))
            link = urls[0] + seq[0] + urls[1]
            date = dates[i].text.strip()
            sdate = date[0:10]
            edate = date[10:20]

            if check_point == title:
                break
            else:
                mongo.post_save(name, title, link, sdate, edate)
                print('이름: ' + name + '\n제목: ' + title + '\n링크: ' + link + '\n신청기간: ' + sdate + ' ~ ' + edate +'\n')

        # 중앙정부 지원사업
        name = '중앙정부 지원사업'
        req = requests.get('https://sbsc.seoul.go.kr/fe/support/bizinfo/NR_list.do')
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')

        # selector 로 데이터가저오기
        titles = soup.select('td > a')
        dates = soup.select('tr > td:nth-child(5)')

        # 체크포인트 불러오기, 저장하기
        check_point = mongo.check_point_read(name)['title']
        mongo.check_point_save(name, titles[0].text.strip())

        # 데이터 변수로 받아서 txt 저장
        for i in range(len(titles)):
            title = titles[i].text.strip()
            link = titles[i].get('href').strip()
            date = dates[i].text.strip()

            if check_point == title:
                break
            else:
                mongo.post_save(name, title, link, date, '')
                print('이름: ' + name + '\n제목: ' + title + '\n링크: ' + link + '\n등록일: ' + date + '\n')
    except Exception:
        message.site_error_push(name)


def mss_scan():
    try:
        # 중소벤처기업부
        names = ['중소벤처기업부_공지사항', '중소벤처기업부_사업공고']

        uris = ['https://www.mss.go.kr/site/smba/ex/bbs/View.do?cbIdx=', '&bcIdx=', '&parentSeq=',  ' ', '&searchRltnYn=A']
        urls = ['https://www.mss.go.kr/site/smba/ex/bbs/List.do?cbIdx=81', 'https://www.mss.go.kr/site/smba/ex/bbs/List.do?cbIdx=126&searchRltnYn=A']

        # 신청가능 사업 공지
        for j in range(2):
            req = requests.get(urls[j])
            html = req.text
            soup = BeautifulSoup(html, 'html.parser')

            # selector 로 데이터가저오기
            titles = soup.select('td.subject > a')
            dates = soup.select('tr > td:nth-child(5)')
            fixed = soup.select('td.num')

            # 체크포인트 불러오기, 저장하기
            check_point = mongo.check_point_read(names[j])['title']

            # 데이터 변수로 받아서 txt 저장
            k = 0  # check point 설정 변수
            for i in range(len(titles)):
                if (j == 0):  # 공지사항에서만
                    if (fixed[i].text.strip() == ''):       # 글번호가 아니면 다음글로 넘김
                        k += 1
                        continue
                title = titles[i].text.strip()
                seq = re.findall("\d+", titles[i].get('onclick'))
                link = uris[0] + seq[0] + uris[1] + seq[1] + uris[2] + seq[1] + uris[j+3]
                date = dates[i].text

                if check_point == title:
                    break
                else:
                    mongo.post_save(names[j], title, link, date, '')
                    print('이름: ' + names[j] + '\n제목: ' + title + '\n링크: ' + link + '\n등록일: ' + date + '\n')

            mongo.check_point_save(names[j], titles[k].text.strip())

    except Exception:
        message.site_error_push(name="중소벤처기업부")

