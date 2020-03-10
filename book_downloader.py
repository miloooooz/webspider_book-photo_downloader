import requests
import re
from bs4 import BeautifulSoup
import sys

# Tutorial: https://zhuanlan.zhihu.com/p/29809609
# Basic tutorial about module requests and bs4: https://www.cnblogs.com/silence-cho/p/9786069.html

# If simply GET, when accessing Mandarin-based website, there will be bunch of messy codes because of encoding
# difference, Python uses UTF-8, while many other websites may use different encoding.
# r.text() has the result of decoding for the default encoding ISO-8859-1 when Content-Type is unclear
# https://blog.csdn.net/feixuedongji/article/details/82984583?depth_1-utm_source=distribute.pc_relevant.none-task&utm_source=distribute.pc_relevant.none-task
# https://blog.csdn.net/qq_38318303/article/details/80104499?depth_1-utm_source=distribute.pc_relevant.none-task&utm_source=distribute.pc_relevant.none-task

server_page = "http://www.biqukan.com/"
category_page = 'http://www.biqukan.com/1_1094/'

class DownloadBooks():
    def __init__(self, server_page= server_page, category_page= category_page):
        self.server_page = server_page
        self.category_page = category_page
        self.category_names = []
        self.urls = []
        self.category_nb = 0

    def download_content(self, target):
        target_page = requests.get(url=target)
        # Update: I found that if I use target_page.encoding first, I'll get the encoding type of the text so that I could
        # decode it with its original encoding and then decode back into UTF-8

        # here we don't use 'req_t.text' since the text is decoded using default endoing methods,
        # and the requested URL doesn't use default encoding
        # https://blog.csdn.net/qq_38900441/article/details/79946377
        # content = self.encoding_unify(target_page)
        content = target_page.content
        content_bs = BeautifulSoup(content, "lxml")
        content_only = content_bs.find_all('div', class_= 'showtxt') #this returns 'bs4.element.ResultSet'
        # https://blog.csdn.net/thewindkee/article/details/79890207
        # \xa0 means non-breaking space
        downloaded_texts = content_only[0].text.replace('\xa0', '')  # replace non-breaking space with empty string
        return downloaded_texts

    def download_url_pages(self):
        get_urls = requests.get(url=self.category_page)
        # categories = self.encoding_unify(get_urls)
        categories = get_urls.content
        # print(get_urls.encoding)      can directly get the encoding of the webpage by this command
        bs = BeautifulSoup(categories, "lxml")
        category_all = bs.find_all('div', class_='listmain') # to look for the categories within the whole page
        category_bs = BeautifulSoup(str(category_all[0]), "lxml")
        category_lists = category_bs.find_all('a')      # return 'bs4.element.ResultSet'
        # Since there are some URLs containing non-category pages such as introductions or homepages
        # we need to ignore them
        for i in range(len(category_lists)):     # the 'each' element is with 'Tag' type
            if re.match('章节目录', str(category_lists[i].string)):
                # print(str(category_lists[i]))        returns '<a href="/1_1094/5386268.html">章节目录</a>'
                category_lists = category_lists[i+1:]
                break
        for each in category_lists:
            if re.match('^第[\d\w]*章', str(each.string)): # re tutorial: https://blog.csdn.net/whycadi/article/details/2011046?depth_1-utm_source=distribute.pc_relevant.none-task&utm_source=distribute.pc_relevant.none-task
                self.category_names.append(each.string)
                self.urls.append(self.server_page + each.get('href'))
        self.category_nb = len(self.category_names)

    def write(self, name, path, url):
        with open(path, 'a', encoding = 'utf-8') as f:
            f.write(name + '\n\n')
            f.write(self.download_content(url))
            f.write('\n\n')


if __name__ == '__main__':
    try:
        server_page = sys.argv[1]
        category_page = sys.argv[2]
        book_name = sys.argv[3]
        a = DownloadBooks(server_page, category_page)
    except IndexError:
        a = DownloadBooks()
        book_name = "book.txt"
    a.download_url_pages()
    a.download_content(a.urls[1])
    # print('Start downloading the book.')
    for i in range(a.category_nb):
        a.write(a.category_names[i], book_name, a.urls[i])
        sys.stdout.write(f"Downloading: {i / a.category_nb:.2f}%" + '\r')
        sys.stdout.flush()
    print('The book is downloaded.')




    # def encoding_unify(self, r):
    #     if r.status_code == 200:
    #         # Solve the problem of messy code
    #         if r.encoding == 'ISO-8859-1':
    #             if not requests.utils.get_encodings_from_content(r.text):
    #                 encoding = r.apparent_encoding
    #             else:
    #                 encoding = requests.utils.get_encodings_from_content(r.text)[0]
    #
    #             if re.match('^utf-8', encoding.lower()):
    #                 content = r.text.encode('ISO-8859-1').decode('utf-8', 'ignore')

    #                 # since the website doesn't declare its encoding, Python decoded the text using 'ISO-8859-1',
    #                 # so here we need to encode it back with 'ISO-8859-1' and decode it with its real encoding
    #
    #             elif re.match('^utf-16', encoding.lower()):
    #                 content = r.text.encode('ISO-8859-1').decode('utf-16', 'ignore')
    #             elif encoding.lower() == 'gb2312':
    #                 content = r.text.encode('ISO-8859-1').decode('gb2312', 'ignore')
    #             elif encoding.lower() == 'gbk':
    #                 content = r.text.encode('ISO-8859-1').decode('gbk', 'ignore')
    #             else:
    #                 pass
    #     return content
