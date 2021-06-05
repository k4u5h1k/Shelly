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
import requests

try:
    script_loc = os.path.dirname(os.path.realpath(__file__))
except:
    # If run command is used to run this script
    # __file__ will cause error 'name not defined' to be raised
    script_loc = os.getcwd()

# Adding scripts to PYTHONPATH so everything 
# in scripts is directly importable
sys.path.insert(0, os.path.join(script_loc,'scripts'))

# Loading history file
histarray = []
histpath = os.path.join(script_loc,'.shelly_history')
if os.path.exists(histpath):
    with open(histpath,'r+') as f:
        for line in f:
            histarray.append(line.strip())
histfile = open(histpath, 'w+')

reset  = '\033[0m'
red    = '\033[31m'
green  = '\033[32m'
yellow = '\033[33m'
blue   = '\033[34m'
orange = '\033[35m'
cyan   = '\033[36m'
white  = '\033[29m'

# Persistent prompt colours across sessions
colourfile = os.path.join(script_loc,'.colours')
if os.path.exists(colourfile):
    with open(colourfile,'r+') as f:
       usercolour, dircolour, symbolcolour = f.readline().split()
else:
    usercolour = cyan
    dircolour = green
    symbolcolour = orange

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

# Show corresponding help message when command is help <function name>
usage = {
    'kedit'   : ("Our very own text editor\n"
                "Usage: kedit <filename> (optional: default='Untitled.txt')"),
    'cowsay'  : ("Make a cow say something!\n"
                "Usage: cowsay 'string' "),
    'grep'    : ("Search for a string in a file\n"
                "Usage: grep <filename> <string to search>"),
    'wc'      : ("Count the number of characters, words and lines in a file\n"
                 "Usage: wc <filename>"),
    'cd'      : ("Change current working directory\n"
                "Usage: cd path_to_directory (optional: default='~')"),
    'kopen'   : ("Open a file using the browser or a default app\n"
                "Usage: kopen <file>"),
    'play'    : ("Play a sound file\n"
                "Usage: play <file>"),
    'pwd'     : "Print current working directory",
    'whoami'  : "Print current user",
    'ls'      : "Print contents of current working directory",
    'clear'   : "Clear screen",
    'file'    : ("Identify file metadata\n"
                "Usage: file <filename>"),
    'touch'   : ("Create empty file\n"
                "Usage: touch <filename>"),
    'hash'    : ("Generate md5 hash of a file\n"
                "Usage: hash <filename>"),
    'rm'      : ("Remove a file or directory\n"
                "Usage: rm <path>"),
    'mkdir'   : ("Make directory\n"
                "Usage: mkdir <directory_name>"),
    'cat'     : ("Print contents of file to stdout\n"
                "Usage: cat <filename>"),
    'history' : "Print command history",
    'kill'    : ("kill a process\n"
                "Usage: kill <pid>"),
    'df'      : 'Print disk usage',
    'hostname': 'Print hostname of device',
    'echo'    : ("Print a string\n"
                "Usage: echo <string>"),
    'read'    : 'Print how your terminal interprets a key',
    'sleep'   : ("Sleep for a number of seconds\n"
                "Usage: sleep <time in seconds>"),
    'date'    : "Print current date in zsh format",
    'cp'      : ("Copy a file from source path to destination path\n"
                "Usage: cp <source> <destination>"),
    'mv'      : ("Move a file from source path to destination path\n"
                "Usage: mv <source> <destination>"),
    'find'    : ("Walk a file heirarchy\n"
                "Usage: find <start_dir> <to_find>"),
    'which'   : ("Locate a program file in the user's path\n"
                "Usage: which <cmd>"),
    'runpy'   : ("Run a python file\n"
                "Usage: runpy <python_file>"),
    'ex'      : ("Execute a shell binary/command\n"
                "Usage: ex <binary>"),
    'ip'      : "Print your private ip",
    'chat'    : "Chat with IRC",
    'colour'  : "Change prompt colour",
    'ping'    : ("Ping a url/ip\n"
                "Usage: ping <url/ip>"),
    'wget'    : ("Download a file from url\n"
                "Usage: wget <url>"),
    'help'    : "Display shelly help"
}

def kedit(path=None):
    try:
        from kedit import editFile
    except:
        print((f'{red}kedit.py was not found in scripts'
               f' directory, it will not work{reset}'))
        return

    editFile(path)

def cowsay(string=None):
    try:
        from cow import cow
    except:
        print((f'{red}cow.py was not found in scripts'
               f' directory, it will not work{reset}'))
        return

    if string is None:
        string = 'Give me something to say'
    else:
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
        
def wc(path=None):
    if path is None:
        print('Usage: wc <filename>')
    if os.path.isfile(path):
        count_c = 0
        count_l = 0
        count_w = 0
        with open(path) as handle:
            for line in handle:
                words = line.split(" ")
                count_c += len(line)
                count_l += 1
                count_w += len(words)
        print(f"Number of lines present in given file: {count_l}")
        print(f"Number of words present in given file: {count_w}")
        print(f"Number of characters present in given file: {count_c}")
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

def find(start=None, tofind=None):
    if (start is None or tofind is None) or not os.path.isdir(start):
        print('Usage: find <root directory> <file to search>')
    else:
        q = [start]
        found = False
        try:
            while len(q)!=0:
                try:
                    current = q.pop(0)
                    for item in os.listdir(current):
                        if re.match(tofind, item):
                            found = True
                            print(os.path.join(current,item))
                        if os.path.isdir(os.path.join(current, item)):
                            q.append(os.path.join(current, item))
                except Exception as err:
                    print('{red}err{reset}')
        except KeyboardInterrupt:
            return
        finally:
            if not found:
                print(f'{yellow}Could not find {tofind} within {start}{reset}')

def wget(url=None):
    if url is None:
        print("Usage: wget <url>")
    else:
        fname = os.path.basename(url)
        r = requests.get(url, stream=True)
        with open(fname, 'wb') as f:
            fprint(f"{green}Downloading file{reset}")
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
            clrline()
            print(f"{green}Done.{reset}")

def which(cmd=None):
    if cmd is None:
        print('Usage: which <cmd>')
    else:
        print(shutil.which(cmd))

def kopen(filename=None):
    if filename is None:
        print('Usage: fopen <path>')
    else:
        import webbrowser
        if os.path.exists(filename):
            webbrowser.open(f'file://{os.path.abspath(filename)}')
        else:
            print(f'{red}Invalid file path{reset}')

# def play(filename=None):
#     if filename is None:
#         print('Usage: play <path>')
#     else:
#         from playsound import playsound
#         if os.path.isfile(filename):
#             playsound(filename)
#         else:
#             print(f"{red}Not a valid file{reset}")

def pwd():
    print(os.getcwd())

def whoami():
    print(os.getenv(USER))

def ls(dirname=None):
    if dirname is None:
        dirname = os.curdir
    else:
        if dirname.startswith('~'):
            dirname = os.path.expanduser(dirname)

        elif os.path.isfile(dirname):
            print(f"{red}That is a file not directory {os.getenv(USER)}!{reset}")
            return

        elif not os.path.isdir(dirname):
            print(f"{red}{dirname} is not a valid directory!{reset}")
            return

    ls = os.listdir(dirname)
    ls_cols = 3
    good_length = (cols()//ls_cols)
    ls = list(((name[:good_length-2] + '..')\
            if len(name) > good_length else name) for name in ls)
    max_file_len = max(len(name) for name in ls) + 5

    # I want list in three columns (neat stonk)
    for counter, obj in enumerate(ls, 1):
        print(obj.ljust(good_length),end="")
        if counter%ls_cols==0 or counter == len(ls):
            print()
dir = ls

def clear():
    # Got this using clear | hexdump -C
    print("\x1b\x5b\x48\x1b\x5b\x32\x4a", end="")    
cls = clear

def file(filename=None):
    try:
        from identify import tags_from_path
    except:
        print((f'{red}identify.py was not found in scripts'
               f' directory, it will not work{reset}'))
        return

    if filename is None:
        print("Usage: file <filename>")
    else:
        if os.path.exists(filename):
            print(filename+':'+' '.join(sorted(tags_from_path(filename),
                key=lambda x:len(x))))
        else:
            print(f"{red}Not a valid file path!{reset}")

def hash(filename=None):
    if filename is None:
        print("Usage: hash <filename>")
    else:
        if os.path.isfile(filename):
            import hashlib
            h = hashlib.md5()

            # open file for reading in binary mode
            with open(filename,'rb') as file:
               # loop till the end of the file
               chunk = 0
               while chunk != b'':
                   # read only 1024 bytes at a time
                   chunk = file.read(1024)
                   h.update(chunk)

            print(h.hexdigest())
        else:
            print(f"{red}{filename} is not a valid file path!{reset}")

def touch(filename=None):
    if filename is None:
        print("Usage: touch <filename>")
    else:
        if not os.path.exists(filename):
            open(filename, 'a').close()
        else:
            print(f"{red}file already exists{reset}")

def rm(path=None):
    if path is None:
        print("Usage: rm <path>")
    else:
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                choice = input("Delete directory?(y/n) ")
                if choice=='' or choice.lower().startswith('y'):
                    shutil.rmtree(path)
        else:
            print(f"{red}Not a valid file/directory path!{reset}")
remove = rm

def mkdir(dirname=None):
    if dirname is None:
        print("Usage: mkdir <dirname>")
    else:
        if not os.path.isdir(dirname):
            os.mkdir(dirname)
        else:
            print(f"{red}Not a valid/available directory path!{reset}")

def cat(filename=None):
    if filename is None:
        print("Usage: cat <filename>")
    else:
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
    for counter, command in enumerate(histarray):
        print(f"{(str(counter+1)+'.').ljust(3)} {command.rstrip()}")

def kill(pid=None):
    if pid is None:
        print("{red}Usage: kill <pid>{reset}")
    else:
        import signal
        os.kill(pid, signal.SIGSTOP)

def df():
    st = os.statvfs("/")
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize

    print("Total: %d GiB"%(total//(2**30)))
    print("Used: %d GiB"%(used//(2**30)))
    print("Free: %d GiB" %(free//(2**30)))

def echo(toprint=None):
    if toprint==None:
        print('Usage: echo <string to print>')
    else:
        print(toprint)

def read():
    try:
        while True:
            print(str(readchar().encode())[2:-1])
    except KeyboardInterrupt:
        return

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

def mv(source=None, destination=None):
    if source==None or destination==None:
        print('Usage: mv <source> <destination>')
    elif os.path.exists(source):
        print(f'moving: {source} -> {destination}')
        shutil.move(source, destination)
    else:
        print(f'{red}One or both paths are invalid{reset}')

def runpy(filename=None,**kwargs):
    if filename==None:
        print('Usage: runpy <filename>')
    else:
        with open(filename, "rb") as source_file:
            code = compile(source_file.read(), filename, "exec")

        try:
            exec(code, kwargs)
        except KeyboardInterrupt:
            pass
        except Exception as err:
            print(f'{red}{err}{reset}')

def ex(command=None, *args):
    if command==None:
        print('Usage: ex <binary to execute>')
    else:
        import subprocess
        if os.path.isfile(command):
            os.chmod(command, 0o777)
            args = command

        else:
            args = [command] + list(args)

            for char in ['|', ';', '&&', '||', '=']:
                if char in ''.join(args):
                    print(f'{red}{char} not allowed.{reset}')
                    print(f'{red}cannot interpret special chars.{reset}')
                    return

        popen = subprocess.Popen(args)
        popen.wait()

def ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        print(f'{green}{s.getsockname()[0]}{reset}')
        s.close()
    except Exception as err:
        print(f'{red}Offline{reset}')

def ping(url=None):
    if url is None:
        print(f"{red}Usage: ping <url>{reset}")
    else:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            host = socket.getaddrinfo(url, 80)
            result = sock.connect_ex(host[-1][4])
            if result==0:
                print(f"{green}{url} is up{reset}")
        except Exception as err:
            if '[Errno 8]' in str(err):
                print(f"{red}{url} is down{reset}")
            else:
                print(f"{red}{err}{reset}")
        finally:
            sock.close()

def chat():
    client_path = os.path.join(script_loc, 'scripts', 'irc_client.py')
    if os.path.exists(client_path):
        runpy(client_path)
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
                "orange",
                "cyan"  ,
                "white" 
                ]

    toprint = "\n".join(list(f'{globals()[i]}{i}{reset}' \
            for i in available))

    print(f'Available colours: \n{toprint}')
    user = input('Username colour: ').lower()
    directory = input('Directory colour: ').lower()
    symbol = input('Prompt symbol colour: ').lower()
    if all(x in available for x in [user, directory, symbol]):
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
        help_cols = 4
        max_comm_len = cols()//help_cols
        print(f'{yellow}Available Commands:{reset}')

        # I want list in four columns (neat stonk)
        for counter, obj in enumerate(available, 1):
            print(obj.ljust(max_comm_len),end="")
            if counter%help_cols==0 or counter==len(available):
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

if 'readchar' in available:
    available.remove('readchar')

# Print to same line
fprint = lambda x: print(x,end='', flush=True)

# Clear the current line
cols = lambda : shutil.get_terminal_size().columns
clrline = lambda : fprint('\r'+' '*cols()+'\r')

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
        # Actual length of PS1+command to be printed after
        # removing colour codes
        printlen = len(command+re.sub(r'\x1b\[.+?m', '', PS1))

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
            tempcmd = green + command[:space] + reset + command[space:]
            toprint = PS1 + tempcmd
        # Otherwise just print it as is
        else:
            toprint = PS1 + command

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
                    if histcount > 0:
                        histcount -= 1
                        command = histarray[histcount]
                elif key_is(down):
                    if histcount < len(histarray)-1:
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
                    if cur_pos() > -1:
                        left[1] += 1
                if key_is(right[0]):
                    if cur_pos() < len(command):
                        right[1] += 1

        # If key is backspace remove character in front of cursor
        elif byte_char()==backspace:
            command = command[:cur_pos()-1] + command[cur_pos():]

        # Tab completion
        elif key_is(tab):
            command = command.replace('~',os.path.expanduser('~'))
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

                if len(possible_cmd) > 1:
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
                    if len(possible) > 0:
                        toprint = f'{red}Multiple possibilites{reset}'
                    else:
                        toprint = f'{red}No such file/directory{reset}'

                    clrline()
                    fprint(PS1+toprint)
                    time.sleep(0.7)

        elif actual_char() in string.printable:
            command = command[:cur_pos()] + actual_char() + command[cur_pos():]

def runShell():
    global histarray

    cwd = os.getcwd()

    # Replace home in prompt with '~'
    if cwd==os.path.expanduser('~'):
        dirname = '~'
    elif cwd=='/':
        dirname = '/'
    else:
        dirname = os.path.split(cwd)[-1]

    user = os.getenv(USER)
    PS1 = f"{usercolour}{user}{reset} {dircolour}{dirname}{reset} {symbolcolour}${reset} "

    # Take input command and add it to history
    command = take_input(PS1)
    command = command.replace('~', os.path.expanduser('~'))

    # Add command to history
    histarray.append(command)

    # Possible command types 
    # Python line
    # Shell Command
    # Invalid

    # if first word is valid function
    # then type is 2. Split and parse
    # command into valid function call
    split_com = shlex.split(command)
    if split_com[0] in available:
        args = ','.join(map(lambda x: "'"+x+"'", split_com[1:]))
        command = f'{split_com[0]}({args})'

    # If command is a directory cd to it
    elif os.path.isdir(command):
        cd(command)
        return
    # If command is file try to execute it
    elif os.path.isfile(command):
        ex(command)
        return

    # At this point either command is
    # a parsed shell command or Python
    # or invalid. 
    # So we can execute it now and if 
    # error occurs consider it invalid
    try:
        exec(command, globals(), globals())
    except Exception as err:
        print(f'{red}{err}{reset}')
        return

def main():
    try:
        while True:
            runShell()
    except KeyboardInterrupt:
        clrline()
        print(f"{red}Enter exit or quit to exit shell.{reset}")
        main()
    except Exception as err:
        print(f"{red}Error: {err}{reset}")
        main()
    finally:
        histfile.write('\n'.join(histarray)+'\n')
        histfile.close()

if __name__ == '__main__':
    main()
