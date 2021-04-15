#!/usr/bin/env python3
import os
import re
import sys
import time
import shlex
import shutil
import socket
import string
import platform

try:
    script_loc = os.path.dirname(os.path.realpath(__file__))
except:
    # If run command is used to run this file
    # __file__ will raise error as not defined
    script_loc = os.getcwd()

# Adding scripts to PYTHONPATH so everything in scripts is directly importable
sys.path.insert(0, os.path.join(script_loc,'scripts'))

# Loading history file
histarray = []
histpath = os.path.join(script_loc,'.shelly_history')
if os.path.exists(histpath):
    with open(histpath,'r+') as f:
        for line in f:
            histarray.append(line.strip())
histfile = open(histpath, 'a+')

iswin = sys.platform.startswith('win')
if iswin:
    import msvcrt
    win_encoding = "mbcs"
    XE0_OR_00 = "\x00\xe0"

    # Get a single character on Windows.
    def readchar(blocking=False):
        while msvcrt.kbhit():
            msvcrt.getch()
        ch = msvcrt.getch()
        # print('ch={}, type(ch)={}'.format(ch, type(ch)))
        # while ch.decode(win_encoding) in unicode('\x00\xe0', win_encoding):
        while ch.decode(win_encoding) in XE0_OR_00:
            # print('found x00 or xe0')
            msvcrt.getch()
            ch = msvcrt.getch()

        return ch if sys.version_info.major > 2 else ch.decode(encoding=win_encoding)

    # Username is stored in USERNAME env variable in windows
    USER = 'USERNAME'

    # This makes ansi escape codes work in cmd magically (O_O)
    os.system('color')

else:
    import termios
    import tty

    # Get a single character on Linux
    def readchar():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    # Username is stored in $USER env variable in windows
    USER = 'USER'

reset = '\033[0m'
red = '\033[31m'
green = '\033[32m'
yellow = '\033[33m'
blue = '\033[34m'
purple = '\033[35m'
cyan = '\033[36m'
white = '\033[29m'

# Show corresponding help message when command is help <function name>
usage = {
    'kedit': ("Our very own text editor\n"
                "Usage: kedit <filename>(optional: default='Untitled.txt')"),
    'cowsay': ("Make a cow say something!\n"
                "Usage: cowsay 'string' "),
    'grep': ("Search for a string in a file\n"
            "Usage: grep <filename> <string to search>"),
    'cd': ("Change current working directory\n"
            "Usage: cd path_to_directory(optional: default='~') "),
    'pwd': 'Print current working directory',
    'whoami': 'Print current user',
    'ls': 'Print contents of current working directory',
    'clear': 'Clear screen',
    'file': ("Identify file metadata\n"
            "Usage: file <filename>"),
    'touch': ("Create empty file\n"
            "Usage: touch <filename>"),
    'rm': ("Remove a file or directory\n"
            "Usage: rm <path>"),
    'mkdir': ("Make directory\n"
            "Usage: mkdir <directory_name>"),
    'cat': ("Print contents of file to stdout\n"
            "Usage: cat <filename>"),
    'history': 'Print command history',
    'kill': ("kill a process\n"
            "Usage: kill <pid>"),
    'df': 'Print disk usage',
    'hostname': 'Print hostname of device',
    'echo': ("Print a string\n"
            "Usage: echo <string>"),
    'sleep': ("Sleep for a number of seconds\n"
            "Usage: sleep <time in seconds>"),
    'date': 'Print current date in zsh format',
    'cp': ("Copy a file from source path to destination path\n"
            "Usage: cp <source> <destination>"),
    'mv': ("Move a file from source path to destination path\n"
            "Usage: mv <source> <destination>"),
    'find': ("Walk a file heirarchy\n"
            "Usage: find <start_dir> <to_find>"),
    'which': ("Locate a program file in the user's path\n"
            "Usage: which <cmd>"),
    'run': ("Run a python file\n"
            "Usage: run <python_file>"),
    'ip': 'Print your private ip',
    'chat': 'Chat with IRC',
    'color': 'Change prompt colour',
    'help': 'display pysh help'
}

def kedit(path=None):
    try:
        from kedit import editFile
    except:
        print(f'{red}kedit.py was not found in scripts \
                directory, it will not work{reset}')
        return

    editFile(path)

def cowsay(string=None):
    try:
        from cow import cow
    except:
        print(f'{red}cow.py was not found in scripts \
                directory, it will not work{reset}')
        return

    if string is None:
        string = 'Give me something to say'
    cow(string)

def grep(path=None, tosearch=None):
    if path is None or tosearch is None:
        print('Usage: grep <filename> <string to search>')
    if os.path.isfile(path):
        with open(path) as handle:
            for number, line in enumerate(handle):
                if tosearch in line:
                    print(f'{number}: {line.strip()}')
    else:
        print(f"{red}{path} is not a valid file!{reset}")

def cd(path=None):
    if path is None:
        cd(os.path.expanduser('~'))
    else:
        if os.path.isdir(path):
            os.chdir(path)
        else:
            if os.path.isfile(path):
                print(f"{red}That is a file not directory!{reset}")
            else:
                print(f"{red}{path} is not a valid directory!{reset}")

def find(start=None, tofind=None, firstcall=True):
    global found
    if start is None or tofind is None:
        print('Usage: find <start> <file to search>')
    else:
        if firstcall:
            found = False

        if not found:
            try:
                if os.path.isdir(start):
                    for item in os.listdir(start):
                        if re.match(tofind, item):
                            found = True
                            print(os.path.join(start,item))
                            return
                        if os.path.isdir(os.path.join(start, item)):
                            find(os.path.join(start, item),
                                tofind,
                                False)
                else:
                    print(f"{red}{start} is not a valid directory!{reset}")

            except KeyboardInterrupt:
                pass

def which(cmd=None):
    if cmd is None:
        print(f'Usage: which <cmd>')
    else:
        print(shutil.which(cmd))

def pwd():
    print(os.getcwd())

def whoami():
    print(os.getenv(USER))

def ls(dirname=None):
    ls = None

    if dirname is None:
        ls = os.listdir(os.curdir)
    else:
        if '~' in dirname:
            dirname = dirname.replace('~', os.path.expanduser('~'))

        if os.path.isdir(dirname):
            ls = os.listdir(dirname)
        elif os.path.isfile(dirname):
            print(f"{red}That is a file not directory {os.getenv(USER)}!{reset}")
        else:
            print(f"{red}{dirname} is not a valid directory!{reset}")

    if ls is not None and len(ls)>0:
        ls_cols = 3
        good_length = (cols()//ls_cols)-ls_cols
        ls = list(((name[:good_length-2] + '..')\
                if len(name) > good_length else name) for name in ls)
        max_file_len = max(len(name) for name in ls) + 5

        # I want list in three columns (neat stonk)
        counter = 0
        ls_cols = 3
        for obj in ls:
            print(obj.ljust(good_length+1),end="")
            counter+=1
            if counter%ls_cols==0 or counter == len(ls):
                print()
dir = ls

def clear():
    # Got this using clear | hexdump -C
    print("\x1b\x5b\x48\x1b\x5b\x32\x4a", end="")    
cls = clear

def file(filename):
    try:
        from identify import tags_from_path
    except:
        print(f'{red}identify.py was not found in \
                scripts directory, it will not work{reset}')

    if os.path.exists(filename):
        print(filename+':'+' '.join(sorted(tags_from_path(filename),
            key=lambda x:len(x))))
    else:
        print(f"{red}Not a valid file path!{reset}")

def touch(filename):
    if not os.path.exists(filename):
        open(filename, 'a').close()
    else:
        print(f"{red}file already exists{reset}")

def rm(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            choice = input("Delete directory?(y/n) ")
            if choice=='' or choice.lower().startswith('y'):
                shutil.rmtree(path)
    else:
        print(f"{red}Not a valid file path!{reset}")
remove = rm

def mkdir(path):
    if not os.path.isdir(path):
        os.mkdir(path)
    else:
        print(f"{red}Not a valid/free directory path!{reset}")

def cat(filename):
    if os.path.isfile(filename):
        with open(filename) as handle:
            for line in handle:
                print(line.rstrip())
    else:
        if os.path.isdir(filename):
            print(f"{red}{filename} is a directory not file!{reset}")
        else:
            print(f"{red}File does not exist!{reset}")

def history():
    histfile.seek(0)
    lines = histfile.readlines()
    for counter,command in enumerate(lines):
        print(f"{(str(counter+1)+'.').ljust(3)} {command.rstrip()}")

def kill(pid):
    import signal
    os.kill(pid, signal.SIGSTOP)

def df():
    st = os.statvfs("/")
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize

    print("Total: %d GiB" % (total // (2**30)))
    print("Used: %d GiB" % (used // (2**30)))
    print("Free: %d GiB" % (free // (2**30)))

def echo(toprint=None):
    if toprint==None:
        print('Usage: echo <string to print>')
    else:
        print(toprint)

def sleep(secs=None):
    if secs==None:
        print('Usage: sleep <seconds>')
    else:
        time.sleep(secs)

def hostname():
    print(socket.gethostname())

def date():
    from datetime import datetime
    print(datetime.now().strftime("%a %b %d %H:%M:%S %Y"))

def cp(source=None, destination=None):
    if source==None or destination==None:
        print('Usage: cp <source> <destination>')
    elif os.path.isfile(source):
        print(f'copying file: {source} -> {destination}')
        shutil.copy(source, destination)

def mv(source, destination):
    if source==None or destination==None:
        print('Usage: mv <source> <destination>')
    elif os.path.exists(source):
        print(f'moving file: {source} -> {destination}')
        shutil.move(source, destination)
    else:
        print(f'{red}One or both paths are invalid{reset}')

def run(filename=None,**kwargs):
    if filename==None:
        print('Usage: run <filename>')
    else:
        with open(filename, "rb") as source_file:
            code = compile(source_file.read(), filename, "exec")
        try:
            pid = os.fork()
            if pid:
                os.wait()
            else:
                exec(code, kwargs)
        except Exception as err:
            print(f'{red}{err}{reset}')
            return

def ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        print(green+s.getsockname()[0]+reset)
        s.close()
    except Exception as err:
        print(f'{red}Offline{reset}')

def chat():
    client_path = os.path.join(script_loc,'scripts','irc_client.py')
    if os.path.exists(client_path):
        run(client_path)
    else:
        print("{red} Please place irc_client.py is \
                scripts directory to access chat {reset}")

def colour():
    global usercolour, dircolour, symbolcolour
    available = [ 
                "red"   ,
                "green" ,
                "yellow",
                "blue"  ,
                "purple",
                "cyan"  ,
                "white" 
                ]

    toprint = "\n".join(
            list(f'{globals()[i]}{i}{reset}' for i in available))

    print(f'Available colours: \n{toprint}')
    user = input('Username colour: ').lower()
    directory = input('Directory colour: ').lower()
    symbol = input('Prompt symbol colour: ').lower()
    if user in available and directory in available and symbol in available:
        # Another way to saying access colour from 
        # global variable which user input
        usercolour = globals()[user]
        dircolour = globals()[directory]
        symbolcolour = globals()[symbol]

        # Write colours into a file for next time
        with open(colourfile,'w+') as f:
            f.write(f'{usercolour} {dircolour} {symbolcolour}')
    else:
        print(f'{red}One of more inputs were invalid!{reset}')
    
def exit():
    sys.exit()
quit = exit

def help(func=None):
    if func is None:
        global available
        # max_comm_len = max(len(func) for func in available) + 5
        max_comm_len = cols()//4-4
        print(f'{yellow}Available Commands:{reset}')

        # I want list in four columns (neat stonk)
        counter = 0
        for obj in available:
            print(obj.ljust(max_comm_len),end="")
            counter+=1
            if counter%4==0 or counter==len(available):
                print()
        print(f'{yellow}+ Any python3 one-liner {reset}')
        print(f'{yellow}Use help <command> for help on specific commands{reset}')
    else:
        if usage.get(func) is None:
            print(f'{red}Help on {func} is not available {reset}')
        else:
            print(usage.get(func))

# =====================================
# DEFINE YOUR FUNCTIONS ABOVE THIS LINE.
# IF YOU DEFINE COMMANDS BELOW THEY WILL
# NOT BE CONSIDERED.

# This will make available = ['cd', 'pwd', ... with all functions above next line]
available = []
local_locals = list(locals().items()).copy()
for key, value in local_locals:
    if callable(value) and value.__module__==__name__:
        available.append(key)

# Print to same line
fprint = lambda x: print(x,end='',flush=True)

# Clear the current line
cols = lambda : shutil.get_terminal_size().columns
clrline = lambda : fprint('\r'+' '*cols()+'\r')

# Persistent prompt colours across sessions
colourfile = os.path.join(script_loc,'.colours')
if os.path.exists(colourfile):
    with open(colourfile,'r+') as f:
       usercolour, dircolour, symbolcolour = f.readline().split()
else:
    usercolour = cyan
    dircolour = green
    symbolcolour = purple

def take_input(PS1):
    backspace = b'\x7f' if not iswin else b'\x08'
    tab = b'\t'
    up = b'A'
    down = b'B'
    left = [b'D',0]
    right = [b'C',0]
    
    command = ''
    histcount = len(histarray)
    prevlen = 0

    # Cursor position is length of command minus effective
    # cursor left movement
    cur_pos = lambda: (len(command))-(left[1]-right[1])

    # We take input while True and stop when newline is
    # entered
    while True:
        printlen = len(command+re.sub(r'\x1b\[.+?m','',PS1))
        # If command is wider than terminal width you must move up
        # a little before printing
        for _ in range(prevlen//(cols()+1)):
            clrline()
            # Moving up
            fprint('\x1b[A')

        # Clear line and print prompt with command
        clrline()

        space = command.index(' ') if ' ' in command else len(command)

        isexit = command=='quit' or command=='exit'

        # If the first word of command is a 
        # valid function colour it green
        if len(command.strip())!=0 and \
                (command.split()[0] in available or isexit):
            tempcmd = green+command[:space]+reset+command[space:]
            toprint = PS1+tempcmd
        # Otherwise just print it as is
        else:
            toprint = PS1+command

        fprint(toprint)
        prevlen = printlen

        # After printing cursor is at the end of current line
        # So we must move cursor it to its last known position
        for lr in [left,right]:
            fprint(f'\x1b[{lr[0].decode("utf-8")}'*lr[1])

        # Read a character
        char = readchar()

        # Windows readchar() returns byte and darwin returns string
        # So must have functions to interconvert
        byte_char = lambda: char if type(char)==bytes else char.encode()
        actual_char = lambda: char.decode('utf-8') if type(char)==bytes else char
        key_is = lambda x: byte_char()==x

        # In windows pressing enter returns linefeed not newline -_-
        if actual_char()=='\n' or actual_char()=='\r':
            if len(command)==0:
                continue
            print()
            return command

        # If key is escape
        elif key_is(b'\x1b'):
            char = readchar()
            # if next character is '[' it is probably an arrow key
            if key_is(b'['):
                char = readchar()

                # If key is up or down we scroll through
                # history
                if key_is(up):
                    if histcount>0:
                        histcount -= 1
                        command = histarray[histcount]
                elif key_is(down):
                    if histcount<len(histarray)-1:
                        histcount += 1
                        command = histarray[histcount]
                    else:
                        histcount = len(histarray)
                        command = ''

                if key_is(up) or key_is(down):
                    left[1] = 0
                    right[1] = 0

                # If key is left or right we take the 
                # cursor left or right
                if key_is(left[0]):
                    if cur_pos()>-1:
                        left[1] += 1
                if key_is(right[0]):
                    if cur_pos()<len(command):
                        right[1] += 1

        # If key is backspace remove character in front of cursor
        elif byte_char()==backspace:
            command = command[:cur_pos()-1]+command[cur_pos():]

        # Tab completion
        elif key_is(tab):
            command_split = shlex.split(command)
            if len(command_split)==0:
                continue
            # Last element of shlex.split has to be path to complete
            tocomplete = command_split[-1]
            possible = []
            possible_cmd = []

            # If first word i.e command is tabbed
            # we must find the complete command and print
            if len(command_split)==1:
                for func in available:
                    if func.startswith(tocomplete):
                        possible_cmd.append(func)
                if len(possible_cmd)==1:
                    command = possible_cmd[0]

                if len(possible_cmd)>1:
                    toprint = f'{red}Multiple possible commands{reset}'
                    clrline()
                    fprint(PS1+toprint)
                    time.sleep(0.7)

            # Get directory to search in if there is a separator in path
            # else use the current directory
            if os.sep in tocomplete:
                index = tocomplete.rindex(os.sep)
                directory = tocomplete[:index]
                tocomplete = tocomplete[index+1:]
            else:
                directory = os.curdir


            # If no such command exists then
            # tocomplete can only be a file/directory
            if len(possible_cmd)==0:
                for name in os.listdir(directory):
                    if name.lower().startswith(tocomplete.lower()):
                        possible.append(name)
                if len(possible)==1:
                    complete = re.sub(r' ','\ ',possible[0])
                    command_split[-1] = f"{directory+os.sep+complete}"
                    command = ' '.join(command_split)

                # If multiple completion possibilities just tell the user
                else:
                    if len(possible)>0:
                        toprint = f'{red}Multiple possibilites{reset}'
                    else:
                        toprint = f'{red}No such file/directory{reset}'

                    clrline()
                    fprint(PS1+toprint)
                    time.sleep(0.7)

        elif actual_char() in string.printable:
            command = command[:cur_pos()]+actual_char()+command[cur_pos():]

def runShell():
    cwd = os.getcwd()

    # Replace home in prompt with '~'
    if cwd == os.path.expanduser('~'):
        dirname = '~'
    else:
        if cwd == '/':
            dirname = '/'
        else:
            dirname = os.path.split(cwd)[-1]

    user = os.getenv(USER)
    PS1 = f"{usercolour}{user}{reset} {dircolour}{dirname}{reset} {symbolcolour}${reset} "

    # Take input command and add it to history
    command = take_input(PS1)
    command_copy = command

    # If command is a directory cd to it
    if os.path.isdir(command):
        cd(command)
        return

    '''
    Possible command types 
    1. Python line
    2: Shell Command
    3: Invalid
    '''

    # Now split the user input and run 
    # it through our parsing routine
    # if first word is valid function
    split_com = shlex.split(command)
    if split_com[0] in available:
        command_type = 2

        # Parse through command and add '(', ',', ')' and '"' 
        # wherever needed to create valid python function call string
        start_with_quote = lambda word: word.startswith("'")\
                or word.startswith('"')
        end_with_quote = lambda word: word.endswith("'") or \
                word.endswith('"')
        sawQuote = False
        for i in range(1,len(split_com)):
            word = split_com[i]

            if not sawQuote and not \
                    (start_with_quote(word) or end_with_quote(word)):
                split_com[i]="'"+split_com[i]+"'"
                word = split_com[i]

            elif start_with_quote(word):
                sawQuote=True

            if end_with_quote(word) and i!=len(split_com)-2:
                split_com[i]+=","
                sawQuote = False
            
        args = ','.join(split_com[1:])
        command = f'{split_com[0]}({args})'

    else:
        # Dont print anything here onwards to stdout
        # to suppress whatever bs exec prints
        old_stdout = sys.stdout
        sys.stdout = None 

        try:
            if exec(command) is None:
                command_type = 1

        # If error occurs it is invalid so type 3
        except:
            command_type = 3

        # Resume printing to stdout
        sys.stdout = old_stdout

    if command_type==3:
        print(f"{red}Invalid command {user}!{reset}")
        return
    else:
        try:
            exec(command,globals(),locals())
        except Exception as err:
            command_type = 3
            print(f'{red}{err}{reset}')

    # Add command to history if it is not invalid
    if command_type!=3:
        histfile.write(command_copy+'\n')
        histarray.append(command_copy)


if __name__ == '__main__':
    try:
        while True:
            runShell()

    except (KeyboardInterrupt, ValueError):
        clrline()
    except Exception as err:
        clrline()
        print(f'{red}{err}{reset}')
        print(yellow+"Error Occured, Exiting."+reset)
    finally:
        histfile.close()
