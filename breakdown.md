```py
logging_format = logging.Formatter('%(message)s') 
```
- only the log message itself will be recorded, without additional metadata like timestamps or log levels.
```py
RotatingFileHandler
```
- When a rotation occurs, the current log file (e.g., audits.log) might be renamed to something like audits.log.1. 
- If there are already backup files from previous rotations, the older backups are incremented (e.g., audits.log.2, audits.log.3, etc.).
- The backupCount parameter defines how many of these archived log files will be retained. For example, if backupCount=5, only the five most recent archived logs will be kept. If a sixth rotation occurs, the oldest backup (e.g., audits.log.5) will be deleted.
```
INFO LEVEL
```
- Confirmation that things are working as expected. This level is used for general operational information, indicating that the system is functioning normally.
- The INFO level is primarily used to log messages that are important for understanding the general state of the application without being overly verbose. It confirms that specific operations have been successfully completed.
- when a user successfully logs in, when a file is processed, or when a connection to a database is established.

```py
char = channel.recv(1) # listening to user input - 1 byte at a time
        channel.send(char)
```
- Reads one byte of data (one character) from the client and Echoes the received character back to the client, simulating a real-time terminal where the typed characters appear on-screen.

```py
class Server(paramiko.ServerInterface):
```
- defines the structure and default behavior for an SSH server interface
```
paramiko
```
- The paramiko library is a Python package designed for handling SSH connections. It provides tools for both SSH client and server interactions, allowing secure connections and enabling actions like remote command execution or secure file transfers.
- In this code, paramiko.ServerInterface is being subclassed to create a custom SSH server interface. The ServerInterface class has several methods we can override to customize the server's behavior.

```py
def client_handle()
```
- The client_handle function manages a client's connection to the SSH server. It sets up the necessary transport layer for SSH, initializes the server instance, sends an SSH banner, and starts an emulated shell session for the client.
        - client: The client socket connection object.
        - address: A tuple containing the IP address and port of the connected client

- Transport - this object is responsible for handling the SSH transport layer.
```py
channel = transport.accept(100)
```
- The server waits for a channel (an interactive session) to be opened by the client. The timeout for waiting for the channel is set to 100 seconds. If no channel is opened, a message is printed.

```
socket
```
A socket is an endpoint for sending or receiving data across a computer network.
```py
socket.socket()
```
create new socket object
```
AF_INET
```
- will use ipv4 address
```
SOCK_STREAM
```
- will use TCP connection
```
socket.so_REUSEADDR
```
- This is useful when the server needs to be restarted quickly without waiting for the operating system to release the socket.
