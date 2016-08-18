#!/usr/bin/env python
"""
Author: Ang Wei Xiang Darren (P1444588) & Neo Ken Hong, Kelvin (P1529179)
Class: DISM/FT/2A/02
Task: 3 (Server)
Asynchronous chat server based on Mr Karl Kwan's sample async echo server.
Required ports to be freed: 8089 and 8888
~ original source - http://ilab.cs.byu.edu/python/select/echoserver.html
""" 
import select 
import socket 
import sys
import time
import re

def safeRecv(con,size):
        """Safely handle the input coming in from the user.

        Args:
                con: The connection socket the user is using
                size: The size of the data coming in
        Returns:
                The buffer data the user has sent.
        
        """
        try:
                buf=con.recv(size)
        except:
                buf= ""
        return buf

def serverPrompt():
        """Prints out the server prompt message"""
        print """
        Connect to port 8089 as user client
        Connect to port 8888 as admin client
        """

def sendAllSockets(sockets, msg):
        """Sends a message to all the sockets specified by the argument

        Args:
                sockets: The sockets to send the message to
                msg: The message to send to the sockets
        """
        for socket in sockets:
                socket.sendall(msg)

def findUserName(userdict, socket_address_dict, nickname):
        """Finds the sockets associated to a nickname

        Args:
                userdict: The dictionary that contains the key value pair of ((IP Address, Port), Nickname)
                socket_address_dict: The dictonary that contains the key value pair of (Client Socket, (IP Address, Port))
                nickname: The nickname to search from the dictionaries

        Returns:
                The list of client sockets that uses the nickname specified in the argument
        """
        for address, name in userdict.items():
                if name == nickname:
                        for client, address2 in socket_address_dict.items():
                                if address2 == address:
                                        yield client
                
def findUserIP(socket_address_dict, iptuple):
        """Finds the sockets associated to an IP address and, if specified, a port number

        Args:
                socket_address_dict: The dictonary that contains the key value pair of (Client Socket, (IP Address, Port))
                iptuple: The sequence of IP address and, if specified, a port number

        Returns:
                The list of client sockets associated to an IP address and, if specified, a port number
        """
        for client, address in socket_address_dict.items():
                if address[0] == ipaddr[0]:
                        if len(ipaddr) == 1 or str(address[1]) == ipaddr[1]:
                                yield client


host = '0.0.0.0' # listen on any interface
helpmsg = """
List of admin commands:

/help: Show this help message
/list: Lists all connected users.
/msg-name [name] [message]: Private message a specific user via nickname.
/msg-ip [ip[:port]] [message]: Private message a specific user via IP address and, if specified, port number.
/kick-name [name]: Kick a user via nickname
/kick-ip [ip[:port]]: Kick a user via IP address and, if specified, port number.
/stop: Stops the chat server

To broadcast a message, just send a message.
"""
port = 8089
adminport = 8888
backlog = 5 
size = 1024
# Bind the user client port
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((host,port)) 
server.listen(backlog)
# Bind the admin client port
adminserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
adminserver.bind((host,adminport)) 
adminserver.listen(backlog)

input = [server, adminserver]
user_dict = {}
usersocket_addr_dict = {}
admin_list = []
# define a input list, and set the initial input sources
running = 1 
serverPrompt()
while running: 
        # using select.select to obtain the latest ready lists
        inputready,outputready,exceptready = select.select(input,[],[]) 
        for s in inputready: 
                if s == server: 
                        # handle the client connection socket 
                        client, address = server.accept()
                        print "accepted a new client from"+str(address) 
                        input.append(client)
                        #assign a default name to user that connects since username is unknown when first connect
                        user_dict[address] = 'unnamed'
                        #This is to resolve the problem of not being able to find the address
                        usersocket_addr_dict[client] = address
                        
                elif s == adminserver: 
                        # handle the admin connection socket 
                        adminclient, address = adminserver.accept()
                        print "accepted admin client" + str(address)
                        input.append(adminclient)
                        admin_list.append(adminclient)
                        time.sleep(1.0/10.0)
                        adminclient.sendall("[System]:Type /help for all the commands\n")

                elif s in admin_list:
                        # handle the admin client socket
                        data = safeRecv(s, size).strip()  # Safely receive the data and put it into data variable             
                        if data:
                               # Check if the data is not empty 
                               if data.startswith('/'):
                                       # Check if the data starts as a command 
                                       if data == '/stop':
                                               # Stops the server 
                                               running = 0

                                       elif data == '/help':
                                               # Prints the help message for admin 
                                               s.sendall(helpmsg)

                                       elif data == '/list':
                                               # Lists all connected clients (excluding admins) 
                                               s.sendall("Users online: \n")
                                               if not user_dict:
                                                       s.sendall("No users online\n")
                                               else: 
                                                       for k, v in user_dict.items():
                                                               s.sendall(str(k) + ' - ' + v + '\n')

                                       elif data.split()[0] == '/msg-name':
                                               # Admin private messages client based on name 
                                               # try except to catch IndexError
                                               try:
                                                       nickName = data.split()[1]
                                               except IndexError:
                                                       s.sendall("Use the command with the correct arguments, /msg-name [name] [message]\n")
                                               else:
                                                       # error is set to 1
                                                       error = 1
                                                       # Send a copy of the message to the admin
                                                       # if client yields nothing from start, it would skip this loop and proceeds to print the error msg Invalid user
                                                       for client in findUserName(user_dict, usersocket_addr_dict, nickName):
                                                               s.sendall("[Admin > " + nickName+ "]: " + " ".join(data.split()[2:]) + "\n")
                                                               #error is set to 0 if the user is valid
                                                               error = 0
                                                       if error == 1:
                                                               s.sendall("Invalid user\n")
                                                       # Find the user with the name and sends it to them
                                                       for client in findUserName(user_dict, usersocket_addr_dict, nickName):
                                                                client.sendall("[Admin > " + nickName+ "]: " + " ".join(data.split()[2:]) + "\n")

                                       elif data.split()[0] == '/msg-ip':
                                               # Admin private messages client based on IP address and, if specified, port number 
                                               # try except to catch IndexError
                                               try:
                                                       ipaddr = data.split()[1].split(':')
                                               except IndexError:
                                                       s.sendall("[System]: Use the command with the correct arguments, /msg-ip [ip[:port]] [message]\n")
                                               else:
                                                       # error is set to 1
                                                       error = 1 
                                                       # Send a copy of the message to the admin
                                                       # if client yields nothing from start, it would skip this loop and proceeds to print the error msg Invalid IP address/port
                                                       for client in findUserIP(usersocket_addr_dict, ipaddr):
                                                               s.sendall("[Admin > " + data.split()[1] + "]: " + " ".join(data.split()[2:]) + "\n")
                                                               error = 0
                                                       if error == 1:
                                                               s.sendall("[System]: Invalid IP address/port\n")
                                                       # Find the user with the IP address and sends it to them
                                                       for client in findUserIP(usersocket_addr_dict, ipaddr):
                                                                client.sendall("[Admin > " + data.split()[1] + "]: " + " ".join(data.split()[2:]) + "\n")

                                       elif data.split()[0] == '/kick-name':
                                               # Kicks a client based on their nickname                                                
                                               # try except to catch IndexError
                                               try:
                                                       nickName = data.split()[1]
                                               except IndexError:
                                                       s.sendall("[System]: Use the command with the correct arguments, /kick-name [name]\n")
                                               else:
                                                       # error is set to 1
                                                       error = 1
                                                       for client in findUserName(user_dict, usersocket_addr_dict, nickName):
                                                               print "Kicking: " + nickName
                                                               client.close()
                                                               input.remove(client)
                                                               del user_dict[usersocket_addr_dict[client]]
                                                               del usersocket_addr_dict[client]
                                                               sendAllSockets(input[2:], "[Admin]:Kicked " + nickName + "\n")
                                                               error = 0
                                                       if error == 1:
                                                               s.sendall("[System]: Invalid user\n")

                                       elif data.split()[0] == '/kick-ip':
                                               # Kicks a client based on their IP address and, if specified, port number 
                                               try:
                                                       ipaddr = data.split()[1].split(':')
                                               except IndexError:
                                                       s.sendall("[System]: Use the command with the correct arguments, /kick-ip [ip[:port]")
                                               else:
                                                       # error is set to 1
                                                       error = 1
                                                       for client in findUserIP(usersocket_addr_dict, ipaddr):
                                                               print "Kicking: " + str(ipaddr)
                                                               client.close()
                                                               input.remove(client)
                                                               del user_dict[usersocket_addr_dict[client]]
                                                               del usersocket_addr_dict[client]
                                                               sendAllSockets(input[2:], "[Admin]:Kicked " + data.split()[1] + "\n")
                                                               error = 0
                                                       if error == 1:
                                                               s.sendall("[System]: Invalid IP address/port\n")
 
                                       else:
                                               # If it not a valid command, print an error message
                                               s.sendall("Invalid command, type /help for more information\n")
                                       
                               else:
                                       #Admin broadcast to all users
                                       sendallSockets(input[2:], "[Admin]:" + data + "\n")
                        else:
                                #If the data is empty, it means the admin is disconnecting.
                                print "Closing an admin client"
                                s.close()
                                admin_list.remove(s)
                                input.remove(s)        
                else:
                        # handle all the rest (client input)
                        data = safeRecv(s,size) 
                        if data:
                                #regex to get nickname of user from data
                                getNickName = re.match(r'^\[(.+)]:', data)
                                #storing the nickName into user_dict
                                user_dict[usersocket_addr_dict[s]] = getNickName.group(1)
                                sendAllSockets(input[2:], data)
                        else: 
                                # the client  must have closed the socket at its end.
                                print "closing a client"
                                s.close() 
                                input.remove(s)
                                #delete user from both dict
                                del user_dict[usersocket_addr_dict[s]]
                                del usersocket_addr_dict[s]

# Close all sockets and shutdown server
for s in input:
        s.close()
print "Bye Bye"
