if exists('g:loaded_playlist_global')
    finish
endif
let g:loaded_playlist_global=1

" Keep track of if we've launched the player middleware yet.  Don't worry
" about launching it multiple times (e.g. from sepearate vim instnaces), the
" middleware takes care of that with a lockfile
" Global mappings for interacting with the running player instance
if !exists('g:playlist_fifo_path')
    let g:playlist_fifo_path=$HOME . '/.vim/tmp/playlist_fifo'
endif

function! s:SendCommand(command_string)
    let l:command = 'echo ' . shellescape(a:command_string) . ' > ' . g:playlist_fifo_path
    echom l:command
    call system(l:command)
endfunction


noremap <Plug>(playlist-pause) :call <SID>SendCommand('pause')<cr>
noremap <Plug>(playlist-skip) :call <SID>SendCommand('skip')<cr>
command -nargs=1 PlaylistLoad :call <SID>SendCommand('load ' . <q-args>)
