# for local communication
from socket import AF_INET, socket, SOCK_STREAM,gethostbyname,gethostname

# for threading chats
from threading import Thread

# for encryption
from Crypto.Cipher import AES



class GlobalData:
    clients = {}
    addresses = {}

    #To find ip of my lan network. CLI command : ifconfig
    host = gethostbyname(gethostname()) 
    
    port = 5000
    bufferSize = 1024
    serverAddress = (host, port)

    # initialising socket model
    serverObj = socket(AF_INET, SOCK_STREAM)
    serverObj.bind(serverAddress)

    # encryption key in string
    encKey = "iUJ}qh'GxpIKdNB'*p'aXF.!5#F_LR[FK8k>8.ZX82?bZ5<ic[.bf^o9+eh(B@d"
    
    # An initialization vector (IV) is an arbitrary number that can be used along with a secret key for data encryption.
    aesObj = AES.new(encKey , AES.MODE_CBC ,  'This is an IV456')

    welcomeMessage = "Welcome to local-secure-chat"

    quitStatement = "okquit"

    maxConnectionLimit = 7



def lenstr(msg):
    size=len(msg)
    if size%16 != 0:
        for i in range(size,200):
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



class HandleChat:


    # function to set up the new connection request and intialise the thread
    @classmethod
    def acceptIncomingConnection(cls):

        # virtually can handle unlimited connections
        while(True):

            client , clientAddress = GlobalData.serverObj.accept()

            # printing the connection details
            print("{} has connected".format(clientAddress))

            client.send(bytes(GlobalData.welcomeMessage , "utf-8"))
            client.send(bytes("Send you name please!" , "utf-8"))

            # storing the new connection details in dictionary
            GlobalData.addresses[client] = clientAddress

            # init thread
            Thread(target=cls.handleClient , args=(client)).start()


    # function to handle the initiated client connection
    @classmethod
    def handleClient(cls , client):

        # first thing we receive is the clients name
        nameReceived = client.recv(GlobalData.bufferSize)
        name = HandleEncryption.decrypt(nameReceived)
        name = name.rstrip(b' ')

        # sending greetings to user
        welcomeMessage = "Welcome {} , To quit chat type and send : {}".format(name , GlobalData.quitStatement)
        client.send(bytes(welcomeMessage , "utf-8"))

        # broadcast message to all the connected user that name as connected
        toSend = "{} has joined the local-secure-chat".format(name)
        cls.broadcastMessage(bytes(toSend , "utf-8"))

        # adding client to storage
        GlobalData.clients[client] = name

        while(True):

            # decryting the message
            messageReceived = client.recv(GlobalData.bufferSize)
            messageReceived = HandleEncryption.decrypt(messageReceived)
            messageReceived = messageReceived.rstrip(b" ")

            # if user does not want to quit
            if(messageReceived != bytes(GlobalData.quitStatement , "utf-8")):
                
                # broadcast the message to every one
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
        name = name + b" : "

        toSend = bytes(name) +  message

        for sock in GlobalData.clients:
            sock.send(toSend)







if __name__ == "__main__":
    print("IP serverAddress of the server : {}".format(GlobalData.host))

    GlobalData.serverObj.listen(GlobalData.maxConnectionLimit)

    print("Waiting for connection...")

    startThreading = Thread(target=HandleChat.acceptIncomingConnection)
    
    startThreading.start()
    startThreading.join()
    GlobalData.serverObj.close()
    
