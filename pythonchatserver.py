#-----------------------------------------
#    Program:    A Python Chat Server
#    Developer:  Jeremiah J. Bergkvist 
#    Date:       01 November 2009
#-----------------------------------------
import re
import socket
import string
import sys
import threading
from Tkinter import *

#-----------------------------------------
#    Menu Class
#-----------------------------------------
class Menu(Frame):
   def FileMenu(MENU_FRAME, EVENT=None):
       FILE_BTN=Menubutton(MENU_FRAME, text='File', underline=0)
       FILE_BTN.pack(side=LEFT, padx="2m")
       FILE_BTN.menu=Menu(FILE_BTN)
       #FILE_BTN.menu.add_command(label="Open",underline=0,command=self.Open)
       #FILE_BTN.menu.add_command(label="Exit",underline=0,command=self.Exit)
       FILE_BTN['menu']=FILE_BTN.menu
       return FILE_BTN

   def HelpMenu(MENU_FRAME, EVENT=None):
       HELP_BTN=Menubutton(MENU_FRAME, text="Help", underline=0)
       HELP_BTN.pack(side=LEFT, padx="2m")
       HELP_BTN.menu=Menu(HELP_BTN)
       #HELP_BTN.menu.add_command(label="About",underline=0,command=self.About)
       HELP_BTN['menu']=HELP_BTN.menu
       return HELP_BTN

   def Open():
       print "Open"

   def Exit():
       ROOT.destroy()

   def About():
       ABOUT_WIN=Toplevel()
       ABOUT_FRAME=Frame(ABOUT_WIN, relief=FLAT)
       ABOUT_FRAME.pack(fill=BOTH, side=TOP, padx=10, pady=10, expand=1)
       ABOUT_LABEL=Label(ABOUT_FRAME, text="About Text Area")
       ABOUT_LABEL.pack(side=LEFT)

#-----------------------------------------
#    Socket Class
#-----------------------------------------
class Socket(threading.Thread):
   ALL_CLIENTS = []
   def SocketError(ERROR):
       GUI.LOG.config(state=NORMAL)
       GUI.LOG.insert(END, "Socket Error: %s\n" %ERROR)
       GUI.LOG.config(state=DISABLED)
       return 0

   def EnabledMessage(EVEMT):
       GUI.LOG.config(state=NORMAL)
       GUI.LOG.insert(END, "Server Enabled\n")
       GUI.LOG.config(state=DISABLED)
       return 1

   def WhoJoined(self,USERNAME, PASSWORD):
       GUI.LOG.config(state=NORMAL)
       GUI.LOG.insert(END, "%s joined, password is %s\n"%(USERNAME, PASSWORD))
       GUI.LOG.config(state=DISABLED)
       return 1

   def PortError(EVENT):
       GUI.LOG.config(state=NORMAL)
       GUI.LOG.insert(END, "You must first set the port!\n")
       GUI.LOG.config(state=DISABLED)
       return 0

   def EnableServer(self):
       if GUI.PORT_INT == None:
           self.PortError()
           return 0
       SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       SERVER_SOCKET.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
       try:
           SERVER_SOCKET.bind(('',GUI.PORT_INT))
       except socket.error, ERROR:
           self.SocketError(ERROR)
       SERVER_SOCKET.listen(5)
       self.EnabledMessage()
       #-- Server Listener
       while True:
           CLIENT_SOCKET, ADDRESS = SERVER_SOCKET.accept()
           self.NewClientConnection(CLIENT_SOCKET)
       return 1

   def RecvMessage(self, SOCKET):
       try:
           BUFFER = SOCKET.recv(2048)
           return BUFFER
       except socket.error, ERROR:
           self.SocketError(ERROR)
           return 0

   def NewClientConnection(self, CLIENT_SOCKET):
       SOCKET=CLIENT_SOCKET
       # Recv Username
       try:
           USERNAME = SOCKET.recv(2048)
           USERNAME = USERNAME.strip()
       except socket.error, ERROR:
           self.SocketError(ERROR)
       # Recv Password
       try:
           PASSWORD = SOCKET.recv(2048)
           PASSWORD = PASSWORD.strip()
       except socket.error, ERROR:
           self.SocketError(ERROR)
       # Password check, if valid do:
       self.ALL_CLIENTS.append(SOCKET)
       self.WhoJoined(USERNAME, PASSWORD)
       return 1

   def SendAll(self, BUFFER):
       for INDEX, SOCKET in enumerate(ALL_CLIENTS):
           if self.SOCKET != CLIENT_SOCKET:
               print(self.SOCKFD == CLIENT_SOCKET)
               try:
                   CLIENT_SOCKET.send("[%s] => %s"
%(self.USERNAME, BUFFER))
               except socket.error, ERROR:
                   self.SocketError(ERROR)
                   CLIENT_SOCKET.close()
                   del ALL_CLIENTS[INDEX]
       return 1

#-----------------------------------------
#    GUI Class
#-----------------------------------------
class Gui(Frame):
   PORT_INT = None
   def PortError():
       self.LOG.config(state=NORMAL)
       self.LOG.insert(END,"Port must be between 1 and 65534\n")
       self.LOG.config(state=DISABLED)
       return 0

   def Command(self, COMMAND):
       if COMMAND == "":
           return 0
       self.LOG.config(state=NORMAL)
       self.LOG.insert(END,">>> %s\n" %(COMMAND))
       self.LOG.config(state=DISABLED)
       self.COMMAND_MESSAGE.set("")
       return 1

   def SetPort(self, EVENT=None):
       self.PORT_STR = self.PORT_MESSAGE.get()
       if self.PORT_STR != None:
           try:
               self.PORT_INT = string.atoi(self.PORT_STR)
           except:
               PortError()
               self.PORT_INT = None
               return 0
           if self.PORT_INT < 1:
               PortError()
               self.PORT_INT = None
               return 0
           if self.PORT_INT > 65534:
               PortError()
               self.PORT_INT = None
               return 0
       else:
           PortError()
           return 0
       self.LOG.config(state=NORMAL)
       self.LOG.insert(END,"Using Port %s\n" %(self.PORT_STR))
       self.LOG.config(state=DISABLED)
       return 1

   def Enable(self, EVENT=None):
       #-- Initialize Socket Class
       SOCK=Socket()
       threading.Thread(target =SOCK.EnableServer).start()
       return 1

   def SendCommand(self, EVENT=None):
       self.COMMAND_LIST = []
       self.COMMAND_LIST.append("?")
       self.COMMAND_LIST.append("help")
       self.COMMAND_LINE = self.COMMAND_MESSAGE.get()
       self.COMMANDS = re.findall('[a-zA-Z0-9_ ?]+', self.COMMAND_LINE)
       for self.COMMAND_ARG in self.COMMANDS:
           self.LOG.config(state=NORMAL)
           self.LOG.insert(END," %s \n" %(self.COMMAND_ARG))
           self.LOG.config(state=DISABLED)

       self.Command(self.COMMAND_LINE)
       for CHECK_COMMAND in self.COMMAND_LIST:
           if self.COMMANDS[0] == CHECK_COMMAND:
               self.LOG.config(state=NORMAL)
               self.LOG.insert(END,"Command %s found!\n" %(self.COMMANDS[0]))
               self.LOG.config(state=DISABLED)
               return 1
       self.LOG.config(state=NORMAL)
       self.LOG.insert(END,"Command %s NOT found!\n"
%(self.COMMANDS[0]))
       self.LOG.config(state=DISABLED)
       return 0

   def CreateWidgets(self):
       #-- Initialize Menu Class
       MENU = Menu(ROOT)
       #-- Create Menu
       self.MENU_FRAME=Frame(ROOT, relief=RAISED, borderwidth=1)
       self.MENU_FRAME.pack(fill=X, side=TOP)
       self.MENU_FRAME.tk_menuBar(MENU.FileMenu(self.MENU_FRAME),
MENU.HelpMenu(self.MENU_FRAME))
       #-- Create Port Entry Field
       self.PORT_FRAME=Frame(ROOT, relief=GROOVE, borderwidth=1)
       self.PORT_FRAME.pack(side=TOP)
       self.PORT_LABEL=Label(self.PORT_FRAME, text="Port: ")
       self.PORT_LABEL.pack(side=LEFT)
       self.PORT_FIELD=Entry(self.PORT_FRAME)
       self.PORT_FIELD.pack(side=TOP)
       self.PORT_MESSAGE=StringVar()
       self.PORT_MESSAGE.set("1337")
       self.PORT_FIELD["textvariable"]=self.PORT_MESSAGE
       #-- Create Buttons
       self.BTN_FRAME=Frame(ROOT)
       self.BTN_FRAME.pack(side=TOP)
       self.CONNECT_BTN=Button(self.BTN_FRAME,text="Enable",command=self.Enable)
       self.CONNECT_BTN.pack(side=LEFT, ipadx=5, padx=5, ipady=2, pady=5)
       self.SET_BTN=Button(self.BTN_FRAME,text="Set Port",command=self.SetPort)
       self.SET_BTN.pack(side=LEFT, ipadx=5, padx=5, ipady=2, pady=5)
       #-- Create Log Field
       self.LOG_FRAME=Frame(ROOT)
       self.LOG_FRAME.pack(fill=BOTH, side=TOP, expand=1)
       self.LOG=Text(self.LOG_FRAME)
       self.LOG.config(state=DISABLED)
       self.LOG.pack(fill=BOTH, side=TOP, expand=1)
       #-- Create Command Entry Field
       self.COMMAND_FRAME=Frame(ROOT, relief=GROOVE, borderwidth=1)
       self.COMMAND_FRAME.pack(side=BOTTOM, fill=X, expand=1)
       self.COMMAND_LABEL=Label(self.COMMAND_FRAME, text="Command: ")
       self.COMMAND_LABEL.pack(side=LEFT)
       self.COMMAND_FIELD=Entry(self.COMMAND_FRAME)
       self.COMMAND_FIELD.pack(side=LEFT, fill=X, expand=1)
       self.COMMAND_MESSAGE=StringVar()
       self.COMMAND_FIELD["textvariable"]=self.COMMAND_MESSAGE
       self.COMMAND_BTN=Button(self.COMMAND_FRAME,text="Send",command=self.SendCommand)
       self.COMMAND_BTN.pack(side=LEFT, ipadx=5, padx=5, ipady=2, pady=5)
       self.COMMAND_FIELD.bind('<Key-Return>',self.SendCommand)
       return 1

   def __init__(self,master=None):
       Frame.__init__(self,master)
       self.pack()
       self.CreateWidgets()

ROOT=Tk()
GUI=Gui(master=ROOT)
GUI.master.title("Python Chat Server v0.1")
GUI.master.minsize(200,100)
GUI.mainloop()
