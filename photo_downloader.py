import requests
import threading
from bs4 import BeautifulSoup
from queue import Queue
import json
import sys
import os


# This is a dynamic webpage, with scrolling down more webpages are loaded. So it is different from the book_downloader
# stuff which is a simple html webpage.
# There are two ways to solve the problem:
# 1. By checking the Chrome Developer Tool, I found that the Headers and Previews of several pages.
# We can find that the content-type in response header is json, so here we will use JSON as the data type
# I found the Request URL for each page. By viewing the 'urls' tag under those pages, I found its corresponding photo-downloading links.
# 2. Use selenium to mimic the action of browser. Since the application problem, we may use this method later.

# Github source: https://github.com/librauee/Reptile/tree/master/unsplash
# https://zhuanlan.zhihu.com/p/31127896
# https://zhuanlan.zhihu.com/p/39896085
# Thanks to the tutorial, I decided to use threads to improve the speed

# Threading tutorial for webspider: https://blog.csdn.net/qq_36063562/article/details/92834143
#                                   https://www.cnblogs.com/chen0307/p/9956331.html
#                                   https://cuiqingcai.com/3325.html
THREAD_NB = 3

class DownloadPhotos(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.thread_end = 0
        self.thread_id = thread_id
        self.header = {'referer': 'https://unsplash.com/',
                       'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
                       'authority': 'unsplash.com'}

    def run(self):      # similar to the main function, after the DownloadPhotos().start(), this function will be run
        while not url_queue.empty():
            self.direct_request_json()


    def direct_request_json(self):
        # This function is to get the JSON data of the pictures
        self.target = url_queue.get()
        req = requests.get(self.target[0], headers=self.header)
        print(f'{threading.current_thread().getName()} is requesting Page {self.target[1]} URLs of pictures, the status code is {req.status_code}.')
        self.direct_request_images(req.text)

    def direct_request_images(self, pic_json):
        # By checking the json file, I found that it returns a single list returning dicts containing the information
        # of all pictures within that json file.
        # we found the key 'urls' for each photo, and there are several categories of the urls
        # 'raw', 'full', 'regular', 'small' and 'thumb', the sizes of pictures are decreasing relatively
        # To save time, we download the smallest pictures which are under key 'thumb'
        pics = json.loads(pic_json)     # A list containing 12 or 24 dicts for 12 or 24 photos
        if not os.path.exists('Downloaded_imgs'):
            os.mkdir('Downloaded_imgs')
        i = 1
        for pic in pics:
            thumb_url = pic['urls']['thumb']
            picture = requests.get(thumb_url, headers=self.header)      # Here the return type is 'Response' So we need to make it into bytes
            with open('./Downloaded_imgs/page'+str(self.target[1])+'_'+str(i)+'.png', 'wb') as f:
                f.write(picture.content)
            print(f'Saving photo: page{self.target[1]}_{str(i)}')
            i += 1

def direct_request_urls(url_queue, max_page):
    target = 'https://unsplash.com/'
    first_page_target = 'https://unsplash.com/napi/photos?page=1&per_page=24'
    for i in range(1, max_page+1):
        if i == 1:
            get_page = first_page_target
        else:
            get_page = f"https://unsplash.com/napi/photos?page={i}&per_page=12"
        url_queue.put([get_page, i])


if __name__ == "__main__":
    url_queue = Queue()     # use queue in order to make sure no repetition download
    threads = []
    if len(sys.argv) == 2:
        max_page = sys.argv[1]
        direct_request_urls(url_queue, int(max_page))
    else:
        direct_request_urls(url_queue, 3)
    for i in range(THREAD_NB):
        d = DownloadPhotos(i)
        d.start()
        threads.append(d)
    for t in threads:
        t.join()
    print('Exit thread.')