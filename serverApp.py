# for local communication
import socket
from socket import error, setdefaulttimeout
import errno

# for threading chats
from threading import Thread

# for encryption
from Crypto.Cipher import AES

# Global Data
from globalData import GlobalData


from contextlib import closing







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



class HandleChat:


    # function to set up the new connection request and intialise the thread
    @classmethod
    def acceptIncomingConnection(cls):

        # virtually can handle unlimited connections
        while(True):

            client , clientAddress = GlobalData.serverObj.accept()

            # printing the connection details
            print("{} has connected".format(clientAddress))

            # send a welcome message and ask for name
            client.send(bytes(GlobalData.welcomeMessage , "utf-8"))
            client.send(bytes("|| Send you name please!" , "utf-8"))

            # storing the new connection details in dictionary
            GlobalData.addresses[client] = clientAddress

            # init thread
            Thread(target=cls.handleClient , args=(client , )).start()


    # function to handle the initiated client connection
    @classmethod
    def handleClient(cls , client):

        # first thing we receive is the clients name
        nameReceived = client.recv(GlobalData.bufferSize)
        name = HandleEncryption.decrypt(nameReceived)

        # removing the extra added during lenStr function
        name = name.rstrip(b' ')

        # sending greetings to user
        try:
            welcomeMessage = "Welcome {} , To quit chat type and send : {}".format(str(name , "utf-8") , GlobalData.quitStatement)
            client.send(bytes(welcomeMessage , "utf-8"))
        except UnicodeDecodeError:
            client.send(bytes("This name is not allowed , you are allocated name : user" , "utf-8"))
            name = b"user"

        # broadcast message to all the connected user that name as connected
        toSend = "{} has joined the local-secure-chat".format(str(name , "utf-8"))
        cls.broadcast(bytes(toSend , "utf-8"))

        # adding client to storage
        GlobalData.clients[client] = name

        while(True):

            # decryting the message
            try:
                messageReceived = client.recv(GlobalData.bufferSize)
            
            # bad file descriptor
            except OSError:
                break

            # decrypting the message
            messageReceived = HandleEncryption.decrypt(messageReceived)
            messageReceived = messageReceived.rstrip(b" ")

            # if user does not want to quit
            if(messageReceived != bytes(GlobalData.quitStatement , "utf-8")):
                
                # broadcast the message to every one
                # here we don't need to worry about space as we are not working with string
                cls.broadcast(messageReceived , name)

            else:

                # init the closing sequence

                # send the client also to close the connection
                client.send(bytes(GlobalData.quitStatement , "utf-8"))
                client.close()

                # delete the client data
                del GlobalData.clients[client]

                # broad cast to let others know that name as left the chat room
                cls.broadcast(bytes("{} has left the chat room".format(name) , "utf-8"))

                break


    # function to broadcast a message to all the clients
    @classmethod
    def broadcast(cls , message , name = b""):

        # if the name contains space then it cannot be used with utf-8
        name = name + b" : "

        toSend = bytes(name) +  message

        tempGlobalClients = GlobalData.clients.copy()

        # sending message to each client
        for sock in tempGlobalClients:
            try:
                sock.send(toSend)
            except BrokenPipeError:
                print("failed to broadcast to {} because of broken pipe , deleting client".format(sock))
                sock.close()

                # delete the client data
                del GlobalData.clients[sock]






if __name__ == "__main__":


    # getting the ip address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))


    GlobalData.host = s.getsockname()[0]

    GlobalData.serverAddress = (GlobalData.host , GlobalData.port)

    try:
        GlobalData.serverObj.bind(GlobalData.serverAddress)
    except error as e:
            # if the port number is unavailable
            if(e.errno == errno.EADDRINUSE):

                # getting the port number
                with closing(s) as s:
                    s.close()
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                    s.bind(('', 0))
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        
                    # assign the port to object
                    GlobalData.port = s.getsockname()[1]

            # initialising serve object
            s.close()
            GlobalData.serverAddress = (GlobalData.host , GlobalData.port)
            GlobalData.serverObj.bind(GlobalData.serverAddress)


    # printing ip address and port number to connect
    print("IP serverAddress of the server : {}".format(GlobalData.host))
    print("port used by the server is : {}".format(GlobalData.port))
    
    GlobalData.serverObj.listen(GlobalData.maxConnectionLimit)

    print("Waiting for connection...")

    # each new connection will get a sepearte thread
    try:
        startThreading = Thread(target=HandleChat.acceptIncomingConnection)
        
        startThreading.start()
        startThreading.join()
        GlobalData.serverObj.close()
    except KeyboardInterrupt:
        GlobalData.serverObj.close()

    
