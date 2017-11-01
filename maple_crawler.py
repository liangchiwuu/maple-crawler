# coding=UTF-8

import base64
import logging
import os
import random
import re
import time
from logging.handlers import TimedRotatingFileHandler

import requests

from conf import settings

logger = logging.getLogger(__name__)


class MapleTunesParser:
    def __init__(self, source):
        self.__source = source

    def get_track_name(self):
        findings = re.findall('(?<=現正播放：)(.*)(?=\",)', self.__source)
        if len(findings) == 0:
            return None
        name = findings[0].replace('/', '／').replace('\\', '').replace('>', '＞').replace('<', '＜') \
            .replace(':', '：').replace('?', '？').replace('*', '＊').replace('\"', '＂')
        return name

    def get_base64_string(self):
        findings = re.findall('(?<=mpeg;base64,)(.*)(?=\" type=\"audio)', self.__source)
        if len(findings) == 0:
            return None
        base64_string = base64.b64decode(findings[0])
        return base64_string

    def get_file_address(self):
        findings = re.findall('(?<=<source src=\")(.*)(?=\" type=\"audio)', self.__source)
        if len(findings) == 0:
            return None
        file_address = findings[0].replace(' ', '%20')
        return file_address


def __setup_logger():
    log_format = '%(asctime)s %(levelname)s (%(name)s:%(lineno)d) %(message)s'
    date_format = '%Y-%m-%dT%H:%M:%SZ'
    log_dir = os.path.join(settings.PROJECT_DIR, settings.LOG_DIR)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # setup root logger
    logging.Formatter.converter = time.gmtime
    logging.getLogger().setLevel(logging.DEBUG)

    # setup file handler
    fh = TimedRotatingFileHandler(os.path.join(log_dir, 'maple.log'), when='midnight', utc=True)
    fh.setFormatter(logging.Formatter(fmt=log_format, datefmt=date_format))
    fh.setLevel(logging.INFO)
    logging.getLogger().addHandler(fh)

    # setup stream handler
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(fmt=log_format, datefmt=date_format))
    sh.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(sh)

    logger.info('Logger setup complete.')


def __save_mp3(directory, filename, content):
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = filename.decode('utf-8')
    with open('{}.mp3'.format(os.path.join(directory, filename)), 'wb') as of:
        of.write(content)


def __request(url):
    response = requests.get(url)
    return response.content


def main():
    __setup_logger()

    while True:
        try:
            source = __request(settings.MAPLETUNES_RANDOM_PLAYER)
        except requests.exceptions.RequestException:
            # failed to retrieve data, wait a bit then try again
            logger.error('Failed to visit player, retrying...')
            time.sleep(210)
            continue

        # TODO handle duplicate track
        parser = MapleTunesParser(source)

        track_name = parser.get_track_name()
        base64_string = parser.get_base64_string()
        file_address = parser.get_file_address()
        download_dir = os.path.join(settings.PROJECT_DIR, settings.DOWNLOAD_DIR)

        if base64_string is not None:

            __save_mp3(download_dir, track_name, base64_string)
            logger.info('Download base64 {} complete.'.format(track_name))

        elif file_address is not None:

            file_url = settings.MAPLETUNES_URL + file_address
            try:
                track_content = __request(file_url)
                __save_mp3(download_dir, track_name, track_content)
                logger.info('Download {} complete.'.format(track_name))
            except requests.exceptions.RequestException:
                logger.error('Failed to download {} from {}'.format(track_name, file_url))

        else:
            logger.error('Failed to find track in source!')

        # randomly sleep a few seconds
        time.sleep(random.uniform(13, 35))


if __name__ == '__main__':
    main()
