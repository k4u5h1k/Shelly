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

    # Colours
    reset = '\033[0m'
    red = '\033[31m'
    green = '\033[32m'
    yellow = '\033[33m'
    blue = '\033[34m'
    purple = '\033[35m'
    cyan = '\033[36m'

    # Key codes - UP is \1xb[A and only 
    # the last character of each code 
    # is unique so just store that.
    # Index 1 is cursor's direction count
    up = [b'A',0]
    down = [b'B',0]
    left = [b'D',0]
    right = [b'C',0]

    # Windows uses a different hex form backspace 
    # (use xxd -psg in cmd to verify)
    backspace = b'\x08' if iswin else b'\x7f'

    # Rows and Columns in our terminal window
    cols = lambda: shutil.get_terminal_size().columns
    rows = lambda: shutil.get_terminal_size().lines-1

    clear_hex = "\x1b\x5b\x48\x1b\x5b\x32\x4a"

    # If our file exists open it up and read it into towrite
    if os.path.isfile(path):
        with open(path,'r+') as f:
            towrite = f.read().rstrip()
        lines = towrite.split('\n')
        for rownum,line in enumerate(lines):
            if len(line)>cols():
                lines[rownum:rownum+1] = line[:cols()], line[cols():]
        towrite = '\n'.join(lines)
    else:
        towrite = ''

    # Print without newline
    fprint = lambda x: print(x,end="",flush=True)

    # Clear screen
    clr = lambda: fprint(clear_hex)

    # Print banner
    padding = lambda: ' '*((cols()-8)//2) if cols()>8 else ''
    print_banner = lambda: print(clear_hex+padding()+"\x1b[30;31m"+'KEDIT V1'+"\x1b[0m"+padding())

    # Start print_banner
    welcome = [f'Editing {path}',
               f'Hit escape twice to save and exit',
               f'Any other key after escape to exit without saving',
               f'Press any key to continue']
    colors = [yellow,green,red,purple]
    print_banner()

    # This will hide the cursor
    fprint('\033[?25l')
    fprint('\n'*(rows()//2-2))
    for i in range(4):
        print(colors[i]+welcome[i].center(cols())+reset)
    readchar()
    # This will show cursor
    fprint('\033[?25h')

    while True:
        # print title print_banner
        print_banner()

        # print((f'up:{up[1]} down:{down[1]} '
        #        f'left:{left[1]} right:{right[1]} '
        #        f'rows:{rows()-1}  scroll:{scroll}/{(down[1]-up[1])-(rows()-1)}'))

        # All editing is done within a split array
        # joined in last line.
        lines = towrite.split('\n')

        # Split lines greater than term width.
        # This gets removed before writing.
        # Without this printing gets messed up.
        rownum = 0
        while rownum<len(lines):
            if len(lines[rownum])>cols():
                next_row_prefix = lines[rownum][cols():]
                lines[rownum] = lines[rownum][:cols()]
                try:
                    lines[rownum+1] = next_row_prefix + lines[rownum+1]
                except IndexError:
                    lines.append(next_row_prefix)
            rownum+=1

        # Might need to scroll screen if file is long
        scroll = max(0, (down[1]-up[1])-(rows()-1))

        # Print out file
        fprint('\n'.join(lines[scroll:rows()+scroll]))

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
                toedit = toedit[:curs_col()] + actual_char() + toedit[curs_col():]
                lines[curs_row()] = toedit

                if actual_char()=='\n':
                    left[1] = 0
                    right[1] = 0
                    down[1] += 1
                else:
                    right[1]+=len(char)

                # If cursor is at the last column when
                # character is entered move it to next line
                if curs_col()==cols()+1:
                    down[1] += 1
                    left[1] = 0
                    right[1] = 1

            # If key is backspace remove the 
            # character before the cursor
            elif key_is(backspace):

                # If cursor is at the first column when
                # character is backspaced move to previous line
                if curs_col()==0:
                    if not curs_row()==0:
                        right[1] = len(lines[curs_row()-1])
                        left[1] = 0
                        lines[curs_row()-1]+=toedit
                        lines.pop(curs_row())
                        up[1] += 1
                else:
                    toedit = toedit[:curs_col()-1]+toedit[curs_col():]
                    # if curs_row()!=len(lines)-1 and len(toedit)==cols()-1 \
                    #         and len(lines[curs_row()+1].strip())!=0:
                    #     lines[curs_row()] = toedit + lines[curs_row()+1][0]
                    #     lines[curs_row()+1] = lines[curs_row()+1][1:]
                    # else:
                    lines[curs_row()] = toedit
                    left[1]+=1

            towrite = '\n'.join(lines)


    temp = deepcopy(towrite)
    towrite = ''
    for line in temp.split('\n'):
        # If a line is longer than termwidth
        # next line is its continuation so 
        # dont add newline in between
        if len(line)>=cols():
            towrite+=line
        else:
            towrite+=line+'\n'

    clr()
    # Save and exit if write flag set if not exit
    if write:
        print(f"{green}Saving {path}{reset}")
        with open(path,'w+') as f:
            f.write(towrite)
    else:
        print(f"{red}Exiting without saving {path}{reset}")

if __name__=="__main__":
    path = sys.argv[1] if len(sys.argv)>1 else None
    editFile(path)
