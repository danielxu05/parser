import Queue
import urllib2

import os.path
import time

import exifread


def build_wordlist(wordlist_file):
    # read in the word list
    fd = open(wordlist_file, "rb")
    raw_words = fd.readlines()
    fd.close()

    resume = None
    found_resume = False
    words = Queue.Queue()

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


def download(url):
    file_name = url.split('/')[-1]
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8) * (len(status) + 1)
        print status,
    f.close()
    pass

def write_into_file(nfile,way,content):
    f = open(nfile, way)
    f.write(content)
    f.close()
    pass

#download("https://idge.staticworld.net/ifw/IFW_logo_social_300x300.png")

file = "test.jpg"
w_nfile = "https://idge.staticworld.net/ifw/IFW_logo_social_300x300.png"
print('File         :', file)
print('Access time  :', time.ctime(os.path.getatime(file)))
print('Modified time:', time.ctime(os.path.getmtime(file)))
print('Change time  :', time.ctime(os.path.getctime(file)))
print('Size         :', os.path.getsize(file))


f = open(file, 'rb')
a = f.read()
write_into_file("byteresult.txt","w",a)
tags = exifread.process_file(f,details=False)

print(tags)
for x,y in tags:
    print(x)
    print(y)
