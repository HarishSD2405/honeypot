# libraries
import logging 
from logging.handlers import RotatingFileHandler 
import paramiko
import socket
import datetime
import threading

# constants
logging_format = logging.Formatter('%(message)s') # only the log message itself will be recorded, without additional metadata like timestamps or log levels.
SSH_BANNER = "SSH-2.0-MySSHServer_1.0"
host_key = paramiko.RSAKey(filename='server.key') # private key of the public-private key pair (kept as secret)
# loggers and logging files

# to capture usernames, passwords, ip addresses
funnel_logger = logging.getLogger('FunnelLogger') 
funnel_logger.setLevel(logging.INFO) 
funnel_handler = RotatingFileHandler("audits.log",maxBytes = 2000, backupCount = 5)
funnel_handler.setFormatter(logging_format)
funnel_logger.addHandler(funnel_handler)

# to capture emulated shell commands
creds_logger = logging.getLogger('CredsLogger') 
creds_logger.setLevel(logging.INFO) 
creds_handler = RotatingFileHandler("cmd_audits.log",maxBytes = 2000, backupCount = 5)
creds_handler.setFormatter(logging_format)
creds_logger.addHandler(creds_handler)

# emulated shell
def emulated_shell(channel, client_ip):
    channel.send(b"hArish@hArish-laptop:~$ ")
    command = b""
    
    while True:  
        char = channel.recv(1)
        
        # Handle backspace
        if char == b"\x7f":  # ASCII backspace
            if command:
                command = command[:-1]  # Remove last character
                channel.send(b"\b \b")  # Move back, clear character, move back again
            continue
        
        # Handle regular character input
        channel.send(char)  # Echo back to simulate typing
        
        if not char:  # Client disconnected
            channel.close()
            break
        
        command += char

        # Process command on Enter (carriage return)
        if char == b"\r":
            command_str = command.strip()
            
            if command_str == b'exit':
                response = b"\r\n Goodbye!\r\n"
                channel.send(response)
                channel.close()
                creds_logger.info(f'Client {client_ip} executed command: exit')
                break

            elif command_str == b'pwd':
                response = b"\r\n/home/hArish\r\n"
            elif command_str == b'whoami':
                response = b"\r\ncorpuser1\r\n"
            elif command_str == b'ls':
                response = b"\r\njumpbox1.conf\r\n"
            elif command_str == b'cat jumpbox1.conf':
                response = b"\r\nGo to deeboodah.com\r\n"
            else:
                response = b"\r\nCommand not found: " + command_str + b"\r\n"
                
            # Log command once processed
            creds_logger.info(f'Client {client_ip} executed command: {command_str.decode()}')
            
            # Send response and reset command buffer
            channel.send(response)
            channel.send(b"hArish@hArish-laptop:~$ ")
            command = b""

# ssh server + sockets

class Server(paramiko.ServerInterface):
    def __init__(self, client_ip, input_username=None, input_password=None):
        self.event = threading.Event()
        self.client_ip = client_ip
        self.input_username = input_username
        self.input_password = input_password

    def check_channel_request(self, kind: str, chanid: int) -> int:
        if kind == 'session': # check is session successfully established
            return paramiko.OPEN_SUCCEEDED
    def get_allowed_auth(self):
        return "password" # can also use publicKey
    def check_auth_password(self, username, password):
        funnel_logger.info(f'Client {self.client_ip} attempted connection with ' + f'username {username}, '+ f'password {password}')
            
        if self.input_username is not None and self.input_password is not None:
            if username == self.input_username and password == self.input_password:
                return paramiko.AUTH_SUCCESSFUL
            else:
                return paramiko.AUTH_FAILED
        else:
            return paramiko.AUTH_SUCCESSFUL # if no username or password is defined
        
    # checks if the client’s request to start an interactive shell (like a command-line shell) should be allowed.
    def check_channel_shell_request(self, channel):
        self.event.set()
        return True
    
    # handles the client's request to open a pseudo-terminal (PTY)
    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    # handles a request to execute a specific command on the server (like a one-time command rather than an interactive shell).
    def check_channel_exec_request(self, channel, command):
        command = str(command)
        return True

def client_handle(client, address, username, password):
    client_ip = address[0]
    print(f"{client_ip} has connected to the server.")
    try:
        # handles low level ssh session
        transport = paramiko.Transport(client)
        # transport.local_version = SSH_BANNER
        
        server = Server(client_ip=client_ip, input_username=username, input_password=password)
        
        transport.add_server_key(host_key)

        transport.start_server(server=server)

        channel = transport.accept(100)
        if channel is None:
            print("no channel opened....")
        
        standard_banner = "Welcome to the Secure Shell (SSH) Server\r\n\r\n"

        channel.send(standard_banner)
        emulated_shell(channel, client_ip=client_ip)
        
    except Exception as error:
        print(error)
        print("ERROR!")
    finally:
        try:
            transport.close()
        except Exception as error:
            print(error)
            print("Error!")
        client.close()

# provision ssh based honeypot

def honeypot(address, port, username, password):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # ipv4 and tcp
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # reuse address already in use
    sock.bind((address,port)) # defining where socket should be listening
    sock.listen(100)

    print(f"SSH Server is listening on port {port}.")

    while True:
        try:
            client, address = sock.accept() # listens and accepts incoming connections and returns a tuple
            ssh_honeypot_thread = threading.Thread(target=client_handle, args=(client, address, username, password))
            ssh_honeypot_thread.start()
        except Exception as error:
            print(error)

