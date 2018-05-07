import threading
import urllib
from HTMLParser import HTMLParser

import requests
from bs4 import BeautifulSoup

import sys
from sets import Set

reload(sys)
sys.setdefaultencoding('utf8')
# general settings
user_thread = 1


# target specific settings
# target_url    = "http://appledoreresearch.com/wp-login.php"
# target_post   = "http://appledoreresearch.com/wp-login.php"

class Dictlist(dict):
    def __setitem__(self, key, value):
        try:
            self[key]
        except KeyError:
            super(Dictlist, self).__setitem__(key, [])
        self[key].append(value)

class BruteParser(HTMLParser):
    #burterparser object
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_results = Dictlist()

    def handle_starttag(self, tag, attrs):
        wantedtag = ["src","href","a","p","video"]
        for name, value in attrs:
            if name and value is not None:
                if name == "script":
                    print name ,"-------------->>>>  ",value
                if name in wantedtag:
                    self.tag_results[name] = value



class Bruter(object):
    def __init__(self, url):

        self.url = url
        print "Finished setting up for: %s" % url

    def run_bruteforce(self):
        for i in range(user_thread):
            t = threading.Thread(target=self.web_bruter)
            t.start()

    def get_home_url(self):
        count = 0
        for x in self.url[8:]:
            if x == '/':
                break
            count = count + 1
        home_url = self.url[:count+8]
        return home_url

    def write_into_file(self,nfile,way,content):
        f = open(nfile, way)
        f.write(content)
        f.close()

    def link_operation(self,pos_tags,tag):
        #get image
        pictag = [".gif", ".jpg", ".jpeg", ".tif"]
        set = Set()
        for x in pos_tags[tag]:
            temp = self.links_operation(x)
            set.add(temp)
        ii = 0
        for y in list(set):
            for z in pictag:
                if z in y:
                    self.write_into_file('pic_links.txt', 'a', y+'\n')
                    urllib.urlretrieve(y,'pictures/'+str(ii)+'.jpg')
                    ii = ii + 1
                    print(y)
                else:
                    if temp not in set:
                        self.write_into_file('links.txt','a',y+'\n')
                        set.add(temp)




    def links_operation(self,url):
        #make valid links
        if (url[:4] == "http"):
            return url
        else:
            return self.url+url

    def web_bruter(self):
        #get connection and parse the HTML code to classify different type of code
        resp = requests.get(self.url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        content = ""
        for i in soup.findAll("p"):
            temp = i.text
            content = content + temp + '\n'
        self.write_into_file('content.txt','w',content)

        page = resp.content
        #print(page1)

        parser = BruteParser()
        parser.feed(page)
        post_tags = parser.tag_results

        for x,y in post_tags.iteritems():
            print x,"   ", str(len(y))

        print(post_tags)
        self.link_operation(post_tags,'href')
        self.link_operation(post_tags,'src')

    def download_pictures(self,set,dir):
        #download picture
        ii = 0
        for i in set:
            urllib.urlretrieve(i,ii+".jpg")


target_url = "http://localhost:90/Flatty/"
#target_url = "http://testphp.vulnweb.com/"
#target_url = "http://127.0.0.1/html/login/login.php"
bruter_obj = Bruter(target_url)
bruter_obj.run_bruteforce()







