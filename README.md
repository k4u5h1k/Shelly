# Shelly
A no external dependancy bash-like python REPL with realtime IRC chat and custom text editor.

# Usage 
clone this repo and run `python3 shell.py`.

# Screenshots  

## Shell
![Screenshot 2021-03-14 at 12 19 55 PM](https://user-images.githubusercontent.com/59250093/111059975-99452e80-84bf-11eb-9167-5259123c8a58.png)

## Chat
![Screenshot 2021-03-14 at 12 25 16 PM](https://user-images.githubusercontent.com/59250093/111060071-59327b80-84c0-11eb-8ee7-e70119377da6.png)

## Editor
![Screenshot 2021-03-14 at 12 28 07 PM](https://user-images.githubusercontent.com/59250093/111060136-bd553f80-84c0-11eb-902f-5f4986d4f018.png)
![Screenshot 2021-03-14 at 12 28 27 PM](https://user-images.githubusercontent.com/59250093/111060146-c9410180-84c0-11eb-9fe3-8b10aeb4da98.png)



# Features
- All basic shell commands.
- Python code interpretation.
- Coloured prompt and error messages.
- Tab completion.
- Custom text editor - kedit.
- IRC chat.
- Command specific help messages
- no external dependancies (handwritten python all the way).

# TODO
- Pipe support.
- Redirect operator implementation. 
- sudo support. 
- chmod support. 
- Autojump support. 
- remote command execution (with consent) via IRC.  
- add support for running external binaries. 

# DEVELOPMENT
To add your own commands simply define them as a function above the `DEFINE YOUR FUNCTION ABOVE THIS LINE` line.

# CREDITS
- scripts/cow.py customized from https://github.com/VaasuDevanS/cowsay-python.
- readchar from https://github.com/magmax/python-readchar.
