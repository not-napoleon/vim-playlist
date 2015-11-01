if exists('g:loaded_playlist_ftp')
    finish
endif
let g:loaded_playlist_ftp=1

nnoremap <Plug>(playlist-load-current) :PlaylistLoad <C-r>=expand('%:p')<cr><cr>


" function! s:LoadCurrentLine()
"     call <SID>LoadMP3File(getline('.'))
" endfunction

"Play the file on the current line

" nnoremap <Plug>(playlist-play-selected) :call <SID>LoadCurrentLine()<cr>
" nnoremap <Plug>(playlist-pause-playback) :call <SID>PausePlayback()<cr>
"


" Nicer UI Mappings
" TODO: Let users override or toggle these or something
" nmap <buffer> <cr> <Plug>(playlist-play-selected)
" nmap <buffer> <space> <Plug>(playlist-pause-playback)
"
"
"
