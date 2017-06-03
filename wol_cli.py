import sys
import socket  
  
def SendWolRequest(host, port, msg):
    address = (host, port)  
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
    s.sendto(msg, address)  
    s.close()  

def Usage(prog):
    print 'Usage: %s host port msg(name | mac)...' % prog

def IsMacAddr(string):
    if len(string) == 17 and (string[2] == ':' or string[2] == '-'):
        return True

    return False

if '__main__' == __name__:
    argv = sys.argv

    if len(argv) < 4:
        Usage(argv[0])
        sys.exit(0)

    host = argv[1]
    port = int(argv[2])

    magic_header = 'WOL'
    option = ''

    for arg in argv[3:]:
        if IsMacAddr(arg):
            option = 'm' # mac
        else:
            option = 'n' # name

        msg = magic_header + option + arg
        SendWolRequest(host, port, msg)
