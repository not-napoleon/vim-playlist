"""
Interface between vim (or anything really) and mpg123

The main goal here is to detect when playing a song has finished and
queue up the next track.  Additional interactive commands are read from
a pipe and forwarded to mpg123
"""
import os
from subprocess import Popen, PIPE
# See http://stackoverflow.com/a/4896288/529459 for details on why we're using
# threading and the general IPC model --Tozzi(31 Oct 2015 13:23:00)
from threading import Thread

from Queue import Queue, Empty


class Playlist(object):

    """Manage playlist state"""

    def __init__(self, playlist_filename, mode):
        """Initilize the playlist

        :param playlist_filename: Filename of the playlist to laod
        :param mode: one of ['seq', 'suf', 'rand']

        """
        self._playlist = []
        self._playlist_file = playlist_filename
        if mode not in ('seq'):
            raise NotImplementedError("Unsupported playback mode: %s", mode)
        self._mode = mode
        self.reload()
        print "Playlist initlized with %s" % self._playlist
        self._curr_track = None
        if len(self._playlist):
            self._curr_track = 0

    def reload(self):
        """Reload the playlist from the tied file
        """
        basedir = os.path.dirname(self._playlist_file)
        with open(self._playlist_file) as playlist:
            self._playlist = Playlist.load_playlist(playlist, basedir)

    @staticmethod
    def load_playlist(playlist_file, base_dir):
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
        if self._mode == 'seq':
            self._curr_track += 1
            self._curr_track %= len(self._playlist)
        return self._playlist[self._curr_track]


def enqueue_output(out, queue):
    """Blocking read the output pipe, and add results to the synchronized queue
    """
    for line in iter(out.readline, b''):
        if line.startswith('@P'):
            queue.put(line.strip())
    out.close()


def main(playlist_file):
    """Run a poller loop to manage the player
    """
    # load initial playlist
    playlist = Playlist(playlist_file, 'seq')
    # launch player
    player = Popen(['mpg123', '-R'], stdout=PIPE, stdin=PIPE)
    player_output = Queue()
    player_poll_thread = Thread(target=enqueue_output, args=(player.stdout,
                                                             player_output))
    player_poll_thread.daemon = True   # thread dies with the program
    player_poll_thread.start()

    # Start the initial track playing
    player.stdin.write("LOAD %s\n" % playlist.next_track())
    while True:
        # poll player
        try:
            message = player_output.get_nowait()
            print message
        except Empty:
            message = None
        if message == '@P 0':
            next_track = playlist.next_track()
            print "Loading %s" % next_track
            player.stdin.write("LOAD %s\n" % next_track)


if __name__ == '__main__':
    main('/Users/mtozzi/playlist.m3u')
