import urllib2 
import urllib
import threading
import Queue

threads        = 1
target_url     = "http://www.drew.edu"
wordlist_file  = "all.txt" # from SVNDigger
resume         = None
user_agent     = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"

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


def dir_bruter(word_queue):
    
    while not word_queue.empty():
        attempt = word_queue.get()
        
        attempt_list = []
        
        # check if there is a file extension if not
        # it's a directory path we're bruting
        if "." not in attempt:
            attempt_list.append("/%s/" % attempt)
        else:
            attempt_list.append("/%s" % attempt)

                
        # iterate over our list of attempts
        success = 0
        unsuccess = 0
        for brute in attempt_list:
            
            url = "%s%s" % (target_url,urllib.quote(brute))
            try:
                headers = {}
                headers["User-Agent"] = "Googlebot"
                #print(url)
                r = urllib2.Request(url,headers=headers)
                #print(r.data)
                response = urllib2.urlopen(r)
                #print(len(response.read()))
                if len(response.read()) :
                    print "[%d] => %s" % (response.code,url)
                    success += 1
            except urllib2.HTTPError,e:

                if e.code != 404:
                    print "!!! %d => %s" % (e.code,url)
                    unsuccess += 1
                pass
    print "success links: %d" % (success)
    print "unsuccess links: %d" % (success)




word_queue = build_wordlist(wordlist_file)

print("-----------------------------------------------------")
for i in range(threads):
            t = threading.Thread(target=dir_bruter,args=(word_queue,))
            t.start()

