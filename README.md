# vim-playlist
Use vim as a front-end to mpg123

# Requirements
vim-playlist requires a working python install.  At the moment, it's tested
against python 2.7.  I hope to add 3.4 support soon.  No additional libraries
are required to run the server, although the tests do have a few extra
requirements (mock, nose)

# Quick Start
    :PlaylistLoad path_to_playlist

# Why?
The line of reasoning that has led me to this point can be summarized as:

 1. iTunes sucks
 1. So apparently does everything else
 1. mpg123 is usable, mostly...
 1. ...except the console controls aren't reading keyboard events right on my
    terminal, and frankly are pretty minimal anyway
 1. The FIFO controls are working fine though
 1. I should just write a script to manage the FIFO controls
 1. It would be sweet if that script had a playlist editor
 1. Even writing a minimal editor is a ton of work
