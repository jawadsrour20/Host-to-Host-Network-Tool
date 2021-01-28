#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Note that this file was submitted late by the members who worked on traceroute

They seemed to have modified some things in the ping as well at the last minute

For that, we can't have it merged with our project files and the GUI

"""

import socket, struct, os, time

IDX_TYPE = 20
MAX_TTL  = 64
MAX_ATTEMPT = 4

class PingTool(object):
    #initalizes a PingTool objectwith 3 parameters (count default is 20 and timeout default is 2)
    def __init__(self,target_server, count=20, timeout=1): 
        self.target_server = target_server 
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
    
    def ip_from_bytes(self,b):
        ip = ""
        for byte in b:
            ip += str(byte) + "."
        return ip[:-1] # drop the last dot
    
    def analyse_response(self, rData):
        #print("  Ping: {}ms".format(ping)) #Is this ping for google or each router? if google, remove
        ICMP_type = rData[IDX_TYPE]
        source_ip_bytes = rData[12: 16]
        source_ip_str_rep = self.ip_from_bytes(source_ip_bytes)
        print("  Responder: {}".format(source_ip_str_rep))
        if ICMP_type == 0:
            print("  Destination was successfully reached.")
    
        print("\n")
        return ICMP_type == 0

    def send_echo_req(self,icmpsocket,ID):
        #function that sends the icmp packet with the necessary headers and data payload
        ICMP_TYPE = 8
        sequence_num = 1
        target_address  =  socket.gethostbyname(self.target_server) 
        dummy_checksum = 0
        #When calculating checksum we usually set a "dummy" checksum as 0 that
        #is then replaced with the calculated checksum after calculations are dealt with
        pack_header = struct.pack("bbHHh", ICMP_TYPE, 0, dummy_checksum, ID, sequence_num)
        #this converts the necessary information (int, strings etc.) into bytes that can be understood by the network
        payload = (184) * "Q" 
        payload = struct.pack("d", time.time()) + bytes(payload.encode('utf-8')) 
        pack_checksum = self.checkSum(pack_header + payload) 
        #call to checkSum function to be ready for sending the echo request 
        pack_header = struct.pack( "bbHHh", ICMP_TYPE, 0, socket.htons(pack_checksum), ID, sequence_num ) 
        packet = pack_header + payload 
        icmpsocket.sendto(packet, (target_address, 1)) 
    
    def rec_echo(self,start,icmpsocket,ID,timeout):
        while True: 
            icmpsocket.settimeout(start + timeout - time.time())

            try:
                recv_packet, addr = icmpsocket.recvfrom(4096) #buffer size of 1024 bytes
                time_received = time.time()
                icmp_header = recv_packet[20:28]
                icmp_type, code, checksum, packet_ID, sequence = struct.unpack("bbHHh", icmp_header) 
            
            #   confirm that this packet is intended for this host using the identification provided in header
                time_sent = struct.unpack("d", recv_packet[28:36])[0] 
                delay = time_received - time_sent
                return delay, recv_packet
            except Exception:
                return 
            
            
        
    def single_ping(self, ttl = None):
        icmp = socket.getprotobyname("icmp")
        #Create the ICMP Socket
        icmp_sock= socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        if(ttl != None): #Riwa & Jaafar
            icmp_sock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        # os.getpid() --> gets process id from the operating system
        PID = os.getpid() & 0xFFFF
        self.send_echo_req(icmp_sock, PID)
        #Send the echo request
        #Stores time that the packet was sent to be used for delay calculations
        try:
            start = time.time()
            pack_delay, recv_packet = self.rec_echo(start,icmp_sock, PID, self.timeout)
            #Receive echo reply and then close the socket as it is no longer needed
            icmp_sock.close()
            return pack_delay, recv_packet #packet delay recieved from the echo reply 
        except Exception:
            icmp_sock.close()
            return (None, None)
    
    def ping(self):
        loss_count = 0
        print ("Pinging", self.target_server, "...")
        for i in range(0, self.count, 1):
            #call the single_ping function count times
            pack_delay, recv_packet = self.single_ping()
            if pack_delay  ==  None: 
                print ("Request timed out...")
                loss_count += 1
            else:
                pack_delay *= 1000 
                print ("RTT achieved in: ",pack_delay, " ms") 
        packet_loss = loss_count/self.count * 100
        
        print('Packet loss was ', packet_loss,'%')
#@authors: Riwa Karaki & Jaafar Alawieh
#the following traceroute function, along with enhancements for rec_echo and others to accomodate it, were written to display routes taken by the packets across our IP network.
#reference for some parts were from GitHub user siyuliu0329's submitted codes
    def traceroute(self):

        dest = socket.gethostbyname(self.target_server)
        print("MAX_TTL={}\n".format(MAX_TTL))
        recv_packet = None
        reached = False
        ttl = 1
        attempt_n = 1

        while recv_packet == None or reached == False:
            if attempt_n == 1:
                print("{} Sending packet: \n      (domain='{}', ip={}, seq={}, ttl={})".format(ttl , self.target_server, dest, ttl, ttl))
            
            temp, recv_packet = self.single_ping(ttl)
            if recv_packet == None:
                # if timed out, try again
                print("      Request has timed out, rerunning for {} out of {} times... (seq and ttl={})".format(attempt_n, MAX_ATTEMPT, ttl))
                attempt_n += 1

                if attempt_n > MAX_ATTEMPT:
                    print("  We have reached the maximum number of assigned attempts, skipping to next hop...\n")
                    ttl += 1
                    attempt_n = 1
                continue
                

            else:
                attempt_n = 1# recovered, reset number of attempts
                reached = self.analyse_response(recv_packet)
            if not reached:
                ttl += 1

            if ttl > MAX_TTL:
                print("Max ttl reached, terminating...")
                break
        if ttl==1:
            print("There was only {} hop in total".format(ttl))
        else:
            print("There were {} hops in total".format(ttl))

if __name__ == "__main__":
    target_host = 'google.com' 

    # # ping and packet loss test
    pinging = PingTool(target_host) 
    # pinging.ping() 
    # helping = PingTool(target_host) 
    # traceroute 
    pinging.traceroute()


            
    