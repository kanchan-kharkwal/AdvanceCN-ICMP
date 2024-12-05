import os
import sys
import time
import socket
import struct
import select

ICMP_ECHO_REQUEST = 8  # ICMP type for Echo Request
DATA_SIZE = 32  # Size of the data in bytes

def checksum(source_string):
    """Calculate the checksum of the packet."""
    countTo = (len(source_string) // 2) * 2
    sum = 0
    for count in range(0, countTo, 2):
        val = source_string[count + 1] * 256 + source_string[count]
        sum += val
    if countTo < len(source_string):
        sum += source_string[len(source_string) - 1]
    sum = (sum >> 16) + (sum & 0xFFFF)
    sum += (sum >> 16)
    return ~sum & 0xFFFF

def create_packet(id):
    """Create an ICMP packet."""
    # Header
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, id, 1)
    # Data
    data = bytes(DATA_SIZE)  # 32 bytes of data
    # Checksum
    my_checksum = checksum(header + data)
    # Repack header with checksum
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), id, 1)
    return header + data

def handle_response(sock, packet_id, start_time):
    """Handle the response from the ping."""
    while True:
            print("Waiting for response...")
            # Receive the response
            recv_packet, addr = sock.recvfrom(1024)
            time_received = time.time()
            icmp_header = recv_packet[20:28]
            type, code, checksum, recieved_id, sequence = struct.unpack('bbHHh', icmp_header)

            if recieved_id == packet_id:
                round_trip_time = (time_received - start_time) * 1000  # Convert to milliseconds
                print(f"Reply from {addr[0]}: time={round_trip_time:.2f} ms")
                break
            else:
                print("Received packet with different ID, ignoring.")
                break


def ping(host, timeout=5):
    """Send an ICMP Echo Request to the specified host."""
    
    try:
        # Create a raw socket
        icmp = socket.getprotobyname("icmp")
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        
         # Create packet
        packet_id = os.getpid() & 0xFFFF  # Get the process ID
        packet = create_packet(packet_id)
    
        print(f"Sending packet to {host}...")
        sock.sendto(packet, (host, 1))  # Send packet to the host
    
    
        # Wait for a reply
        print("Packet sent, waiting for reply...")
        start_time = time.time()
        handle_response(sock, packet_id, start_time)
        
        # Set a timeout of 1 second for the socket
        sock.settimeout(timeout)
        
    except PermissionError:
        print("You need to run this script with administrative privileges.")
        sys.exit(1)
    
    except socket.timeout:
        print("Request timed out.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        sock.close()

if __name__ == "__main__":
    target_host = "8.8.8.8"  
    ping(target_host)