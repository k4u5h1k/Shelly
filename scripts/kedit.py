#!/usr/bin/env python3
import os
import sys
import shutil
import string
from time import sleep
from copy import deepcopy

from readchar import readchar

iswin = sys.platform.startswith('win')
if iswin:
    # Must run this in windows for colour codes to work
    os.system('color')

def editFile(path=None):
    
    # Make Untitled.txt if there isn't a path
    if path is None:
        path = 'Untitled.txt'

    reset = '\033[0m'
    red = '\033[31m'
    green = '\033[32m'
    yellow = '\033[33m'
    blue = '\033[34m'
    purple = '\033[35m'
    cyan = '\033[36m'

    # Key codes - up is \1xb[A and only the last character is unique so just store that
    # Index 1 is cursor's direction count
    up = [b'A',0]
    down = [b'B',0]
    left = [b'D',0]
    right = [b'C',0]

    # Windows uses a different hex form backspace (use xxd -psg to confirm)
    backspace = b'\x7f' if not iswin else b'\x08'

    # If our file exists open it up and read it into towrite
    towrite = ''
    if os.path.isfile(path):
        with open(path,'r+') as f:
            towrite += f.read().rstrip()
    scroll = 0

    # Rows and Columns in our terminal window
    columns = shutil.get_terminal_size().columns
    termrows = shutil.get_terminal_size().lines-1

    clear_hex = "\x1b\x5b\x48\x1b\x5b\x32\x4a"

    # Print without newline
    fprint = lambda x: print(x,end="",flush=True)

    # Clear screen
    clr = lambda: fprint(clear_hex)

    # Print banner
    padding = ' '*((columns-8)//2) if columns>8 else ''
    print_banner = lambda: print(clear_hex+padding+"\x1b[30;31m"+'KEDIT V1'+"\x1b[0m"+padding)

    # Start print_banner
    welcome = [f'Editing {path}',
               f'Hit escape twice to save and exit',
               f'Any other key after escape to exit without saving',
               f'Press any key to continue']
    colors = [yellow,green,red,purple]
    print_banner()

    # This will hide the cursor
    fprint('\033[?25l')
    fprint('\n'*(termrows//2-2))
    for i in range(4):
        print(colors[i]+welcome[i].center(columns)+reset)
    readchar()
    # This will show cursor
    fprint('\033[?25h')

    while True:
        # print title print_banner
        print_banner()

        # print((f'up:{up[1]} down:{down[1]} '
        #        f'left:{left[1]} right:{right[1]} '
        #        f'rows:{termrows-1}  scroll:{scroll}/{(down[1]-up[1])-(termrows-1)}'))

        # All editing is done within a split array
        # joined in last line
        lines = towrite.split('\n')

        # Might need to scroll screen if file is long
        # we will calculate that later
        fprint('\n'.join(lines[scroll:termrows+scroll]))

        # Take cursor to top left of screen
        fprint('\x1b[2;1H')

        # Go to cursor's position by calculating effective y
        # and x from the top left and move by that much
        downcount = down[1]-up[1]
        rightcount = right[1]-left[1]
        fprint(f'\x1b[{down[0].decode("utf-8")}'*downcount)
        fprint(f'\x1b[{right[0].decode("utf-8")}'*rightcount)

        # Read a character
        char = readchar()

        # Windows readchar() returns byte and darwin returns string
        # So must have functions to interconvert
        byte_char = lambda: char if type(char)==bytes else char.encode()
        actual_char = lambda: char.decode('utf-8') if type(char)==bytes else char

        # Check if char is a specific byte
        key_is = lambda x: byte_char()==x

        linecount = len(lines)
        curs_row = lambda : down[1]-up[1]
        curs_col = lambda : right[1]-left[1]

        # If key is escape
        if key_is(b'\x1b'):
            char = readchar()
            # if next character is '[' it is probably an arrow key
            if key_is(b'['):
                char = readchar()
                if key_is(up[0]):
                    if curs_row()-1>=0:
                        up[1]+=1
                        if curs_col()>len(lines[curs_row()])-1:
                            right[1] = len(lines[curs_row()])
                            left[1] = 0;
                if key_is(down[0]):
                    if curs_row()+1<=linecount-1:
                        down[1]+=1
                        if curs_col()>len(lines[curs_row()])-1:
                            right[1] = len(lines[curs_row()])
                            left[1] = 0
                if key_is(right[0]):
                    if curs_col()<len(lines[curs_row()]):
                        right[1]+=1
                if key_is(left[0]):
                    if curs_col()-1>=0:
                        left[1]+=1

            # Pressing escape twice means save and exit
            elif key_is(b'\x1b'):
                write = True
                break

            # Pressing something after escape means exit without save
            else:
                write = False
                break

        # Otherwise this is probably a normal character
        else:
            # In windows pressing enter returns linefeed not newline -_-
            if actual_char()=='\r':
                char = '\n'

            # Lets edit the row we are in then reassign to line[curs_row()]
            toedit = lines[curs_row()]
            if actual_char() in string.printable:
                if char=='\t':
                    char = ' '*4
                toedit = toedit[:curs_col()]+actual_char()+toedit[curs_col():]
                lines[curs_row()] = toedit
                if actual_char()=='\n':
                    left[1] = 0
                    right[1] = 0
                    down[1] += 1
                else:
                    right[1]+=len(char)

            # If key is backspace remove the character before the cursor
            elif key_is(backspace):
                if curs_col()==0:
                    if not curs_row()==0:
                        right[1] = len(lines[curs_row()-1])
                        left[1] = 0
                        lines[curs_row()-1]+=toedit
                        lines.pop(curs_row())
                        up[1] += 1
                else:
                    toedit = toedit[:curs_col()-1]+toedit[curs_col():]
                    lines[curs_row()] = toedit
                    left[1]+=1

            towrite = '\n'.join(lines)

        # If our total lines is greater than terminal length 
        # we could need to scroll down if cursor is on the last line
        if linecount>termrows:
            check_scroll = (down[1]-up[1])-(termrows-1)
            if check_scroll>=0:
                scroll = check_scroll

    towrite = towrite.rstrip('\n')+'\n'


    clr()
    # Save and exit if write flag set if not exit
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
