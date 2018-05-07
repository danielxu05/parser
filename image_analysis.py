import Queue
import os.path
import urllib2
from operator import attrgetter

import reverse_geocode
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


class picture_info(object):
    #class object for picture information
    def __init__(self,name,time,num_gps,city):
        self.name = name
        self.time = time
        self.gps = num_gps
        self.city = city

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
    #download the image through link
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
    #write into a file
    f = open(nfile, way)
    f.write(content)
    f.close()
    pass

def _convert_to_degress(value):
    #transfer the GEOlocation into longtitude and latitude
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)


def get_exif_data(image):
    #get exif data from the image
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]

                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value
    return exif_data


def get_lat_lon(exif_data):
    #Get the latitude and longitiude
    lat = None
    lon = None

    gps_info = exif_data["GPSInfo"]

    gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
    gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
    gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
    gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = _convert_to_degress(gps_latitude)
        if gps_latitude_ref != "N":
            lat = 0 - lat

        lon = _convert_to_degress(gps_longitude)
        if gps_longitude_ref != "E":
            lon = 0 - lon

    return lat, lon


def _get_if_exist(data, key):
    #check whether there is data type in that image
    if key in data:
        return data[key]
    return None


def write_into_file(nfile,way,content):
    #write into a file
    f = open(nfile, way)
    f.write(content)
    f.close()

def main():
    filelist = list()
    for filename in os.listdir("pictures"):
        try:
            im = Image.open("pictures/"+filename)
            imifd = get_exif_data(im)
            print(filename)
            print(imifd['DateTimeDigitized'])
            gpsdata = ""
            city = ""
            try:
                gpsdata = get_lat_lon(imifd)
                print gpsdata
                city = reverse_geocode.get(gpsdata)
                print(city)
            except(KeyError):
                print('No GPS data avaiable')
            print("--------------->>>>>>>>>>>>>>>>>>>>>")
            temp = picture_info(filename,imifd['DateTimeDigitized'],gpsdata,city)
            filelist.append(temp)
        except:(IOError)
    filelist.sort(key=attrgetter('time'))
    for x in filelist:
        temp = x.name + "  " + " " + x.time + " " + " " + str(x.city) + " " + str(x.gps)
        print(temp)
        write_into_file("result.txt",'a',temp+'\n')


print("-------------------------------------------------------")

main()

