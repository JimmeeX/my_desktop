#!/usr/bin/env python3

import dbus, argparse, re

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def print_field(string, width):
    """
    Prints Multi-line
    Pads based on Height 
    Allocate Max Height of N
    """
    for i, chunk in enumerate(chunker(string, width)):
        print('${alignc}' + chunk)
    return

def print_all(title, artist, width):
    # Allocate 3 lines to title, 1 line to artist, pad rest

    regex = r"[^A-Za-z0-9\s'\-\.\[\]\|]"
    title = re.sub(regex, "", title)
    artist = re.sub(regex, "", artist)
    curr_height = 4
    for i, chunk in enumerate(chunker(title, width)):
        if curr_height == 1: break
        print('${alignc}${font Open Sans:pixelsize=16:bold}' + chunk)
        curr_height -= 1
    print('${alignc}${font Open Sans:pixelsize=14}' + artist)
    curr_height -= 1 

    # Padding Prints
    if curr_height <= 0: return
    for i in range(curr_height): print('')
    return

class Player:

    _name = None
    _service = None
    _player = None
    _interface = None
    _bus = dbus.SessionBus()
    _info = {}
    _pause_icon = "\uf04c"
    _play_icon = "\uf04b"
    _trackMap = {
        'trackid': 'mpris:trackid',
        'length': 'mpris:length',
        'artUrl': 'mpris:artUrl',
        'album': 'xesam:album',
        'artist': 'xesam:artist',
        'title': 'xesam:title',
        'url': 'xesam:url',
        'rating': 'xesam:autoRating',
        'status': 'PlaybackStatus',
    }

    def __init__(self, service):
        self._service = service
        self._name = service.split('.')[-1]
        self._player = self._bus.get_object(self._service,
                                            '/org/mpris/MediaPlayer2')
        self._interface = dbus.Interface(
            self._player, dbus_interface='org.freedesktop.DBus.Properties')
        self.get_metadata()

    # Get all availables information from DBus for a player object
    def get_metadata(self):
        self._info = {}
        metadata = self._interface.GetAll('org.mpris.MediaPlayer2.Player')
        for key, val in metadata.items():
            if isinstance(val, dict):
                for subk, subv in val.items():
                    self._info[subk] = subv
            self._info[key] = val

    def is_playing(self):
        return self._info['PlaybackStatus'] == 'Playing'

    # Print information for a player
    def print_metadata(self):
        for k, v in self._trackMap.items():
            if v not in self._info:
                continue
            val = self._info[v]
            print(f"{k}: {', '.join(val) if isinstance(val, list) else val}")
            
    def retrieve_metadata(self):
        metadata = {}
        for k, v in self._trackMap.items():
            if v not in self._info:
                continue
            val = self._info[v]
            metadata[k] = str(', '.join(val) if isinstance(val, list) else val)
        return metadata

    def next(self):
        dbus.Interface(
            self._player,
            dbus_interface='org.mpris.MediaPlayer2.Player').Next()

    def prev(self):
        dbus.Interface(
            self._player,
            dbus_interface='org.mpris.MediaPlayer2.Player').Previous()

    def play_pause(self):
        dbus.Interface(
            self._player,
            dbus_interface='org.mpris.MediaPlayer2.Player').PlayPause()

    def stop(self):
        dbus.Interface(
            self._player,
            dbus_interface='org.mpris.MediaPlayer2.Player').Stop()


def get_player_details():
    sessions = dbus.SessionBus().list_names()
    players = []
    for session in sessions:
        if "org.mpris.MediaPlayer2" in session:
            player = Player(session)
            metadata = player.retrieve_metadata()
            session_index = get_session_index(session)
            status_index = get_status_index(metadata['status'])
            players.append((status_index, session_index, metadata['title'], metadata['artist']))

    sorted_players = sorted(players, key=lambda k: (k[0], k[1]))
    return sorted_players[0]

def get_session_index(session):
    preferred_sessions = ['chrome', 'spotify']
    for i, preferred_session in enumerate(preferred_sessions):
        if preferred_session in session: return i
    return i+1 # Low Priority for any other media

def get_status_index(status):
    preferred_status = ['Playing', 'Paused', 'Stopped']
    return preferred_status.index(status)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--width', type=int, default=25)
    args = parser.parse_args()

    try:
        (status_index, session_index, title, artist) = get_player_details()
    except IndexError as e:
        # No Players Running
        # if args.status: print(status_index)
        # if args.artist: pass
        # if args.title: print_field("No Music Detected", args.width)
        print_all("No Music Detected", '', args.width)
    else:
        # if args.status: print(status_index)
        # if args.artist: print_field(artist, args.width)
        # if args.title: print_field(title, args.width)
        print_all(title, artist, args.width)
