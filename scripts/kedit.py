#!/usr/bin/env python3
import os
import sys
import shutil
import string
from time import sleep
from copy import deepcopy

if not __name__=='__main__':
    from scripts.readchar import readchar
else:
    from readchar import readchar

def editFile(path=None):
    if path is None:
        path = 'Untitled.txt'

    reset = '\033[0m'
    red = '\033[31m'
    green = '\033[32m'
    yellow = '\033[33m'
    blue = '\033[34m'
    purple = '\033[35m'
    cyan = '\033[36m'

    columns = shutil.get_terminal_size().columns
    center_row = (shutil.get_terminal_size().lines-1)//2
    up = [b'A',0]
    down = [b'B',0]
    left = [b'D',0]
    right = [b'C',0]
    backspace = b'\x7f'

    towrite = ''
    prev_towrite = ''
    if os.path.isfile(path):
        with open(path,'r+') as f:
            towrite += f.read().rstrip()

    # curs_row = curs_col = lambda : 1
    # rows=0

    write = False
    clear_hex = "\x1b\x5b\x48\x1b\x5b\x32\x4a"
    fprint = lambda x: print(x,end="",flush=True)
    clr = lambda: fprint(clear_hex)
    banner = lambda: print(clear_hex+"\x1b[30;37m"+'KEDIT V1'.center(columns)+"\x1b[0m")

    welcome = [f'Editing {path}',
               f'Hit escape twice to save and exit',
               f'Any other key after escape to exit without saving',
               f'Press any key to continue']
    colors = [yellow,green,red,purple]
    clr()
    banner()
    fprint('\033[?25l')
    fprint('\n'*(center_row-2))
    for i in range(4):
        print(colors[i]+welcome[i].center(columns)+reset)
    readchar.readchar()
    fprint('\033[?25h')

    try:
        while True:
            banner()
            fprint(towrite)

            upcount = up[1]-down[1]
            fprint(f'\x1b[{up[0].decode("utf-8")}'*upcount)

            leftcount = left[1]-right[1]
            if leftcount>=0:
                fprint(f'\x1b[{left[0].decode("utf-8")}'*leftcount)
            else:
                fprint(f'\x1b[{right[0].decode("utf-8")}'*-leftcount)

            char = readchar.readchar()
            key_is = lambda x: char.encode()==x
            temp = towrite.split('\n')
            rows = len(temp)-1
            curs_row = lambda : rows-up[1]+down[1]
            curs_col = lambda : len(temp[-1])-1-left[1]+right[1]

            if key_is(b'\x1b'):
                char = readchar.readchar()
                if key_is(b'['):
                    char = readchar.readchar()
                    if key_is(up[0]):
                        if curs_row()-1>=0:
                            up[1]+=1
                            if curs_col()>len(temp[curs_row()])-1:
                                left[1] = len(temp[-1])-len(temp[curs_row()])
                                right[1] = 0;
                    if key_is(down[0]):
                        if curs_row()+1<=rows:
                            down[1]+=1
                            if curs_col()>len(temp[curs_row()])-1:
                                left[1] = len(temp[-1])
                                right[1] = 0;
                    if key_is(right[0]):
                        if curs_col()+1<len(temp[curs_row()]):
                            right[1]+=1
                    if key_is(left[0]):
                        if curs_col()-1>=-1:
                            left[1]+=1
                elif key_is(b'\x1b'):
                    write = True
                    break
                else:
                    write = False
                    break

            else:
                toedit = temp[curs_row()]
                if char in string.printable:
                    toedit = toedit[:curs_col()+1]+char+toedit[curs_col()+1:]
                    temp[curs_row()] = toedit
                    if char=='\n':
                        if curs_row() == rows:
                            left[1] = len(toedit[curs_col():])-1
                        else:
                            left[1] = len(temp[-1])
                        right[1] = 0
                    elif curs_row()!=len(temp)-1:
                            right[1]+=1

                elif key_is(backspace):
                    if curs_col()==-1:
                        if not curs_row()==0:
                            temp[curs_row()-1]+=toedit
                            temp.pop(curs_row())
                    else:
                        toedit = toedit[:curs_col()]+toedit[curs_col()+1:]
                        temp[curs_row()] = toedit
                        if curs_row()!=rows:
                            left[1]+=1

                towrite = '\n'.join(temp)

    except:
        pass

    finally:
        towrite = towrite.rstrip('\n')+'\n'


    clr()
    if write:
        print(f"{green}Saving {path}{reset}")
        with open(path,'w+') as f:
            f.write(towrite)
    else:
        print(f"{red}Exiting without saving {path}{reset}")
        exit

if __name__=="__main__":
    path = sys.argv[1] if len(sys.argv)>1 else None
    editFile(path)
