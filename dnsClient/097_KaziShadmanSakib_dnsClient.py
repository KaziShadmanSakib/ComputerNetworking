import random
import socket
import sys
from dnslib import DNSRecord

#selects random root server
def randomRootServer():
    rootServers=["198.41.0.4",
                  "199.9.14.201",
                  "192.33.4.12",
                  "199.7.91.13",
                  "192.203.230.10",
                  "192.5.5.241",
                  "192.112.36.4",
                  "198.97.190.53",
                  "192.36.148.17",
                  "192.58.128.30",
                  "193.0.14.129",
                  "199.7.83.42",
                  "202.12.27.33"]
    return random.choice(rootServers)

#returns query type A/NS/CNAME/MX
def query_Type(name):
    if name=="A":
        return b"\x00\x01"
    elif name=="NS":
        return b"\x00\x02"
    elif name=="MX":
        return b"\x00\x0f"
    elif name=="CNAME":
        return b"\x00\x05"

#encodes request
def makeRequest(url, type):
    requestHeader = b"\x00\x00" + b"\x00\x00" + b"\x00\x01" + b"\x00\x00" +b"\x00\x00" +b"\x00\x00"

    queryType = query_Type(type)
    queryClass = b"\x00\x01"

    requestQuestion = bytes('', 'utf-8')
    for parts in url:
        requestQuestion += len(parts).to_bytes(1, byteorder='big') + parts.encode()
    requestQuestion += b"\x00" + queryType + queryClass

    request = requestHeader + requestQuestion
    return request

#dns resolver to get the responses of the requests that are made
def dnsResolver(url, queryType, client,root_server):
    urlS = url.split(".")
    curServer = root_server
    for i in range(len(urlS)-1, 0, -1):
        queryName = '.'.join(urlS[i:])
      
        print(f"--> Contacting root ({curServer}) for NS of {queryName}")

        request = makeRequest(urlS[i:], "NS")
        client.sendto(request, (curServer, 53))
        byteResponse, ip_address = client.recvfrom(2048)
        response = DNSRecord.parse(byteResponse)
        if len(response.ar) > 0: #additional resources (A type)
            if int(response.ar[0].rtype) == 28: #ipv6
                print(f"<-- ERROR")
                return
            curServer = str(response.ar[0].rdata)
            print(f"<-- NS of {queryName} is {curServer}")
        else:
            print(f"<-- ERROR No NS for {queryName}")
            return

    print(f"--> Contacting {curServer} for {queryType} of {url}")
    request = makeRequest(urlS, queryType)
    client.sendto(request, (curServer, 53))
    byteResponse, ip_address = client.recvfrom(2048)
    response = DNSRecord.parse(byteResponse)
    if int(response.rr[0].rtype) == 5: #cname
        cName = str(response.rr[0].rdata) #response resources
        cName = cName[:-1] if cName[-1] == "." else cName
        print(f"<-- CNAME of {url} is {cName}")
        return dnsResolver(cName, queryType, client,root_server)

#main function begins here
invoke = input()
queryType, url = invoke.split()
queryType = queryType.upper()

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dnsResolver(url, queryType, client,randomRootServer())
except Exception as error:
    print(error)
    sys.exit()