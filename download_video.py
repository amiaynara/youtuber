# https://github.com/googleapis/google-api-python-client/blob/main/docs/start.md

import json 
import argparse
import googleapiclient.discovery
from urllib.parse import parse_qs, urlparse
from pytube import YouTube
from pytube.cli import on_progress

# constants
DESTINATION = '../test_playlist'  # make this a command line argument
DOWNLOAD_RESOLUTION = '480p'
TEST_PLAYLIST = 'https://www.youtube.com/playlist?app=desktop&list=PL59FEE129ADFF2B12'

class YouTubeWrapper():
  '''Wrapper to customise download from youtube'''

  def __init__(self, api_key_filename):
    self.api_key = self._get_secret(api_key_filename).get('api_key', None)

  def _get_secret(self, api_key_filename):
    '''Method to get secret, this can be pushed to an abstract class'''
    # read file
    content = None
    try:
      with open(api_key_filename, 'r') as eye:
        content = eye.read()
    except Exception as error:
      print(f'ERROR: file {file_name} not found')
      print(error)
    return content and json.loads(content)

  def download_playlist(self, playlist_link, destination, download_quality=DOWNLOAD_RESOLUTION):
    '''Use pytube library to download the youtube playlist'''
    if not playlist_link:
      playlist_link = TEST_PLAYLIST
      print(f'WARNING: Playlist link was not provided, as a demo downloading videos from {TEST_PLAYLIST}')
    links = self.extract_playlist_links(playlist_link) or []
    for link in links:
      try:
        self.download_video(link, download_quality)
      except:
        print('ERROR: Could not download', link)
  
  def download_video(self, video_link, download_resolution=DOWNLOAD_RESOLUTION):
    '''Use pytube to dowload a video'''
    yt = YouTube(
      video_link,
      on_progress_callback=on_progress
    )
    print(f'Downloading {yt.title} ...')
    yt and yt.streams.filter(res=download_resolution).first().download(DESTINATION)
    
  def extract_playlist_links(self, play_list_url=None):
    '''Returns list of urls from a playlist on youtube'''
    #extract playlist id from url
    try:
      message = f'PlayList: {play_list_url}, link is not valid'
      if play_list_url:
        url = play_list_url
        query = parse_qs(urlparse(url).query, keep_blank_values=True)
        playlist_id = query["list"][0]
        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=self.api_key)
        request = youtube.playlistItems().list(
          part = "snippet",
          playlistId = playlist_id,
          #maxResults = 50,
        )
        response = request.execute()
        playlist_items = []
        while request is not None:
          response = request.execute()
          playlist_items += response["items"]
          request = youtube.playlistItems().list_next(request, response)

        message = f'PlayList is valid. Number of videos found: {len(playlist_items)}'
        play_list_links = [f'https://www.youtube.com/watch?v={t["snippet"]["resourceId"]["videoId"]}&list={playlist_id}&t=0s' 
                                  for t in playlist_items]
        return play_list_links
    except Exception as error:
      print(error)
    print(message)

def main():
  args = read_args()
  api_key_filename = args.api_key or '/Users/amiaynarayan/Projects/secrets/youtube/secrets.json'
  yt = YouTubeWrapper(api_key_filename)
  #gate_playlist = 'https://www.youtube.com/watch?v=WZMfFqIXKlw&list=PLiSPNzs4fD9vGQD-aUVKpDuzsRaXekgjj' # Maths xe gate playlist
  gate_playlist = args.playlist_url
  download_quality = args.video_url
  destination = args.folder_name
  yt.download_playlist(gate_playlist, destination, download_quality)

def read_args():
  '''Read the arguments'''
  parser = argparse.ArgumentParser()
  parser.add_argument("--api-key", help="api key json file")
  parser.add_argument("--folder-name", help="Folder name where videos will be downloaded", default=DESTINATION)
  parser.add_argument("--playlist-url", help="URL of the playlist, we want to work on")
  parser.add_argument("--video-url", help="URL of the video, we want to work on")
  parser.add_argument("--video-quality", help="Quality of video we want to work with", default=DOWNLOAD_RESOLUTION)
  return parser.parse_args()

if __name__ == '__main__':
  main()

