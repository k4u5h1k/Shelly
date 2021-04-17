import sys
if sys.platform.startswith('win'):
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
if __name__=='__main__':
    while True:
        print(readchar().encode())
