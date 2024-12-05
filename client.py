import os
import sys
import time
import socket
import struct

ICMP_ECHO_REQUEST = 8  # ICMP Echo Request Type


def calculate_checksum(data):
    """Compute the ICMP packet checksum."""
    checksum = 0
    count_to = (len(data) // 2) * 2
    for count in range(0, count_to, 2):
        val = data[count + 1] * 256 + data[count]
        checksum += val
    if count_to < len(data):
        checksum += data[-1]
    checksum = (checksum >> 16) + (checksum & 0xFFFF)
    checksum += (checksum >> 16)
    return ~checksum & 0xFFFF


def create_packet(packet_id, termination=False):
    """Build the ICMP packet."""
    header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, 0, packet_id, 1)
    data = b's' if termination else b'Hello, ICMP!'
    checksum = calculate_checksum(header + data)
    header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, socket.htons(checksum), packet_id, 1)
    return header + data


def send_ping(host, termination=False):
    """Send a single ICMP packet to the specified host."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
    except PermissionError:
        print("Run the script with administrative privileges.")
        sys.exit(1)

    packet_id = os.getpid() & 0xFFFF
    packet = create_packet(packet_id, termination)
    sock.sendto(packet, (host, 1))

    start_time = time.time()
    sock.settimeout(3)
    try:
        recv_packet, addr = sock.recvfrom(1024)
        elapsed_time = (time.time() - start_time) * 1000
        print(f"Reply from {addr[0]}: time={elapsed_time:.2f} ms")
    except socket.timeout:
        print("Request timed out.")
    finally:
        sock.close()
        
if __name__ == "__main__":
    target_host = "192.168.56.1"  #  target server's IP
    send_ping(target_host)  # Normal ping
    send_ping(target_host, termination=True)  # Termination signal
