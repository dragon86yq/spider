#### 第四次作业

#### 作业：
1. 爬取大数据专题所有文章列表，并输出到文本中保存。
2. 每篇文章需要爬取的数据：作者、标题、文章地址、摘要、缩略图地址、阅读数、平均数、点赞数、打赏数。

#### 第一个作业爬取大数据专题所有文章列表
- 思路：
    1. 爬取大数据专题页面的所有链接。可以直接从大数据专题界面爬取，不需要进入每篇文章获取链接
    2. 获取大数据专题页面每篇文章的链接后，爬取对应链接中感兴趣的内容：标题、内容

- 代码：
设置作业一和作业二共同使用的参数:
```
import os
import time
import urllib2
import urlparse
from bs4 import BeautifulSoup
url_root = 'http://www.jianshu.com'
url_seed = 'http://www.jianshu.com/c/9b4685b6357c?page=%d'
```


下载页面的内容，使用download函数
```
def download(url, retry=2):
    """
    下载页面的函数，会下载完整的页面信息
    :param url: 要下载的url
    :param retry: 重试次数
    :return: 原生html
    """
    print "downloading", url
    # 设置header信息，模拟浏览器请求
    header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'
    }
    try: #爬取可能会失败，采用try-except方式来捕获处理
        request = urllib2.Request(url, headers=header)  #设置请求数据
        html = urllib2.urlopen(request).read()  #抓取url
    except urllib2.URLError as e:  #异常处理
        print "download error:", e.reason
        html = None
        if retry > 0:  #未超过重试次数，可以继续爬取
            if hasattr(e,'code') and 500 <= e.code <= 600:  #错误码范围，是请求出错才继续重试爬取
                print e.code
                return download(url, retry-1)
    time.sleep(0.2)  #等待0.2s，避免对服务器造成压力，也避免被服务器屏蔽爬取
    return html
```

爬取大数据专题的所有文章链接，使用crawled_links函数
```
def crawled_links(url_seed,url_root):
    """
    抓取文章链接
    :param url_seed: 下载的种子页面地址
    :param url_root: 爬取网站的根目录
    :return: 需要爬取的页面
    """
    crawled_url = set()  #设置无序集合 ,需要爬取的页面
    i = 1
    flag = True  #标记是否需要继续爬取
    while flag:
        url = url_seed % i #真正爬取的页面
        i += 1  #下一次需要爬取的页面
        html = download(url)  #下载页面
        if html == None:  #下载页面为空，表示已爬取到最后
            break
        soup = BeautifulSoup(html, "html.parser")  #格式化爬取的页面数据
        links = soup.find_all('a', {'class' : 'title'}) #获取标题元素
        if links.__len__() == 0:  #爬取的页面中已无有效数据，终止爬取
            flag = False
        for link in links:  #获取有效的文章地址
            link = link.get('href')
            if link not in crawled_url:
                realUrl = urlparse.urljoin(url_root, link)
                crawled_url.add(realUrl)  # 记录未重复的需要爬取的页面
            else:
                print 'end % page' %(i)
                flag = False
    paper_num = crawled_url.__len__()
    print 'total paper num:', paper_num
    return crawled_url
```

爬取每篇文章的内容，并将内容存入txt，使用crawled_page函数
```
def crawled_page(crawled_url):
    """
    爬取文章内容
    :param crawled_url: 需要爬取的页面地址集合
    """
    for link in crawled_url: #按地址逐篇文章爬取
        html = download(link)
        soup = BeautifulSoup(html, "html.parser")
        title = soup.find('h1', {'class': 'title'}).text #获取文章标题
        content = soup.find('div', {'class': 'show-content'}).text #获取文章内容     
        title = title.replace('\x08', '_') #将标题中特殊符号转换为'_'  
        title = title.replace(r'<', '_')
        title = title.replace(r'>', '_')
        title = title.replace(r':', '_')
        title = title.replace(r'|', '_')
        title = title.replace(r'?', '_')
        title = title.replace(r'*', '_')       
        title = title.replace(r'/', '_')
        title = title.replace(r'"', '_')
        if os.path.exists('spider_res/') == False:   #检查保存文件的地址
            os.mkdir('spider_res')
        file_name = 'spider_res/' + title + '.txt'   #设置要保存的文件名
        if os.path.exists(file_name):
            continue
        file = open(file_name,'wb')  #写文件
        content = unicode(content).encode('utf-8',errors = 'ignore')
        file.write(content)
        file.close()
```

执行函数
```
crawled_links = crawled_links(url_seed,url_root)
crawled_page(crawled_links)
```

####  第二个作业爬取大数据专题所有文章详情
- 思路：
    1. 获取大数据专题第一页的每篇文章信息：作者、标题、文章地址、摘要、缩略图地址、阅读数、平均数、点赞数。
    2. 通过循环函数获取大数据专题每页中的文章信息：作者、标题、文章地址、摘要、缩略图地址、阅读数、平均数、点赞数。
- 代码：

爬取大数据专题第一页中的文章列表，使用crawl_list函数
```
def crawl_list(url):
    """
    爬取对应链接的内容，
    return：爬取的文章列表
    """
    html = download(url)
    if html == None:
        return
    soup = BeautifulSoup(html, "html.parser")
    return soup.find(id = 'list-container').find('ul', {'class' : 'note-list'})
```

爬取每篇文章的作者、标题、文章地址、摘要、缩略图地址、阅读数、平均数、点赞数。使用函数crawl_paper_tag
```
def crawl_paper_tag(list, url_root):
    """
    获取文章列表详情
    """
    paperlist = []
    lists = list.find_all('li')
    for paperTag in lists:
        author = paperTag.find('div', {'class' : 'content'}).find('div', {'class' : 'author'}).text
        title = paperTag.find('div', {'class' : 'content'}).find('a', {'class' : 'title'}).text
        paperUrl = paperTag.find('div', {'class' : 'content'}).find('a', {'class' : 'title'}).get('href')
        abstract = paperTag.find('div', {'class' : 'content'}).find('p', {'class' : 'abstract'}).text
        pic = paperTag.find('a', {'class' : 'wrap-img'})
        metaRead = paperTag.find('div', {'class' : 'content'}).find('div', {'class' : 'meta'}).find('i',{'class':'iconfont ic-list-read'}).text
        metaComment = paperTag.find('div', {'class' : 'content'}).find('div', {'class' : 'meta'}).find('i',{'class':'iconfont ic-list-comments'}).text
        metaLike = paperTag.find('div', {'class' : 'content'}).find('div', {'class' : 'meta'}).find('i',{'class':'iconfont ic-list-like'}).text
        metaReward = ''
        paperAttr = {
        'author' : author,
        'title' : title,
        'url' : urlparse.urljoin(url_root, paperUrl),
        'abstract' : abstract,
        'pic' : pic,
        'read' : metaRead,
        'comment' : metaComment,
        'like' : metaLike,
        'reward' : metaReward
        }
        if os.path.exists('info/') == False:
            os.mkdir('info')
        title = deal_title(title)
        file_name = 'info/' + title + '.txt'          
        file = open(file_name, 'wb')
        content_tag = unicode(paperAttr).encode('utf-8',errors = 'ignore')
        file.write(content_tag)
        file.close()
        paperlist.append(paperAttr)
    return paperlist
```


使用'_'替换标题中特殊符号，使用函数deal_title
```
def deal_title(title):
    """
    文件命名中不能够特殊符号，转换标题中特殊符号
    """
    title = title.replace('\x08', '_')
    title = title.replace(r'<', '_')
    title = title.replace(r'>', '_')
    title = title.replace(r':', '_')
    title = title.replace(r'|', '_')
    title = title.replace(r'?', '_')
    title = title.replace(r'*', '_')       
    title = title.replace(r'/', '_')
    title = title.replace(r'"', '_')
    return title
```

去爬所有文章的作者、标题、文章地址、摘要、缩略图地址、阅读数、平均数、点赞数，使用函数crawl_all_paper_tag
```
def crawl_all_paper_tag(url_seed, url_root):
    """
    爬取所有文章的详细内容
    """
    i = 1
    flag = True
    all_tag_list = []
    while flag:
        url = url_seed % i
        i += 1
        crawl_content = crawl_list(url)
        all_tag_list = crawl_paper_tag(crawl_content, url_root)
        if all_tag_list.__len__() == 0:
            flag = False
            print 'the end'
```

执行函数
```
crawl_all_paper_tag(url_seed, url_root)
```
