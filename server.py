import socket
import os
import struct

ICMP_ECHO_REPLY = 0  # ICMP type for Echo Reply

def create_reply_packet(request_packet):
    """Create an ICMP Echo Reply packet."""
    # Unpack the received packet
    icmp_header = request_packet[20:28]
    type, code, checksum, packet_id, sequence = struct.unpack('!BBHHH', icmp_header)

    # Create the reply packet
    reply_header = struct.pack('!BBHHH', ICMP_ECHO_REPLY, 0, checksum, packet_id, sequence)
    return reply_header + request_packet[28:]  # Append the original data

def start_server():
    """Start the ICMP Echo server."""
    # Create a raw socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
    sock.bind(("", 0))  # Bind to all interfaces

    print("ICMP Echo server is running...")

    while True:
        # Receive packets
        request_packet, addr = sock.recvfrom(1024)
        print(f"Received message: {request_packet} from {addr}")

        # Create and send the reply packet
        reply_packet = create_reply_packet(request_packet)
        sock.sendto(reply_packet, addr)
        print(f"Sent reply to {addr}")

        # Check for a specific termination condition
        # Here we check if the payload contains the termination signal 's'
        if request_packet[28:29] == b's':  # Check the first byte of the payload
            print("Stopping server as termination signal received.")
            break

    sock.close()

if __name__ == "__main__":
    start_server()


