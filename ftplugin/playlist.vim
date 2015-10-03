let g:playlist_fifo_path=$HOME . '/.vim/tmp/playlist_fifo'

function! s:SendCommand(command_string)
    let l:command = 'echo ' . shellescape(a:command_string) . ' > ' . g:playlist_fifo_path
    echom l:command
    call system(l:command)
endfunction


" MPG123 remote commands
" @H {
" @H HELP/H: command listing (LONG/SHORT forms), command case insensitve
" @H LOAD/L <trackname>: load and start playing resource <trackname>
function! s:LoadMP3File(filename)
    call <SID>SendCommand('LOAD ' . a:filename)
endfunction

function! s:LoadCurrentLine()
    call <SID>LoadMP3File(getline('.'))
endfunction

" @H LOADPAUSED/LP <trackname>: load but do not start playing resource <trackname>
" @H LOADLIST/LL <entry> <url>: load a playlist from given <url>, and display its entries, optionally load and play one of these specificed by the integer <entry> (<0: just list, 0: play last track, >0:play track with that position in list)
" @H PAUSE/P: pause playback
function! s:PausePlayback()
    call <SID>SendCommand('PAUSE')
endfunction
" @H STOP/S: stop playback (closes file)
" @H JUMP/J <frame>|<+offset>|<-offset>|<[+|-]seconds>s: jump to mpeg frame <frame> or change position by offset, same in seconds if number followed by "s"
" @H VOLUME/V <percent>: set volume in (0..100...); float value
" @H RVA off|(mix|radio)|(album|audiophile): set rva mode
" @H EQ/E <channel> <band> <value>: set equalizer value for frequency band 0 to 31 on channel 1 (left) or 2 (right) or 3 (both)
" @H EQFILE <filename>: load EQ settings from a file
" @H SHOWEQ: show all equalizer settings (as <channel> <band> <value> lines in a SHOWEQ block (like TAG))
" @H SEEK/K <sample>|<+offset>|<-offset>: jump to output sample position <samples> or change position by offset
" @H SCAN: scan through the file, building seek index
" @H SAMPLE: print out the sample position and total number of samples
" @H FORMAT: print out sampling rate in Hz and channel count
" @H SEQ <bass> <mid> <treble>: simple eq setting...
" @H PITCH <[+|-]value>: adjust playback speed (+0.01 is 1 % faster)
" @H SILENCE: be silent during playback (meaning silence in text form)
" @H STATE: Print auxiliary state info in several lines (just try it to see what info is there).
" @H TAG/T: Print all available (ID3) tag info, for ID3v2 that gives output of all collected text fields, using the ID3v2.3/4 4-character names. NOTE: ID3v2 data will be deleted on non-forward seeks.
" @H    The output is multiple lines, begin marked by "@T {", end by "@T }".
" @H    ID3v1 data is like in the @I info lines (see below), just with "@T" in front.
" @H    An ID3v2 data field is introduced via ([ ... ] means optional):
" @H     @T ID3v2.<NAME>[ [lang(<LANG>)] desc(<description>)]:
" @H    The lines of data follow with "=" prefixed:
" @H     @T =<one line of content in UTF-8 encoding>
" @H meaning of the @S stream info:
" @H S <mpeg-version> <layer> <sampling freq> <mode(stereo/mono/...)> <mode_ext> <framesize> <stereo> <copyright> <error_protected> <emphasis> <bitrate> <extension> <vbr(0/1=yes/no)>
" @H The @I lines after loading a track give some ID3 info, the format:
" @H      @I ID3:artist  album  year  comment genretext
" @H     where artist,album and comment are exactly 30 characters each, year is 4 characters, genre text unspecified.
" @H     You will encounter "@I ID3.genre:<number>" and "@I ID3.track:<number>".
" @H     Then, there is an excerpt of ID3v2 info in the structure
" @H      @I ID3v2.title:Blabla bla Bla
" @H     for every line of the "title" data field. Likewise for other fields (author, album, etc).
" @H }
"
" /Volumes/KINGSTON/Music/The Black Mages/The Skies Above/The Black Mages - Maybe I'm a Lion (Final Fantasy VIII).mp3

"Play the file on the current line

nnoremap <Plug>(playlist-play-selected) :call <SID>LoadCurrentLine()<cr>
nnoremap <Plug>(playlist-pause-playback) :call <SID>PausePlayback()<cr>



" Nicer UI Mappings
" TODO: Let users override or toggle these or something
nmap <buffer> <cr> <Plug>(playlist-play-selected)
nmap <buffer> <space> <Plug>(playlist-pause-playback)
