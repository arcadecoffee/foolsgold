import logging
import os
from datetime import datetime, timedelta

import eyed3
from jinja2 import Template


class PodcastCollection:
    def __init__(self, directory=None):
        self.directory = directory
        if directory:
            self.load_directory(directory)

    def load_directory(self, directory):
        logging.info('getting list of episode files')
        self.episodes = []
        for filename in os.listdir(directory):
            if filename.endswith('.mp3'):
                filepath = os.path.join(directory, filename)
                mp3file = eyed3.load(filepath)
                self.episodes.append({
                    'date': datetime.fromisoformat(str(mp3file.tag.recording_date)),
                    'size': mp3file.info.size_bytes,
                    'duration': timedelta(seconds=int(mp3file.info.time_secs)),
                    'filename': filename,
                    'filepath': filepath,
                })
        logging.info(f'found {len(self.episodes)} episodes')

    def purge_old_episodes(self, max_age):
        if max_age:
            episodes_to_purge = list(filter(lambda e: datetime.now() - e['date'] > max_age, self.episodes))
            logging.info(f'found {len(episodes_to_purge)} episodes to purge')
            for episode in episodes_to_purge:
                logging.info(f'removing {episode["filename"]}')
                os.remove(episode['filepath'])
                self.episodes.remove(episode)

    def create_rss_file(self, rss_template, media_host_url):
        logging.info(f'populating rss template with {len(self.episodes)} episodes')
        with open(rss_template) as file_:
            template = Template(file_.read())
        return template.render(episodes=self.episodes, media_host_url=media_host_url)
