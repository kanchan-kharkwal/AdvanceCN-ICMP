import os
import socket
import struct
import time

ICMP_ECHO_REQUEST = 8  # ICMP type for Echo Request


def calculate_checksum(data):
    """Calculate the checksum of the packet."""
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


def create_icmp_packet(packet_id):
    """Create an ICMP Echo Request packet."""
    header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, 0, packet_id, 1)
    data = b'Hello!'  # Payload
    checksum = calculate_checksum(header + data)
    header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, socket.htons(checksum), packet_id, 1)
    return header + data


def ping(host):
    """Send an ICMP Echo Request to the host and calculate RTT."""
    try:
        print(f"Sending packets to {target}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
    except PermissionError:
        print("Run the script with administrative privileges.")
        return

    packet_id = os.getpid() & 0xFFFF  # Unique identifier for the packet
    packet = create_icmp_packet(packet_id)

    try:
        print("Packet sent, waiting for reply...")
        sock.sendto(packet, (host, 1))
        start_time = time.time()
        print("Waiting for response...")

        sock.settimeout(3)
        reply, addr = sock.recvfrom(1024)
        rtt = (time.time() - start_time) * 1000  # Round-Trip Time in ms

        print(f"Reply from {addr[0]}: time={rtt:.2f} ms")
    except socket.timeout:
        print("Request timed out.")
    finally:
        sock.close()


if __name__ == "__main__":
    target = "8.8.8.8"  # Google Public DNS
    ping(target)
