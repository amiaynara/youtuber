# https://github.com/googleapis/google-api-python-client/blob/main/docs/start.md

import json 
import googleapiclient.discovery
from urllib.parse import parse_qs, urlparse
from pytube import YouTube
from pytube.cli import on_progress

# constants
DOWNLOAD_RESOLUTION = '480p'
DESTINATION = '../maths_xe_gate_720p'  # make this a command line argument

class YouTubeWrapper():
  '''Wrapper to customise download from youtube'''

  def __init__(self):
    self.api_key = self._get_secret().get('api_key', None)

  def _get_secret(self):
    '''Method to get secret, this can be pushed to an abstract class'''
    # read file
    file_name = '/Users/amiaynarayan/Projects/secrets/youtube/secrets.json' # make this an command line argument
    content = None
    try:
      with open(file_name, 'r') as eye:
        content = eye.read()
    except Exception as error:
      print(f'ERROR: file {file_name} not found')
      print(error)
    return content and json.loads(content)

  def download_playlist(self, playlist_link):
    '''Use pytube library to download the youtube playlist'''
    pass
  
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

  def percent(self, tem, total):
    perc = (float(tem) / float(total)) * float(100)
    return perc

  def progress_function(self, stream, chunk, bytes_remaining):
    '''Method that tracks the progess of download'''
    size = stream.filesize
    p = 0
    print('progress function was called', bytes_remaining, size)
    while p <= 100:
      progress = p
      print(str(p)+'%')
      p = self.percent(bytes_remaining, size)

def main():
  args = read_args()
  yt = YouTubeWrapper()
  playlist_url = 'https://www.youtube.com/watch?v=WZMfFqIXKlw&list=PLiSPNzs4fD9vGQD-aUVKpDuzsRaXekgjj' # Maths xe gate playlist
  links = yt.extract_playlist_links(playlist_url) or []
  for link in links:
    try:
      yt.download_video(link, '720p')
    except:
      print('could not download', link)

def read_args():
  '''Read the arguments'''
  args = {}
  return args

if __name__ == '__main__':
  main()

