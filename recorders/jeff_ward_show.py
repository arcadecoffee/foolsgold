import logging
import os
import re
import random
import requests
import shutil
import xml.etree.ElementTree as ElementTree

from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile

import eyed3.id3

show_length = timedelta(hours=3)


def choose_server():
    url = 'http://playerservices.streamtheworld.com/api/livestream?station=SNN_RADIO&version=1.9'
    servers = []

    logging.info(f'getting recording sources from {url}')

    xml_string = re.sub(r'\sxmlns="[^"]+"', '', requests.get(url).text, count=1)
    mountpoint = ElementTree.fromstring(xml_string).\
        find('mountpoints/mountpoint/media-format/audio/[@bitrate="96000"]/[@codec="mp3"]/../..')
    mount = mountpoint.find('mount').text

    for server in mountpoint.findall('servers/server'):
        servers.append({
            'ip': server.find('ip').text,
            'ports': list(map(lambda n: n.text, server.findall('ports/port/[@type="http"]')))
        })

    server = random.choice(servers)
    if '80' in server['ports']:
        return f"http://{server['ip']}/{mount}.mp3"
    else:
        return f"http://{server['ip']}:{random.choice(server['ports'])}/{mount}.mp3"


def record_show(dest_filename='jeff_ward_show.mp3', duration=show_length):
    stream = requests.get(url=choose_server(), stream=True)

    with NamedTemporaryFile('wb', delete=False) as incoming_file:

        logging.info(f'writing stream from {stream.url} to {incoming_file.name} for {duration}')

        end_time = datetime.now() + duration
        for block in stream.iter_content(1024):
            incoming_file.write(block)
            if datetime.now() > end_time:
                break
        incoming_file.close()

        logging.info('recording complete, adding ID3 tags')

        mp3file = eyed3.load(incoming_file.name)
        mp3file.tag = eyed3.id3.Tag()
        mp3file.tag.artist = 'Jeff Ward'
        mp3file.tag.album = 'The Jeff Ward Show'
        mp3file.tag.title = f'The Jeff Ward Show - {datetime.now().date().isoformat()}'
        mp3file.tag.recording_date = eyed3.core.Date(*list(datetime.now().timetuple())[:6])
        mp3file.tag.save()

        logging.info(f'moving recording from {incoming_file.name} to {dest_filename}')

        os.makedirs(os.path.dirname(dest_filename), exist_ok=True)
        shutil.move(incoming_file.name, dest_filename)
        os.chmod(dest_filename, 0o644)