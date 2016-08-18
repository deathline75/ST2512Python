#!/usr/bin/python
"""
Author: Ang Wei Xiang Darren (P1444588) & Neo Ken Hong, Kelvin (P1529179)
Class: DISM/FT/2A/02
Task: 2
"""
import crypt
import time

#print start time
print "Program started time:", time.strftime("%Y-%m-%d %H:%M:%S"), '\n'

#Read shadow file and put it in content variable
with open('shadow.txt', 'r') as shadow:
    content = shadow.readlines()
    shadow.close()
    
#declaring variables and lists to be used later on
user = []
salt = []
hashedpwd = []
addtonumlist = False
crackedpwd = ''

#generating list of unique numbers using list comprehension
print 'Generating number list...'
numlist = [num for num in range(999999) if len(set(str(num))) == len(str(num))]
print 'Number list generated: ', len(numlist), 'unique numbers in list\n'

#splitting values and store them in the appropriate lists
for s in content:
    user.append(s[:8])
    salt.append(s[9:20])
    hashedpwd.append(s[9:-20])
    
print 'Password cracking started...\n'    
#password cracking part            
for i in range(len(user)):
    for checkhash in numlist:
        checkhash = str(checkhash)
        if crypt.crypt(checkhash, salt[i]) == hashedpwd[i]:
            crackedpwd = checkhash
            break
    print 'password of user',user[i],'is', crackedpwd

#print End time
print '\nFinished cracking...\n'
print "Program completed time:", time.strftime("%Y-%m-%d %H:%M:%S")
