# for local communication
from socket import AF_INET, socket, SOCK_STREAM

# for threading chats
from threading import Thread

# for GUI
import tkinter as tk
from tkinter import *
import tkinter

# for encryption
from Crypto.Cipher import AES

from globalData import GlobalData



def lenstr(msg):
    size=len(msg)
    if size%16 != 0:
        for i in range(size,600):
            if i%16 == 0:
                return msg
            else:
                msg=msg+" "
    else:
        return msg



# class contain methods to handle encryption and decrption using AES module
class HandleEncryption:

    @classmethod
    def decrypt(cls , encryptedText):
        decryptedMessage = GlobalData.aesObj.decrypt(encryptedText)
        return decryptedMessage

    @classmethod
    def encrypt(cls , toencrypt):
        cipheredText = GlobalData.aesObj.encrypt(toencrypt)
        return cipheredText


class TkObjects:
    tkObj = tk.Tk()
    messagesFrame = tk.Frame(tkObj)
    myMessage = tk.StringVar()
    scrollBar = tk.Scrollbar(messagesFrame)
    messageList = tk.Listbox(messagesFrame , height=25 , width=70 , font=('Times', 20) , yscrollcommand=scrollBar.set)
    entryField = tk.Entry(tkObj , textvariable=myMessage , background = "#D3D3D3" , font = "Helvetica 20",width=50)
    sendButton = tk.Button(tkObj , text="Send")



class HandleConnection:

    @classmethod
    def receive(cls):
        while(True):                                             
            try:
                message = GlobalData.serverObj.recv(GlobalData.bufferSize)
                message = str(message , "utf-8")
                TkObjects.messageList.insert(tk.END , message)
                TkObjects.messageList.see(tk.END)


            except OSError:
                break
            except RuntimeError:
                break

    
    @classmethod
    def send(cls , event=None):
        message = TkObjects.myMessage.get()
        tempMessage = message
        message = HandleEncryption.encrypt(lenstr(message))

        TkObjects.myMessage.set("")

        GlobalData.serverObj.sendto(bytes(message) , GlobalData.serverAddress)

        if(tempMessage == GlobalData.quitStatement):
            GlobalData.serverObj.close()
            TkObjects.tkObj.quit()


    @classmethod
    def sendInput(cls , input , event=None):

        message = HandleEncryption.encrypt(lenstr(input))
        GlobalData.serverObj.sendto(bytes(message) , GlobalData.serverAddress)




    @classmethod
    def onClose(cls , event=None):
        TkObjects.myMessage.set(GlobalData.quitStatement)
        cls.send()

    








if __name__ == "__main__":
    TkObjects.tkObj.title("local-secure-chat")
    TkObjects.tkObj.withdraw()

    TkObjects.myMessage.set("Type Here")

    TkObjects.scrollBar.pack(side=tk.RIGHT , fill=tk.Y)

    TkObjects.messageList.pack(side = tk.LEFT , fill=tk.BOTH)
    TkObjects.messageList.pack()
    TkObjects.messageList.see(tk.END)

    TkObjects.messagesFrame.pack()

    TkObjects.entryField.bind("<Return>" , HandleConnection.send)
    TkObjects.entryField.pack(padx=20, pady=20)
    TkObjects.entryField.focus()


    TkObjects.sendButton = tk.Button(TkObjects.tkObj , text="Send" , command=HandleConnection.send , font = "Helvetica 20 bold" , height = 2, width = 20 , bg='green')
    TkObjects.sendButton.pack()

    TkObjects.tkObj.protocol("WM_DELETE_WINDOW", HandleConnection.onClose)

    GlobalData.host = input("Enter HOST ip address : ")
    GlobalData.port = input("Enter HOST port address : ")

    GlobalData.port = int(GlobalData.port)

    GlobalData.serverAddress = (GlobalData.host , GlobalData.port)

    GlobalData.serverObj.connect(GlobalData.serverAddress)


    receivingThread = Thread(target=HandleConnection.receive)
    receivingThread.start()
    TkObjects.tkObj.deiconify()
    tk.mainloop()

    




