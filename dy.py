from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import requests
import pymysql

# 搜索 URL 和头部信息
search_url = 'https://www.douyin.com/search/雪允?publish_time=0&sort_type=2&type=general'
headers = {
    "cookie": '',
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
}
NumOfVideos = 20

# 设置 Chrome 选项
option = webdriver.ChromeOptions()
option.add_argument('--disable-blink-features=AutomationControlled')
option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=option)
driver.get(search_url)
sleep(3)

# 数据库配置
config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '112212',
    'database': 'douyin_data',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}

# 连接数据库
connection = pymysql.connect(**config)

try:
    with connection.cursor() as cursor:

        # 遍历视频并收集数据
        for i in range(NumOfVideos):
            js = 'document.getElementsByClassName("MgWTwktU")[' + str(i) + '].scrollIntoView()'
            driver.execute_script(js)
            sleep(3)
            card = driver.find_elements(By.CLASS_NAME, 'MgWTwktU')[i]
            video_container = card.find_element(By.TAG_NAME, 'xg-video-container')
            video_url = video_container.find_elements(By.TAG_NAME, 'source')[0].get_attribute('src')
            print(video_url)
            video_response = requests.get(video_url, headers=headers, timeout=5)

            with open('./videos/'+str(i)+'.mp4', mode='wb') as f:
                f.write(video_response.content)

            hidden_image_divs = card.find_elements(By.CLASS_NAME, 'display-none')
            for hidden_image in (hidden_image_divs[:NumOfVideos]):
                img_element = hidden_image.find_element(By.TAG_NAME, 'img')
                img_url = img_element.get_attribute('src')
                img_alt = img_element.get_attribute('alt')  # 获取图片标题
                print(img_alt)

                # 插入数据到数据库
                cursor.execute("INSERT INTO videos (title, url) VALUES (%s, %s)", (img_alt, img_url))

        # 提交事务
                connection.commit()

finally:
    driver.quit()
    connection.close()
