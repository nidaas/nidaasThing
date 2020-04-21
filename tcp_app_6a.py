import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import time, threading

scriptBoxCount=10

def receiveParse(data):
    msg_list.insert(tk.END, data)
    msg_list.see(tk.END)

def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            if msg=='':
                print("Connection Closed")
                break
            else:
                print(msg)
            receiveParse(msg)
            
        except OSError:  # Possibly client has left the chat.
            break


def sendStr(cmd,event=None):  # event is passed by binders.
    """Handles sending of messages."""
    msg = cmd
    print('Sent')
    client_socket.send(bytes(msg, "utf8"))

def sendbyte(cmd,event=None):  # event is passed by binders.
    """Handles sending of messages."""
    data = bytes.fromhex(cmd)
    print('Sent')
    client_socket.send(data)


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        client_socket.close()
        root.destroy()

def popupmsg(msg):
    popup = tk.Tk()
    popup.wm_title("!")
    label = ttk.Label(popup, text=msg, font='NORM_FONT')
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()

def scriptStop():
    print('Script Stop')
    runScript.configure(text='Run Script',command=lambda:scriptRun(0))
    global t1
    t1.cancel()

def scriptRun(i):
    print('Script Run')
    global t1
    runScript.configure(text='Stop Script',command=scriptStop)
    if app[i].activationState.get():
        app[i].sendData()
        for j in range(i+1,scriptBoxCount+1):
            if j==scriptBoxCount:
                if scriptLoop.get()==1:
                    timeDelay=app[i].delay.get()/1000
                    t1 = threading.Timer(timeDelay, scriptRun,args=[0])
                    t1.start()
                    print(str(j)+ ' is active next for:'+str(timeDelay))
                else:
                    runScript.configure(text='Run Script',command=lambda:scriptRun(0))
                break

            if app[j].activationState.get():
                timeDelay=app[i].delay.get()/1000
                t1 = threading.Timer(timeDelay, scriptRun,args=[j])
                t1.start()
                print(str(j)+ ' is active next for:'+str(timeDelay))
                break

class App(tk.Tk):
  def __init__(self, master):
    frame = tk.Frame(master)
    frame.pack()
    self.activationState=tk.IntVar()
    self.activateCheck= tk.Checkbutton(frame,variable=self.activationState)
    self.activateCheck.pack(side='left',padx=8)
    self.isHex=tk.IntVar()
    self.isHexCheck= tk.Checkbutton(frame,variable=self.isHex)
    self.isHexCheck.pack(side='left',padx=8)
    self.data=tk.Entry(frame)
    self.data.pack(side='left')
    self.appendOptionString=tk.StringVar(frame)
    self.appendOptions=tk.OptionMenu(frame, self.appendOptionString, "None", "\\r\\n", "\\r", "\\n","CTRL+Z")
    self.appendOptions.config(width=6)
    self.appendOptions.pack(side='left')
    self.delay=tk.IntVar()
    self.delayField=tk.Entry(frame,textvariable=self.delay,width=10)
    self.delayField.pack(side='left')
    self.manualFire = tk.Button(frame,
                         text="Send",
                         command=self.sendData)
    self.manualFire.pack(side='left',padx=10)
  def digitValidate(self, P):
    if str.isdigit(P) or P == "":
        return True
    else:
        return False
  def sendData(self):
      if self.activationState.get():
          print("Acivated")
          if self.isHex.get():
            strHex=self.data.get()
            appendOp=self.appendOptionString.get()
            if appendOp=="None":
                print("Append :None")
            elif appendOp=="\\r\\n":
                print("Append :\\r\\n")
                strHex+='0D0A'
            elif appendOp=="\\r":
                print("Append :\\r")
                strHex+='0D'
            elif appendOp=="\\n":
                print("Append :\\n")
                strHex+='0A'
            elif appendOp=="CTRL+Z":
                print("Append :CTRL+Z")
                strHex+='1A'
            sendbyte(strHex)
          else:
            strstr=self.data.get()
            print(strstr)
            appendOp=self.appendOptionString.get()
            if appendOp=="None":
                  print("Append :None")
            elif appendOp=="\\r\\n":
                  print("Append :\\r\\n")
                  strstr+='\r\n'
            elif appendOp=="\\r":
                  print("Append :\\r")
                  strstr+='\r'
            elif appendOp=="\\n":
                  print("Append :\\n")
                  strstr+='\n'
            sendStr(strstr)
            if appendOp=="CTRL+Z":
                  print("Append :CTRL+Z")
                  sendbyte('1A')  
      else:
         print("Deactive")

def setting_Popup():
    win = tk.Toplevel()
    win.wm_title("Set UP System")

    lbl = tk.Label(win, text="Pleas select Protocol.")
    lbl.pack()
    
    btn = tk.Button(win, text="OK", command=win.destroy)
    btn.pack()
    
    win.transient(root) #set to be on top of the main window
    win.grab_set() #hijack all commands from the master (clicks on the main window are ignored)
    root.wait_window(win) #pause anything on the main window until this one closes (optional)



root = tk.Tk()
scriptFrame = tk.Frame(root)
messages_frame = ttk.Frame(root)
scriptUpperFrame = ttk.Frame(scriptFrame)
scriptDownFrame = ttk.Frame(scriptFrame)
scrollbar = ttk.Scrollbar(messages_frame,orient=tk.VERTICAL)  # To navigate through past messages.
# Following will contain the messages.
global msg_list 
msg_list= tk.Listbox(messages_frame, height=25, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
scrollbar.config(command=msg_list.yview)
msg_list.pack(side=tk.LEFT, fill=tk.BOTH)
msg_list.pack()
messages_frame.pack(side=tk.LEFT,anchor='nw',padx=5)

isActive = tk.Label(scriptUpperFrame, text = "Active")
isActive.pack(side='left',fill='x')

isHex = tk.Label(scriptUpperFrame, text = "Hex")
isHex.pack(side='left',fill='x',padx=10)

textData = tk.Label(scriptUpperFrame, text = "Data")
textData.pack(side='left',fill='x',padx=60)

toAppend = tk.Label(scriptUpperFrame, text = "Append")
toAppend.pack(side='left',fill='x',padx=10)

toDelay = tk.Label(scriptUpperFrame, text = "Delay(ms)")
toDelay.pack(side='left',fill='x',padx=30)

scriptUpperFrame.pack(side=tk.TOP,fill=tk.BOTH)

app=[]
for i in range(scriptBoxCount):
    app.append(App(scriptFrame))

scriptLoop = tk.IntVar()
scriptLoopUI=tk.Checkbutton(scriptDownFrame, text="Loop", variable=scriptLoop)
#scriptLoopUI.pack(side='left',padx=100,fill='x')
runScript = tk.Button(scriptDownFrame,text="Run Script",command=lambda:scriptRun(0))
#runScript.pack(side='left',padx=5)
scriptLoopUI.grid(row=0, column=1, padx=(200, 10),pady=(20,10))
runScript.grid(row=0, column=2, padx=(10, 100),pady=(20,10)) 
scriptDownFrame.pack(side=tk.TOP,fill=tk.BOTH)

scriptFrame.pack(side=tk.RIGHT,fill=tk.BOTH)
setting_Popup()
HOST = '192.168.43.251'
PORT = '33000'
if not PORT:
    PORT = 30000
else:
    PORT = int(PORT)

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)
receive_thread = Thread(target=receive,daemon=True)
receive_thread.start()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()