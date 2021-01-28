"""
Created on Mon Nov 23 21:03:48 2020

@author: YorgoBS & JawadSrour
"""
import socket, struct, os, time

#pip3 install socket struct os time threading time iza she whde na2sa:P
# This program must be run as root to function
# For MAC users, just use the command "sudo" as follows:
# sudo python3 MyPing.py

'''
    percetnage packet loss = (sent_packets - received_packets)/sent_packets * 100

    Delay = RTT = difference in time between send and receive packets

    sequence number helps to match replies with requests within the process. That is necessary to calculate the RTT (round-trip time) and to detect unanswered pings.

'''


'''
    The following prgram is built based on the module of the Ping model
    It is also similar to the original ping model in the  ICMP echo request and ICMP echo reply
    
    The purpose of this program is to find the time delay and the packet loss percentage when sending and receiving packets for a user chosen server
    
    you can either input the server's DNS or the IP address
    
    Testing with loopback address
    
    The program uses the following libraries:
    - multi-threading
    - socket programming
    - struct
    - os  (to get the process id when sending an echo request)
    - time (used to find the delay between sending and receiving packets to the server)

'''

####################################################################################################################################################################################################################################
####################################################################################################################################################################################################################################

class PingTool(object):
    #initalizes a PingTool objectwith 3 parameters (count default is 20 and timeout default is 2)
    def __init__(self,targer_server, count=20, timeout=2): 
        self.targer_server = targer_server 
        self.count = count 
        self.timeout = timeout
    
    #Checksum function for packet error detection 
    #reference for checksum : mje349, GitHub
    def checkSum(self, src_data):
        summation = 0
        count = 0
        max_count = (len(src_data)/2)*2
        
        while count<max_count:
            thisVal = src_data[count + 1]*256 + src_data[count] 
            summation = summation + thisVal 
            summation = summation & 0xffffffff  
            count += 2
        if max_count<len(src_data):
            summation = summation + ord(src_data[-1])
            summation = summation & 0xffffffff
        summation = (summation >> 16)  +  (summation & 0xffff) 
        summation = summation + (summation >> 16) 
        result_sum = ~summation 
        result_sum = result_sum & 0xffff 
        result_sum = result_sum >> 8 | (result_sum << 8 & 0xff00) 
        return result_sum
    
    def send_echo_req(self,icmpsocket,ID):
        #function that sends the icmp packet with the necessary headers and data payload
        sequence_num = 1
        icmp_type = 8 #Type for ICMP Echo Request
        target_address  =  socket.gethostbyname(self.targer_server) 
        dummy_checksum = 0
        #When calculating checksum we usually set a "dummy" checksum as 0 that
        #is then replaced with the calculated checksum after calculations are dealt with
        pack_header = struct.pack("bbHHh", icmp_type, 0, dummy_checksum, ID, sequence_num)
        #this converts the necessary information (int, strings etc.) into bytes that can be understood by the network
        payload = (184) * "Q" 
        payload = struct.pack("d", time.time()) + bytes(payload.encode('utf-8')) 
        pack_checksum = self.checkSum(pack_header + payload) 
        #call to checkSum function to be ready for sending the echo request 
        pack_header = struct.pack( "bbHHh", icmp_type, 0, socket.htons(pack_checksum), ID, sequence_num ) 
        packet = pack_header + payload 
        icmpsocket.sendto(packet, (target_address, 1))
    
    def rec_echo(self,start,icmpsocket,ID,timeout):
        while True: 
            icmpsocket.settimeout(start + timeout - time.time()) 
            try:
                recv_packet, addr = icmpsocket.recvfrom(1024) #buffer size of 1024 bytes
                time_received = time.time()
                icmp_header = recv_packet[20:28]
                icmp_type, code, checksum, packet_ID, sequence = struct.unpack("bbHHh", icmp_header) 
                if packet_ID == ID: 
                #confirm that this packet is intended for this host using the identification provided in header
                    time_sent = struct.unpack("d", recv_packet[28:36])[0] 
                    return time_received - time_sent
            except Exception:
                return #Timeout
            
    def single_ping(self):
        icmp = socket.getprotobyname("icmp")
        #Create the ICMP Socket
        icmp_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        pID = os.getpid() & 0xFFFF
        # os.getpid() --> gets process id from the operating system
        self.send_echo_req(icmp_sock, pID)
        #Send the echo request
        start = time.time()
        #Stores time that the packet was sent to be used for delay calculations
        pack_delay = self.rec_echo(start,icmp_sock, pID, self.timeout)
        #Receive echo reply and then close the socket as it is no longer needed
        icmp_sock.close()
        return pack_delay #packet delay recieved from the echo reply 
        

    def ping(self):


        success = []
        loss_count = 0
        print ("Pinging", self.targer_server, "...")
        for i in range(0, self.count, 1):
            #call the single_ping function count times
            pack_delay = self.single_ping()
            if pack_delay  ==  None:
                print ("Request timed out...")
                loss_count += 1
            else:
                pack_delay *= 1000
                # print ("RTT achieved in: ",pack_delay, " ms")
                success.append(pack_delay)
            # if loss_count == self.count:
            #     break
        packet_loss = loss_count/self.count * 100
        success.append(packet_loss)
        # print('Packet loss was ', packet_loss,'%')

        return success

if __name__ == '__main__':
    target_host = 'google.com'
    pinging = PingTool(target_host)
    pinging.ping()