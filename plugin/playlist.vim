if exists('g:loaded_playlist_global')
    finish
endif
let g:loaded_playlist_global=1

let s:plugin_dir = expand('<sfile>:p:h:h')

" Keep track of if we've launched the player middleware yet.  Don't worry
" about launching it multiple times (e.g. from sepearate vim instnaces), the
" middleware takes care of that with a lockfile
let s:is_running=0

" Global mappings for interacting with the running player instance
if !exists('g:playlist_fifo_path')
    let g:playlist_fifo_path=$HOME . '/.vim/tmp/playlist_fifo'
endif

if !exists('g:playlist_lock_path')
    let g:playlist_lock_path=$HOME . '/.vim/tmp/playlist_lock'
endif

function! s:LaunchMiddleware()
    if !s:is_running
        " echom 'Starting middleware'
        let l:command =
            \  '/usr/bin/env python ' . s:plugin_dir . '/mpg123_wrapper.py'
            \. ' ' . shellescape(g:playlist_fifo_path)
            \. ' ' . shellescape(g:playlist_lock_path)
            \. ' &'
        " echom l:command
        call system(l:command)
        let s:is_running = 1
    endif
endfunction

function! s:SendCommand(command_string)
    call <SID>LaunchMiddleware()
    let l:command = 'echo ' . shellescape(a:command_string) . ' > ' . g:playlist_fifo_path
    echom l:command
    call system(l:command)
endfunction


nnoremap <Plug>(playlist-pause) :call <SID>SendCommand('pause')<cr>
nnoremap <Plug>(playlist-skip) :call <SID>SendCommand('skip')<cr>
nnoremap <Plug>(playlist-quit) :call <SID>SendCommand('quit')<cr>
command -nargs=1 PlaylistLoad :call <SID>SendCommand('load ' . <q-args>)
" command PlaylistStart :call <SID>LaunchMiddleware()
