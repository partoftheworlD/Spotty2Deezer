import json
import requests

class Spotify:
    def __init__(self, token, playlist_id) -> None:
        self.track_list = []
        self.token = token
        self.header = { 'Accept': 'application/json',
                        'Authorization': f'Bearer {self.token}'}
        self.playlist_api = 'https://api.spotify.com/v1/playlists/'
        self.playlist_id = playlist_id
        self.playlist_name = ''
        self.body = None

    def getPlaylistInfo(self):
        # TODO: Add check for some weird name of tracks
        response = requests.get(self.playlist_api + self.playlist_id, headers=self.header)
        if response.status_code == requests.status_codes.codes.ok:
            self.body = response.json()
            self.playlist_name = self.body['name']
        else:
            print('[+] ', response.status_code)
    
    def getPlaylist(self):
        self.getPlaylistInfo()
        data = []
        next = ''
        try:
            data = [self.body['tracks']['items'][i]['track']['artists'][0]['name'] +
                    ' - ' + self.body['tracks']['items'][i]['track']['name'] for i in range(len(self.body['tracks']['items']))]
        except TypeError:
            pass

        self.track_list.append(data)

        next = self.body['tracks']['next']

        if next:
            response = requests.get(next, headers=self.header)
        while next != None:
            response = requests.get(next, headers=self.header)
            if response.status_code == requests.status_codes.codes.ok:
                body = response.json()
                data = [body['items'][i]['track']['artists'][0]['name'] +
                        ' - ' + body['items'][i]['track']['name'] for i in range(len(body['items']))]
                self.track_list.append(data)
                next = body['next']
        

class Deezer:
    def __init__(self, playlist_name, track_list, access_token, user_id) -> None:
        self.access_token = access_token
        self.playlist_name = playlist_name
        self.user_id = user_id
        self.playlist_id = ''
        self.track_list = track_list

    def createPlaylist(self):
        response = requests.post(
            f'https://api.deezer.com/user/{self.user_id}/playlists/?title={self.playlist_name}&request_method=post&access_token={self.access_token}')
        if response.status_code == requests.status_codes.codes.ok:        
            self.playlist_id = response.json()['id']

    def addTracks(self):
        for query in [track for idx in range(len(self.track_list)) for track in self.track_list[idx]]:
            # Search track
            try:
                track_id = requests.get(
                    f'https://api.deezer.com/search?q={query}').json()['data'][0]['id']
                # Add to playlist
                requests.post(
                    f'https://api.deezer.com/playlist/{self.playlist_id}/tracks?songs={track_id}&request_method=post&access_token={self.access_token}')
            except IndexError:
                print(f'Not found {query}')

# Spotify token https://accounts.spotify.com/authorize?response_type=token&client_id=<client_id>&scope=playlist-read-private&redirect_uri=http://localhost:5000/callback
# Deezer code   https://connect.deezer.com/oauth/auth.php?perms=manage_library&app_id=<app_id>&redirect_uri=http://localhost:5000/callback
# Deezer token  https://connect.deezer.com/oauth/access_token.php?app_id={app_id}&secret={secret}&code={code}
if __name__ == '__main__':
    spotify = Spotify('<TOKEN>',
                      '<PLAYLIST-ID>')
    spotify.getPlaylist()

    deezer = Deezer(spotify.playlist_name,
                    spotify.track_list,
                    '<ACCESS-TOKEN>',
                    '<USER-ID>')

    deezer.createPlaylist()
    deezer.addTracks()
    
    
