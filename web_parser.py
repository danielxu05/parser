import threading
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

    #def handle_data(self, data):
        #print(data)


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
        pictag = [".png", ".gif", ".jpg", ".jpeg", ".tif"]
        set = Set()
        for x in pos_tags[tag]:
            temp = self.links_operation(x)
            for z in pictag:
                if z in x:
                    self.write_into_file('pic_links.txt', 'a', temp+'\n')
                else:
                    if temp not in set:
                        self.write_into_file('links.txt','a',temp+'\n')
                        set.add(temp)


    def links_operation(self,url):
        if (url[:4] == "http"):
            return url
        else:
            return self.get_home_url()+url

    def web_bruter(self):
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

        self.link_operation(post_tags,'href')
        self.link_operation(post_tags,'src')


target_url = "https://www.facebook.com/josh.ryan.731/photos?lst=100008955589475%3A100002884971023%3A1523412190&source_ref=pb_friends_tl"
#target_url = "http://testphp.vulnweb.com/"
#target_url = "http://127.0.0.1/html/login/login.php"
bruter_obj = Bruter(target_url)
bruter_obj.run_bruteforce()
print(bruter_obj.get_home_url())






