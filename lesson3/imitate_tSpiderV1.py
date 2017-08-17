import os
import time
import urllib2
import urlparse
from bs4 import BeautifulSoup

def download(url, retry=2):
    print "downloading:", url
    header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'
    }
    try:
        request = urllib2.Request(url, headers=header)
        html = urllib2.urlopen(request).read()
    except urllib2.URLError as e:
        print "download error: ", e.reason
        html = None
        if retry > 0:
            if hasattr(e,'code') and 500 <= e.code <= 600:
                print e.code
                return download(url, retry - 1)
    time.sleep(1)
    return html

def crawled_links(url_seed,url_root):
    crawled_url = set()
    i = 1
    flag = True
    while flag:
        url = url_seed % i
        i += 1
        html = download(url)
        if html == None:
            break
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all('a',{'class':'title'})
        if links.__len__() == 0:
            flag = False
        for link in links:
            link = link.get('href')
            if link not in crawled_url:
                realUrl = urlparse.urljoin(url_root,link)
                crawled_url.add(realUrl)
            else:
                print 'end %d page'%(i)
                flag = False

    paper_num = crawled_url.__len__()
    print 'total paper num: ', paper_num
    return crawled_url


def crawled_page(crawled_url):
    for link in crawled_url:
        html = download(link)
        soup = BeautifulSoup(html, "html.parser")
        title = soup.find('h1', {'class': 'title'}).text
        content = soup.find('div', {'class': 'show-content'}).text
        title = title.replace('\x08', ' ')
        title = title.replace(r'<', '_')
        title = title.replace(r'>', '_')
        title = title.replace(r':', '_')
        title = title.replace(r'|', '_')
        title = title.replace(r'?', '_')
        title = title.replace(r'*', '_')       
        title = title.replace(r'/', '_')
        title = title.replace(r'"', '_')

        if os.path.exists('spider_res/') == False:
            os.mkdir('spider_res')

        file_name = 'spider_res/' + title + '.txt'


        if os.path.exists(file_name):
            continue
        file = open(file_name,'wb')
        content = unicode(content).encode('utf-8',errors = 'ignore')
        file.write(content)
        file.close()

url_root = 'http://www.jianshu.com'
url_seed = 'http://www.jianshu.com/c/9b4685b6357c?page=%d'
crawled_url = crawled_links(url_seed,url_root)
crawled_page(crawled_url)