# coding=UTF-8

import time
import urllib2
import random
import re
import sys
import traceback
import os
import base64


RANDOM_PLAYER_URL = ""
DIRECT_FILE_URL = ""
SAVE_TO_DIRECTORY = "maple-bgm"
ERROR_LOG = "fail_log.txt"


def query_data(request_url):
    remote_file = urllib2.urlopen(request_url)
    data = remote_file.read()
    remote_file.close()
    return data


def extract_name(raw_data):
    pattern = re.compile("現正播放：.*\",")
    song_name = pattern.findall(raw_data)[0].replace("現正播放：", "").replace("\",", "")
    song_name = file_name_filter(song_name)
    return song_name


def file_name_filter(name_string):
    name_string = name_string.replace("/", "／").replace("\\", "")
    name_string = name_string.replace(">", "＞").replace("<", "＜")
    name_string = name_string.replace(":", "：").replace("?", "？")
    name_string = name_string.replace("*", "＊").replace("\"", "＂")
    return name_string


def extract_base64_audio(raw_data):
    pattern = re.compile("mpeg;base64,.*\" type=\"audio")
    audio_content = pattern.findall(raw_data)[0].replace("mpeg;base64,", "").replace("\" type=\"audio", "")
    audio_content = base64.b64decode(audio_content)
    return audio_content


def extract_file_address(raw_data):
    pattern = re.compile("<source src=\".*\" type=\"audio")
    audio_content = pattern.findall(raw_data)[0].replace("<source src=\"", "").replace("\" type=\"audio", "")
    audio_content = audio_content.replace(" ", "%20")
    return audio_content


"""
def generate_random_string(size=16, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))
"""


def is_base64(data):
    pattern = re.compile("mpeg;base64,.*\" type=\"audio")
    findings = pattern.findall(data)
    return len(findings) > 0


def save_audio(audio_name, audio_content, directory):
    audio_name = audio_name.decode("utf-8")
    audio_file = open(os.path.join(directory, audio_name) + ".mp3", "wb")
    audio_file.write(audio_content)
    audio_file.close()


def main():
    # check directory
    if not os.path.exists(SAVE_TO_DIRECTORY):
        os.makedirs(SAVE_TO_DIRECTORY)

    while True:
        # query random raw data
        try:
            raw_data = query_data(RANDOM_PLAYER_URL)
        except:
            # failed to retrieve data, wait a bit then try again
            # traceback.print_exc(file=sys.stdout)
            print "Failed to open URL, reconnecting..."
            time.sleep(210)
            continue

        # get audio name
        # TODO handle duplicate file name
        audio_name = extract_name(raw_data)

        # handle base64
        if is_base64(raw_data):
            # get audio and save to local
            audio_content = extract_base64_audio(raw_data)
            save_audio(audio_name, audio_content, SAVE_TO_DIRECTORY)
            print "Download", audio_name, "complete."

        # handle direct file
        else:
            audio_address = extract_file_address(raw_data)
            try:
                # get audio and save to local
                audio_content = query_data(DIRECT_FILE_URL + audio_address)
                save_audio(audio_name, audio_content, SAVE_TO_DIRECTORY)
                print "Download", audio_name, "complete."
            except:
                # failed to get audio file, record in log
                # traceback.print_exc(file=sys.stdout)
                error_log = open(ERROR_LOG, "a")
                error_log.write("Failed to download " + audio_name + " from " + DIRECT_FILE_URL + audio_address)
                error_log.write("\n")
                error_log.close()

        # randomly sleep a few seconds
        time.sleep(random.uniform(13, 35))


if __name__ == "__main__":
    main()
