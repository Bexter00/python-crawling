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
    # List�� ��� �����͸� ī��Ʈ
    count_data = Counter(data)
    dict_cnt_data = dict(count_data)

    # style cloud ���
    # text�� �ִ� ���� dict�� ������ ����
    # icon_name ����  URL���� �˻� --> https://www.joydeepdeb.com/misc/font-awesome-5.html
    stylecloud.gen_stylecloud(text=dict_cnt_data, icon_name='fas fa-cloud', palette='colorbrewer.diverging.Spectral_11',
                              background_color='black', gradient='horizontal', output_name="static/image/Wordcloud.jpg", font_path='./Lib/font/NanumSquareRoundB.ttf')

    return  dict_cnt_data


def get_local_data(driver):
    local_list = []
    # �������� 10�� title�� ������
    for i in range(10):
        tid = 'bbs_tr_{0}_bbs_title'.format(i)
        # Title ������ �� ���� �̸��� ����
        # ������ ���������� title�� 10���� �ȵɰ�찡 �־� Except ó�� �߰�.
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
        # ���� ������ ��ư Ŭ��
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


    # �˻� ���� Clear(default �� ����)
    # �˻� ���� �Է�
    driver.find_element_by_xpath('//*[@id="search_start"]').clear()
    driver.find_element_by_xpath('//*[@id="search_end"]').clear()
    driver.find_element_by_xpath('//*[@id="search_start"]').send_keys(sDate)
    driver.find_element_by_xpath('//*[@id="search_end"]').send_keys(eDate)

    # �˻� ��ư Ŭ���Ͽ� ����, �������� �ε� �ð��� ���� sleep ����
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
