from datetime import datetime, timedelta
import logging
import os

from podcast_library_manager import PodcastCollection
import recorders.jeff_ward_show as jws

media_directory = os.path.join('media', 'jeff_ward_show')
media_host_url = 'http://foolsgold.arcadecoffee.com/media/jeff_ward_show'
rss_template = os.path.join('templates', 'jeff_ward_show.rss.jinja2')
rss_output = os.path.join('rss', 'jeff_ward_show.rss')
episode_length = timedelta(hours=3)
max_episode_age = timedelta(days=7)
file_mode = 0o644

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

recording_filename = os.path.join(media_directory, f'{datetime.now().strftime("%Y%m%d")}.mp3')
jws.record_show(dest_filename=recording_filename, duration=episode_length)
os.chmod(dest_filename, file_mode)

podcasts = PodcastCollection(media_directory)
podcasts.purge_old_episodes(max_episode_age)
rss_content = podcasts.create_rss_file(rss_template, media_host_url)

logging.info(f'writing rss file to {rss_output}')
with open(rss_output, 'w') as file_:
    file_.write(rss_content)
