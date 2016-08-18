#!/usr/bin/env python
"""
Author: Ang Wei Xiang Darren (P1444588) & Neo Ken Hong, Kelvin (P1529179)
Class: DISM/FT/2A/02
Task: 3 (Admin Client)
Chat client based on Mr Karl Kawn's GUI Chat Client
See below for existing comments
"""
# Author : Karl Kwan
# Date: July 2016
# Source : simChatClient.v.1.py
#
# Objective: sample program for AY20162017S1 - ST2512 assignment2.
#               This program works with a co-responding multi-user chat server
#
# This program uses Tkinter (conventional python gui module) to support the
# gui interface requirement.
# gui programming in Python is not part of ST2512 scope.
# Students are not required to implement their solution using gui.

import sys
import socket
import threading
from Tkinter import *
from ScrolledText import ScrolledText

root = None
def getnewsocket():
        # short function to save typing effort only.
	return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def monitor(con):
    #Assumming the connection of the 'con' is ok and has been connected to the
    #chat server
    #
    # This function will be started in an independent thread
    #   It monitors the connected socket for any incoming messages for display.
    #   It works indefinitely until the socket is broken.
    #   set the con to blocking mode.
    #   The recv() needs a timeout, as the broken exception only reports to the
    #   program at the initial invocation time of the recv(). Thus, we need to
    #   restart the recv() every 3 seconds, to capture such exception.
    con.setblocking(True)
    con.settimeout(3.0)
    while True:
        try:
                buf = con.recv(255)
                if len(buf) > 0:
                        displayT.configure(state="normal")
                        displayT.insert(END,buf)
                        displayT.see(END) # simulate autoscroll
                        displayT.configure(state="disabled")
                else:
                        break
        except Exception as inst:
                if str(inst) != "timed out":
                    break
                #The connection may be dropped
                #else , this is only a normal time out exception.
                #the while loop will be continued, and retry to call recv()
    print "connection is closed"
    # calling quit() to stop the tkinter window (in case, it is still running)
    quit(None)
 
def quit(event):
    if clientsocket:
        # after the socket is closed. the monitor function will be receiving a
        # socket closed exception and exit.
        clientsocket.close()
    try:
        root.destroy()
    except:
        pass # in case the root has been destroyed already
    sys.exit()

def sendmsg(event):
    contents = inputT.get(1.0, END).strip()
    #1.0 refer to 1st line, 0th col
    if contents:
        try:     
            clientsocket.sendall(contents+'\n')
            history.append(contents)
            # set index to global to update the value
            global index
            index = len(history)
        except:
            quit(None)
    # delete the current input from the textbox. (from 1st char to the end)        
    inputT.delete(1.0,END)
##  #set cursor back to row 1, col 0
    inputT.see(1.0)
    
def inputKeyup(event):
    if len(event.char)<1: #ignore 'shift, crtl ... key release
        return
    val = ord(event.char)
    if val==13:   # detected an enter key
        sendmsg(None)

# For up arrow key
def upKey(event):
    """ The function fires when the UP key is pressed

    Args:
            event: The event that caused the key to be pressed
    """
    # set index to global to update the value
    global index    
    if history:
            inputT.delete(1.0,END)
            try:
                    # to prevent the index from going negative
                    if index > 0:
                            index = index - 1
                    inputT.insert(1.0, history[index])
            except IndexError:
                    pass

# For down arrow key
def downKey(event):
        """ The function fires when the DOWN key is pressed

        Args:
                event: The event that caused the key to be pressed
        """
        # set index to global to update the value
        global index
        if history:
                inputT.delete(1.0,END)
                try:
                        # to prevent the index from going over length of history
                        if index < len(history):
                                index = index + 1
                        inputT.insert(1.0, history[index])       
                except IndexError:
                        pass
        
#main program starts here
if len(sys.argv)<2:
    print "Usage: ",sys.argv[0]," server_ip"
    # program still proceeds, using the following two default settings.
    host = 'localhost'
else:     
    host = sys.argv[1]

try:
    clientsocket = getnewsocket()
    clientsocket.connect((host, 8888))
except:
    print "Connection Failed. Please try again later"
    sys.exit()
# starting a separate thread to monitor and display incoming message from
# chat server
t = threading.Thread(target=monitor, args=(clientsocket,)) 
t.start()

# The following is the gui programming part to create a
# window to display the incoming messages, and accept user input to send to
# chat server
root = Tk()
root.title("Admin Chat Client v.0.1")

# For history commands
history = []
index = 0

# Display textbox (15 rows by 80 columns) 
displayT = ScrolledText(root, height=15, width=80)
displayT.insert(END, "")
displayT.configure(state="disabled")
displayT.pack()

# User input textbox (at the lower part of the window, only 2 rows x 80 column)
inputT = Text(root, height=2, width=80, bg='#00BFFF')
inputT.insert(END, "")
inputT.bind('<KeyRelease>', inputKeyup)
# Bind the UP and DOWN key to the functions upKey() and downKey() respectively
inputT.bind('<Up>', upKey)
inputT.bind('<Down>', downKey)

inputT.pack(side=LEFT)
sendbutton = Button(root,text="Send")
sendbutton.bind('<Button-1>',sendmsg)
sendbutton.pack()
quitbutton = Button(root,text="Quit")
quitbutton.bind('<Button-1>',quit)
quitbutton.pack()
inputT.focus_set() # ensure focus on the input textbox
# mainloop() is required to start the window activities.
mainloop()
