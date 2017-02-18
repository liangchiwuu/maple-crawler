# coding=UTF-8

import time
import urllib2
import random
import re
import string


def query_data(request_url):
    # query data
    url = request_url
    remote_file = urllib2.urlopen(url)
    data = remote_file.read()
    remote_file.close()
    return data


def extract_name(raw_data):
    pattern = re.compile("現正播放：.*\",")
    song_name = pattern.findall(raw_data)[0].replace("現正播放：", "").replace("\",", "")
    return song_name


def save_to_txt(file_name, data):
    text_file = open(file_name + ".txt", "w")
    text_file.write(data)
    text_file.close()


def download_maple():
    while True:
        try:
            raw_data = query_data("https://maplebgm.tk/bgmplayer_rand.php")
        except:
            time.sleep(210)
            print "Failed to open URL, reconnecting..."
            continue
        song_name = extract_name(raw_data)
        print "Processing", song_name, "..."
        try:
            save_to_txt(song_name.decode('utf-8'), raw_data)
            print "Download", song_name, "complete."
        except:
            backup_name = generate_random_string()
            save_to_txt(backup_name, raw_data)
            print "Failed to parse file name, using default name."
            print "Download", backup_name, "complete."
        time.sleep(random.uniform(13, 35))


def generate_random_string(size=16, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


if __name__ == "__main__":
    download_maple()
