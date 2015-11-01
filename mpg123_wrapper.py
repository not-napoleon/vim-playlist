#!/usr/bin/env python
"""
Interface between vim (or anything really) and mpg123

The main goal here is to detect when playing a song has finished and
queue up the next track.  Additional interactive commands are read from
a pipe and forwarded to mpg123
"""
import fcntl
import os
import random
from subprocess import Popen, PIPE
import sys
# See http://stackoverflow.com/a/4896288/529459 for details on why we're using
# threading and the general IPC model --Tozzi(31 Oct 2015 13:23:00)
from threading import Thread

from Queue import Queue, Empty


class Playlist(object):

    """Manage playlist state"""

    def __init__(self, mode):
        """Initilize the playlist

        :param playlist_filename: Filename of the playlist to laod
        :param mode: one of ['seq', 'shuf', 'rand']

        """
        self._playlist = []
        self._playlist_file = None
        if mode not in ('seq', 'shuf'):
            raise NotImplementedError("Unsupported playback mode: %s", mode)
        self._mode = mode
        self._curr_track = None

    @property
    def current_track(self):
        """The name of the current track
        """
        if self._playlist:
            return self._playlist[self._curr_track]
        return None

    def load(self, playlist_file):
        """Reload the playlist from the tied file
        """
        basedir = os.path.dirname(playlist_file)
        with open(playlist_file) as playlist:
            self._playlist = Playlist.parse_playlist(playlist, basedir)
        if len(self._playlist):
            self._curr_track = 0
        if self._mode == 'shuf':
            random.shuffle(self._playlist)
        print "Loaded %s tracks" % len(self._playlist)

    @staticmethod
    def parse_playlist(playlist_file, base_dir):
        """Load the given playlist file into a python data structure

        :param playlist_file: open file-like containing the playlist
        :param base_dir: base directory to which paths in the playlist
                         are relative
        :returns: list of paths to playable MP3 files

        """
        playlist = []
        for line in playlist_file:
            if line.startswith('#'):
                continue
            # TIL os.path.join will discard all components prior to the last
            # absolute path, so if line already contains an absolute path,
            # it'll just do the right thing here.
            line = os.path.join(base_dir, line)
            playlist.append(line)
        return playlist

    def next_track(self):
        """Return the next track to play
        """
        if self._mode in ('seq', 'shuf'):
            self._curr_track += 1
            self._curr_track %= len(self._playlist)
        return self._playlist[self._curr_track]


def poll_mpg123(out, queue):
    """Blocking read the output pipe, and add results to the synchronized queue
    """
    for line in iter(out.readline, b''):
        if line.startswith('@P'):
            queue.put(line.strip())
    out.close()


def poll_vim(fifo_name, queue):
    """Repeatedly open and read the fifo vim uses to send commands, and put
    the results on a synchronized queue
    """
    while True:
        with open(fifo_name) as fifo:
            for line in fifo:
                queue.put(line.strip().lower())


def main(fifo_name, lockfile):
    """Run a poller loop to manage the player
    """
    fp = open(lockfile, 'w')
    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        # another instance is running
        sys.exit(1)
    # load initial playlist
    playlist = Playlist('shuf')
    # launch player
    player = Popen(['mpg123', '-R'], stdout=PIPE, stdin=PIPE)
    player_output = Queue()
    player_poll_thread = Thread(target=poll_mpg123,
                                args=(player.stdout, player_output))
    player_poll_thread.daemon = True   # thread dies with the program
    player_poll_thread.start()

    controller_input = Queue()
    controller_poll_thread = Thread(target=poll_vim,
                                    args=(fifo_name, controller_input))
    controller_poll_thread.daemon = True
    controller_poll_thread.start()

    while True:
        # poll player
        try:
            message = player_output.get_nowait()
            print "message %s" % message
        except Empty:
            message = None
        if message == '@P 0':
            player.stdin.write("LOAD %s\n" % playlist.next_track())
            print playlist.current_track

        try:
            command = controller_input.get_nowait()
            print "command %s" % command
        except Empty:
            command = None

        if command == 'pause':
            player.stdin.write("PAUSE\n")
        elif command == 'skip':
            player.stdin.write("LOAD %s\n" % playlist.next_track())
            print playlist.current_track
        elif command and command.startswith("load"):
            # Load playlist
            playlist_file = command[5:]
            playlist.load(playlist_file)
            track = playlist.current_track
            if track:
                player.stdin.write("LOAD %s\n" % track)
                print track


if __name__ == '__main__':
    _, fifo, lockfile = sys.argv
    main(fifo, lockfile)
