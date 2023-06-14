'''
$ tftp ip_address [-p port_mumber] <get|put> filename
'''

import socket
import argparse
#import validators
from struct import pack

DEFAULT_PORT = 69
BLOCK_SIZE = 512
DEFAULT_TRANSFER_MODE = 'netascii'

OPCODE = {'RRQ': 1, 'WRQ': 2, 'DATA': 3, 'ACK': 4, 'ERROR': 5}
MODE = {'netascii': 1,'octet': 2, 'mail': 3}

ERROR_CODE = {
    0: "Not defined, see error message (if any).",
    1: "File not found.",
    2: "Access violation.",
    3: "Disk full or allocation exceeded.",
    4: "Illegal TFTP operation.",
    5: "Unknown transfer ID.",
    6: "File already exists.",
    7: "No such user."
}

def send_wrq(filename, mode):
    # Create the WRQ packet
    format = f'>h{len(filename)}sB{len(mode)}sB'
    wrq_message = pack(format, OPCODE['WRQ'], bytes(filename, 'utf-8'), 0, bytes(mode, 'utf-8'), 0)
    sock.sendto(wrq_message, server_address)

    # Wait for the ACK packet
    try:
        ack_packet, server = sock.recvfrom(4)
        opcode = int.from_bytes(ack_packet[:2], 'big')
        ack_seq_number = int.from_bytes(ack_packet[2:4], 'big')

        if opcode == OPCODE['ACK'] and ack_seq_number == 0:
            # ACK received, WRQ successful
            print(f"WRQ for {filename} successful.")
        else:
            print(f"Error: Unexpected ACK packet received for WRQ.")
    except socket.timeout:
        print(f"Error: Timeout occurred during WRQ.")



def send_rrq(filename, mode):
    format = f'>h{len(filename)}sB{len(mode)}sB'
    rrq_message = pack(format, OPCODE['RRQ'], bytes(filename, 'utf-8'), 0, bytes(mode, 'utf-8'), 0)
    sock.sendto(rrq_message, server_address)
    #print(rrq_message)

def send_ack(seq_num, server):
    format = f'>hh'
    #print(seq_num)
    ack_message = pack(format, OPCODE['ACK'], seq_num)
    #print(ack_message)
    sock.sendto(ack_message, server)
def rrq_send(filename):
    # Open a file with the same name to save data  from server
    file = open(filename, "wb")
    seq_number = 0

    while True:

        # receive data from the server
        data, server = sock.recvfrom(516)
        # server uses a newly assigned port(not 69)to transfer data
        # so ACK should be sent to the new socket
        opcode = int.from_bytes(data[:2], 'big')

        # check message type
        if opcode == OPCODE['DATA']:
            seq_number = int.from_bytes(data[2:4], 'big')
            send_ack(seq_number, server)

        #    elif opcode == OPCODE['ERROR']:
        #        error_code = int.from_bytes(data[2:4], byteorder='big')
        #        print(server_error_msg[error_code])
        #        break
        #    else:
        #        break

        file_block = data[4:]
        print(file_block.decode())
        file.write(file_block)

        if len(file_block) < BLOCK_SIZE:
            print(len(file_block))
            file.close()
            break
def wrq_send(filename):
    # Open the file in binary mode for reading
    try:
        file = open(filename, 'rb')
    except IOError as e:
        print(f"Error: {e}")
        return

    # Create the WRQ packet
    format = f'>h{len(filename)}sB{len(DEFAULT_TRANSFER_MODE)}sB'
    wrq_message = pack(format, OPCODE['WRQ'], bytes(filename, 'utf-8'), 0, bytes(DEFAULT_TRANSFER_MODE, 'utf-8'), 0)
    sock.sendto(wrq_message, server_address)

    seq_number = 1

    while True:
        # Read a block of data from the file
        file_data = file.read(BLOCK_SIZE)

        # Create the DATA packet
        data_packet = pack(f'>hh{len(file_data)}s', OPCODE['DATA'], seq_number, file_data)

        # Send the DATA packet
        sock.sendto(data_packet, server_address)

        # Wait for the ACK packet
        try:
            ack_packet, server = sock.recvfrom(4)
            opcode = int.from_bytes(ack_packet[:2], 'big')
            ack_seq_number = int.from_bytes(ack_packet[2:4], 'big')

            if opcode == OPCODE['ACK'] and ack_seq_number == seq_number:
                # ACK received, move to the next block
                seq_number += 1
            else:
                print(f"Error: Unexpected ACK packet received for block {seq_number}")
                break

        except socket.timeout:
            # Timeout occurred, resend the packet
            print(f"Error: Timeout occurred for block {seq_number}. Retrying...")
            continue

        if len(file_data) < BLOCK_SIZE:
            # End of file reached, transmission complete
            break

    file.close()
    print(f"Uploaded {filename} successfully.")



# parse command line arguments
parser = argparse.ArgumentParser(description='TFTP client program')
parser.add_argument(dest="host", help="Server IP address", type=str)
parser.add_argument(dest="action", help="get or put a file", type=str)
parser.add_argument(dest="filename", help="name of file to transfer", type=str)
parser.add_argument("-p", "--port", dest="port", action="store", type=int)
args = parser.parse_args()

'''
if validators.domain(args.host):
    serber_ip = gethostbyname(args.host) 
elif validators.ip_address.ipv4(args.host)
    server_ip = args.host
else:
    print("Invalid host address")
    exit(0)
        
if args.port == None:
    server_port = DEFAULT_PORT
else 
    server_port == args_port
'''

# Create a UDP socket
server_ip = args.host
server_port = DEFAULT_PORT
server_address = (server_ip, server_port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send RRQ_message
mode = DEFAULT_TRANSFER_MODE
filename = args.filename
if(args.action=='get')
    send_rrq(filename, mode)
    rrq_send(filename)
elif(args.action=='put')
    send_wrq(filename, mode)
    wrq_send(filename)
