from bs4 import BeautifulSoup
from urllib import request
import re
import jieba
import pandas
import numpy
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['figure.figsize']=(10.0,5.0)
from wordcloud import WordCloud

#获取页面html相关内容
def get_html(url):
    html=request.urlopen(url)
    soup=BeautifulSoup(html,"html.parser")
    content=soup.find("div",id="content")
    return content

#获取评论
def get_all(content):
    content=content.find_all("div", class_="item")
    comments=''
    for data in content:
        try:
            comment=data.find("span",class_="comment").get_text()
        except:
            comment=''
        comments=comments+comment
    return comments

#获取页数
def get_page(url):
    html=request.urlopen(url)
    soup=BeautifulSoup(html,"html.parser")
    page=soup.find("span",class_="thispage").get("data-total-page")
    return int(page)


username = input("Please enter username(e.g.\'ahbei\'):")
url='https://movie.douban.com/people/'+username+'/collect?start='#url中username部分填入用户名
page=get_page(url)#获取总页数
#print(page)
all_comment=''
for i in range(page):
    url1=url+str((i-1)*15)
    all_comment+=get_all(get_html(url1))#爬取所有评论
    #print(all_comment)
#print(all_comment)

#使用正则表达式过滤除汉字外的其他字符
pattern=re.compile(r'[\u4e00-\u9fff]+')
filtered=re.findall(pattern,all_comment)
cleaned="".join(filtered)
#print(cleaned)

#使用jieba分词
segment=jieba.lcut(cleaned)
words=pandas.DataFrame({'segment':segment})
#print(words.head())

#过滤无意义停用词
stopwords=pandas.read_csv("stopwords.txt",index_col=False,quoting=3,sep="\t",names=['stopword'],encoding='utf-8')
words=words[~words.segment.isin(stopwords.stopword)]
#print(words.head())

#使用numpy统计词频
stat=words.groupby(by=['segment'])['segment'].agg({"Count":numpy.size})
stat=stat.reset_index().sort_values(by=["Count"],ascending=False)
print(stat.head(100))

#使用wordcloud可视化显示
cloud=WordCloud(font_path="simhei.ttf",background_color="white",max_font_size=60)
word_freq={x[0]:x[1] for x in stat.head(1000).values}
cloud=cloud.fit_words(word_freq)
plt.imshow(cloud)
plt.show()
