import time
import matplotlib.pyplot as plt
import stylecloud
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from collections import Counter
from flask import render_template
from flask import Flask, request


app = Flask(__name__)


def make_wordcloud(data):
    # List에 담긴 테이터를 카운트
    count_data = Counter(data)
    dict_cnt_data = dict(count_data)

    # style cloud 사용
    # text에 주는 값은 dict형 변수로 변형
    # icon_name 값은  URL에서 검색 --> https://www.joydeepdeb.com/misc/font-awesome-5.html
    stylecloud.gen_stylecloud(text=dict_cnt_data, icon_name='fas fa-cloud', palette='colorbrewer.diverging.Spectral_11',
                              background_color='black', gradient='horizontal', output_name="static/image/Wordcloud.jpg", font_path='./Lib/font/NanumSquareRoundB.ttf')

    return  dict_cnt_data


def get_local_data(driver):
    local_list = []
    # 페이지당 10개 title이 존재함
    for i in range(10):
        tid = 'bbs_tr_{0}_bbs_title'.format(i)
        # Title 가져온 후 지역 이름만 저장
        # 마지막 페이지에는 title이 10개가 안될경우가 있어 Except 처리 추가.
        try:
            full_text = driver.find_element_by_id(tid).text
            local_text = ''.join([ i for i in full_text[25:-1] if not i.isdigit()])
            local_list.append(local_text)
        except:
            break

    return local_list


def search_all_text(driver, max_page):
    all_local_list = []
    local_list = []

    for i in range(max_page-1):
        local_list = get_local_data(driver)
        all_local_list = all_local_list + local_list
        # 다음 페이지 버튼 클릭
        driver.find_element_by_xpath('//*[@id="content"]/div[4]/div/a[2]').click()
        time.sleep(3)

    return all_local_list


#def main(sDate, eDate):
@app.route('/start_crawling',methods=['POST'])
def start_crawling():
    if request.method == 'POST':
        sDate = request.form['sDate']
        eDate = request.form['eDate']
    else:
        temp = None

    driver = webdriver.Chrome()
    driver.implicitly_wait(3)
    driver.get("https://www.safekorea.go.kr/idsiSFK/neo/sfk/cs/sfc/dis/disasterMsgList.jsp?menuSeq=679")
    driver.maximize_window()


    # 검색 조건 Clear(default 값 삭제)
    # 검색 조건 입력
    driver.find_element_by_xpath('//*[@id="search_start"]').clear()
    driver.find_element_by_xpath('//*[@id="search_end"]').clear()
    driver.find_element_by_xpath('//*[@id="search_start"]').send_keys(sDate)
    driver.find_element_by_xpath('//*[@id="search_end"]').send_keys(eDate)

    # 검색 버튼 클릭하여 실행, 웹페이지 로딩 시간을 위해 sleep 실행
    driver.find_element_by_xpath('//*[@id="content"]/div[1]/a').click()
    time.sleep(3)

    maxPage = driver.find_element_by_id('maxPage').text
    data = search_all_text(driver, int(maxPage))
    driver.close()
    dict_list = make_wordcloud(data)

    return render_template('result.html', result=dict_list)

@app.route('/')
def inputTest():
    return render_template('main.html')

if __name__ == "__main__":
    app.debug = True
    app.run(port=8080)
