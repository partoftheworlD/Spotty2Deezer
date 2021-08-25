import json
import requests
import re
import socket

class Spotify:
    def __init__(self, playlist_id) -> None:
        self.track_list = []
        self.token = ''
        self.client_id = ''
        self.header = {}
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

    def getToken(self):
        rc = re.compile(r'(\=[A-Za-z0-9\-\_]+)).*')
        # TODO: Doesn't work like a Deezer version
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind(('', 5000))
        serversocket.listen(5)
        requests.get(f'https://accounts.spotify.com/authorize?response_type=token&client_id={self.client_id}\
            &scope=playlist-read-private&redirect_uri=http://localhost:5000/callback')
        (clientsocket, _) = serversocket.accept()
        self.token = re.findall(rc, str(clientsocket.recv(512)))
        serversocket.close()
        self.header = {'Accept': 'application/json','Authorization': f'Bearer {self.token}'}
    
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
    def __init__(self, playlist_name, track_list, app_id, secret) -> None:
        self.app_id = app_id
        self.secret = secret
        self.access_token = ''
        self.playlist_name = playlist_name
        self.user_id = ''
        self.playlist_id = ''
        self.track_list = track_list
        self.code = ''

    def createPlaylist(self):
        response = requests.post(
            f'https://api.deezer.com/user/{self.user_id}/playlists/?title={self.playlist_name}&request_method=post&access_token={self.access_token}')
        if response.status_code == requests.status_codes.codes.ok:        
            self.playlist_id = response.json()['id']

    def getCode(self):
        rc = re.compile('(fr[a-z0-9]+).*')

        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind(('', 5000))
        serversocket.listen(5)
        requests.get(
            f'https://connect.deezer.com/oauth/auth.php?app_id={self.app_id}&\
            redirect_uri=http://localhost:5000/callback&perms=manage_library')
        (clientsocket, _) = serversocket.accept()
        self.code = re.findall(rc, str(clientsocket.recv(64)))[0]
        serversocket.close()

    def getToken(self):
        self.getCode()
        rc = re.compile('(fr[0-9a-zA-Z]+).*')
        data = requests.get(
            f'https://connect.deezer.com/oauth/access_token.php?app_id={self.app_id}\
                &secret={self.secret}&code={self.code}').text
        self.access_token = re.findall(rc, data)[0]
        self.getUserID()

    
    def getUserID(self):
        self.user_id = requests.get(f'https://api.deezer.com/user/me?access_token={self.access_token}').json()['id']


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

if __name__ == '__main__':
    spotify = Spotify('<ACCESS-TOKEN>',
                      '<PLAYLIST-ID>')
    spotify.getPlaylist()
    deezer = Deezer(spotify.playlist_name,
                    spotify.track_list,
                    '<APP-ID>',
                    '<ACCESS-TOKEN>')

    deezer.getToken()
    deezer.createPlaylist()
    deezer.addTracks()
    
    
