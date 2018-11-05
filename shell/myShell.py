#! /usr/bin/env python3

import os
import re
import sys

def pipe(arg):                                                      # Function to take care of the piping
    read, write = os.pipe()                                         # Create the read and write pipe
    fc = os.fork()                                                  # Fork a child off the child
    if fc == 0:
        os.close(1)                                                 # Redirect to the pipe's output
        write = os.dup(write)
        os.set_inheritable(write, True)                             # Set it to inheritable
        for dir in re.split(":", os.environ['PATH']):               # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, (arg[0], arg[1]), os.environ)    # try to exec program
            except FileNotFoundError:                               # ...expected
                pass
    else:
        os.close(0)                                                 # Redirect to the pipe's input
        read = os.dup(read)
        os.set_inheritable(read, True)                              # Set it to inheritable
        os.wait()                                                   # Wait for child to finish
        for dir in re.split(":", os.environ['PATH']):               # try each directory in the path
            program = "%s/%s" % (dir, args[2])
            try:
                os.execle(program, arg[2], os.environ)              # try to exec program
            except FileNotFoundError:                               # ...expected
                pass

def redirectTo(args):                                               # Function takes care of redirection '>'
    if len(args) > 2:                                               # Check if there is more commands after the redirection
        fc = os.fork()                                              # Fork a child if there is more commands
        if fc == 0:
            os.close(1)                                             # redirect child's stdout
            sys.stdout = open(args.pop(), "w")
            fd = sys.stdout.fileno()
            os.set_inheritable(fd, True)
            execute([args[0]])
        else:
            os.wait()                                               # Wait for the child to finish
    else:                                                           # If it is just the redirect command execute it
        os.close(1)                                                 # redirect child's stdout
        sys.stdout = open(args.pop(), "w")
        fd = sys.stdout.fileno()
        os.set_inheritable(fd, True)
        execute(args)                                               # Execute the command

def redirectFrom(args):                                             # Function takes care of redirection '<'
    if len(args) > 2:                                               # Check if there is more commands after the redirection
        fc = os.fork()                                              # Fork a child if there is more commands
        if fc == 0:
            os.close(0)                                             # redirect child's stdin
            sys.stdin = open(args[1], "r")
            fd = sys.stdin.fileno()
            os.set_inheritable(fd, True)
            execute(args[0:3])
        else:
            return                                                  # Do not wait for the child to finish
    else:                                                           # If it is just the redirect command execute it
        os.close(0)  # redirect child's stdin
        sys.stdin = open(args[1], "r")
        fd = sys.stdin.fileno()
        os.set_inheritable(fd, True)
        execute(args)                                               # Execute the command

def background(args):                                               # Function takes care if there is a command to run in the background
    if '<' in args:                                                 # If it is a redirect remove '<' form command
        args.remove('<')
        redirectFrom(args)

def sleep(args):                                                    # Function takes care if there is a sleep command
    fc = os.fork()                                                  # Fork a child
    if fc == 0:
        execute(args)                                               # Execute the command
    else:
        pass

def execute(args):                                                  # Function takes care of executing the commands
        for dir in re.split(":", os.environ['PATH']):               # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            try:
                if '/' in args[0]:
                    os.execve(args[0], args, os.environ)
                else:
                    os.execve(program, args, os.environ)            # try to exec program
            except FileNotFoundError:                               # ...expected
                pass

pid = os.getpid()
if "PS1" in os.environ:                                             # Take care of the 'PS1' variable
    pass
else:
    os.environ['PS1'] = "$"
e = os.environ
while 1:
    os.write(1, e.get('PS1').encode())                              # Print My 'PS1'
    command = os.read(0, 100).decode()                              # Wait for command to execute

    if not command:                                                 # Take care of the EOF
        sys.exit(0)

    args = command.split()                                          # Split the command into a list

    if len(args) == 0:                                              # If there is no command just loop to the beginning
        continue
    if args[0].lower() == 'exit':                                   # If user types exit end the program
        sys.exit(0)

    if len(args) > 1 and args[0] == args[1]:                        # If there is two of the same commands
        args.pop()
        rc = os.fork()

    if '&' in args:                                                 # If there is a command to run in the background
        if len(args) > args.index('&') + 1:                         # Check if there is more commands after the background one
            background(args[0:args.index('&') + 1])                 # Call background to take care of it
            args = args[args.index('&') + 1:]                       # Args is now everything after the background command

    rc = os.fork()                                                  # Fork the process

    if rc < 0:                                                      # Error forking child
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:                                                   # child
        if '|' in args:                                             # Check if it is a pipe
            args.remove('|')                                        # Remove the pipe from the list
            pipe(args)                                              # Call pipe function
        if '>' in args:                                             # Check to see if it is a redirect command
            args.remove('>')
            redirectTo(args)                                        # Call redirectTo
            args = args[2:]                                         # If there is more commands reassign args
        if '<' in args:                                             # Check to see if it is a redirect command
            args.remove('<')
            redirectFrom(args)                                      # Call redirectTo
            args = args[2:]                                         # If there is more commands reassign args
            if '&' in args:                                         # Make sure there is no background command
                args.remove('&')
        if 'sleep' in args and len(args) > 2:                       # Check if there is a sleep command
            sleep(args[:2])
            args = args[2:]

        if args[0].lower() == 'cd':                                 # Check if it is a 'cd' command
            if args[1] == '..':                                     # Check for '..'
                path = os.getcwd()                                  # Get the current directory
                last = path.rfind('/')                              # Find the last '/' in the string
                path = path[0:last]                                 # Remove everything after '/'
                os.chdir(path)                                      # Change the directory
            else:                                                   # If not '..' just change the directory to the specified path
                os.chdir(args[1])
            if len(args) > 2:                                       # Check if there is more commands after 'cd'
                args = args[2:]
                execute(args)
            else:
                sys.exit(0)

        execute(args)

        os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
        sys.exit(1)                                                 # terminate with error
    else:                                                           # parent (forked ok)
        childPidCode = os.wait()
