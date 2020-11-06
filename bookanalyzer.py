from bs4 import BeautifulSoup
from urllib import request
import random
import re
import jieba
import pandas
import numpy
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['figure.figsize']=(10.0,5.0)
from wordcloud import WordCloud
import time

# 返回一个随机的请求头 headers
def getheaders():
    user_agent_list = [ \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1" \
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6", \
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1", \
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5", \
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3", \
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24", \
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]
    UserAgent = random.choice(user_agent_list)
    headers = {'User-Agent': UserAgent}
    return headers

#获取页面html相关内容
def get_html(url):
    headers = getheaders()
    req = request.Request(url, data=None, headers=headers)
    response = request.urlopen(req)
    html = str(response.read(), 'utf-8')
    # html=request.urlopen(url)
    soup=BeautifulSoup(html,"html.parser")
    content=soup.find("div",id="content")
    return content

#获取评论
def get_all(content):
    content=content.find_all("li", class_="subject-item")
    comments=''
    for data in content:
        try:
            comment=data.find("p",class_="comment").get_text()
        except:
            comment=''
        comments=comments+comment
    return comments

# #获取页数
# def get_page(url):
#     headers = getheaders()
#     req = request.Request(url, data=None, headers=headers)
#     response = request.urlopen(req)
#     html = str(response.read(), 'utf-8')
#     # html=request.urlopen(url)
#     soup=BeautifulSoup(html,"html.parser")
#     page=soup.find("span",class_="thispage").get("data-total-page")
#     return int(page)




# username = input("Please enter username(e.g.\'ahbei\'):")
# url='https://book.douban.com/people/'+username+'/collect?start='#url中username部分填入用户名
# page=31#获取总页数
# print(page)
# for i in range(page):
#     print(str(i)+"/"+str(page))
#     url1=url+str((i-1)*15)
#     comment = get_all(get_html(url1))#爬取所有评论
#     with open('bookcomment.txt', 'a+') as f:
#         f.write(comment)
#     time.sleep(random.random() * 3)

with open('bookcomment.txt', 'r') as f:
    all_comment = f.read();


#使用正则表达式过滤除汉字外的其他字符
pattern=re.compile(r'[\u4e00-\u9fff]+')
filtered=re.findall(pattern,all_comment)
cleaned="".join(filtered)
# print(cleaned)

#使用jieba分词
segment=jieba.lcut(cleaned)
words=pandas.DataFrame({'segment':segment})
# print(words.head())

#过滤无意义停用词
stopwords=pandas.read_csv("stopwords.txt",index_col=False,quoting=3,sep="\t",names=['stopword'],encoding='utf-8')
words=words[~words.segment.isin(stopwords.stopword)]
# print(words.head())
#
#使用numpy统计词频
stat=words.groupby('segment')['segment'].agg([('Count',numpy.size)])
stat=stat.reset_index().sort_values(by=["Count"],ascending=False)
# print(stat.head(100))
#
# #使用wordcloud可视化显示
cloud=WordCloud(font_path="simhei.ttf",background_color="white",max_font_size=60)
word_freq={x[0]:x[1] for x in stat.head(1000).values}
cloud=cloud.fit_words(word_freq)
plt.figure(dpi=300)
plt.imshow(cloud)
# plt.show()
plt.savefig('bookcloud.png')
