"""
Tests for the middleware
"""
from sys import version_info
if version_info.major == 2:
    import __builtin__ as builtins  # pylint:disable=import-error
else:
    import builtins  # pylint:disable=import-error

from cStringIO import StringIO

from mock import Mock, mock_open, patch
from nose.tools import eq_


from mpg123_wrapper import Playlist, enqueue_output


def test_ignore_comments():
    """Loading a playlist ignores comment lines
    """
    sample = StringIO("\n".join([
        "#ignore this",
        "/actual/entry"]))
    actual = Playlist.load_playlist(sample, '')
    expected = ['/actual/entry']
    eq_(actual, expected)


def test_prepend_basepath():
    """Loading a relative path playlist entry prepends the basepath
    """
    sample = StringIO("actual/entry")
    actual = Playlist.load_playlist(sample, '/basepath/')
    expected = ['/basepath/actual/entry']
    eq_(actual, expected)


def test_absolute_path():
    """"Loading an absolute path playlist entry doesn't use the basepath
    """
    sample = StringIO("/actual/entry")
    actual = Playlist.load_playlist(sample, '/basepath/')
    expected = ['/actual/entry']
    eq_(actual, expected)


def test_next_seq():
    """Playlist.next() returns the next track in sequential mode
    """
    sample = "\n".join(["/first/file", "/second/file"])
    with patch.object(builtins, 'open',
                      mock_open(read_data=sample)) as mock_file:
        # see
        # http://bash-shell.net/blog/2014/feb/27/file-iteration-python-mock/
        # Apparently this is patched in python 3...
        mock_file.return_value.__iter__.return_value = sample.splitlines()
        playlist = Playlist('bogus', 'seq')
    eq_(playlist.next_track(), '/second/file')
    eq_(playlist.next_track(), '/first/file')


class TestProcessOutput(object):
    """Tests for filtering mpg123 output
    """
    def setup(self):
        """Initilize mocks
        """
        self.mock_out = Mock()
        self.mock_out.readline = Mock()
        self. mock_q = Mock()

    def test_process_ignore_frame(self):
        """Processing the output from mpg123 ignores @F lines
        """
        self.mock_out.readline.side_effect = [
            '@F 12320 502 321.83 13.11',
            '@F 12321 501 321.85 13.09',
            '@F 12322 500 321.88 13.06',
            '@P 0',
            '@F 12323 499 321.91 13.04',
            '@F 12324 498 321.93 13.01',
        ]

        enqueue_output(self.mock_out, self.mock_q)

        self.mock_q.put.assert_called_once_with('@P 0')

    def test_process_catch_end_of_track(self):
        """processing mpg123 output finds @P 0 end of track marker
        """
        self.mock_out.readline.side_effect = ['@P 0']

        enqueue_output(self.mock_out, self.mock_q)

        self.mock_q.put.assert_called_once_with('@P 0')

    def test_process_ignore_no_data(self):
        """processing mpg123 output ignores coreaudio warning about no data
        """
        self.mock_out.readline.side_effect = [
            '@F 12320 502 321.83 13.11',
            '@F 12321 501 321.85 13.09',
            '@F 12322 500 321.88 13.06',
            '@P 0',
            "[coreaudio.c:81] warning: Didn't have any audio data in callback"
            "(buffer underflow)",
            "[coreaudio.c:81] warning: Didn't have any audio data in callback"
            "(buffer underflow)"
        ]

        enqueue_output(self.mock_out, self.mock_q)

        self.mock_q.put.assert_called_once_with('@P 0')
