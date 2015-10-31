" Global mappings for interacting with the running player instance
if !exists('g:playlist_fifo_path')
    let g:playlist_fifo_path=$HOME . '/.vim/tmp/playlist_fifo'
endif

function! s:SendCommand(command_string)
    let l:command = 'echo ' . shellescape(a:command_string) . ' > ' . g:playlist_fifo_path
    echom l:command
    call system(l:command)
endfunction


nnoremap <Plug>(playlist-pause) :call <SID>SendCommand('pause')<cr>
nnoremap <Plug>(playlist-skip) :call <SID>SendCommand('skip')<cr>
