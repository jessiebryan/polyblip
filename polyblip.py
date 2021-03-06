import untangle
import os
from sys import platform
from bottle import route, run, request

#Determine which version of the notification class to import.
if platform == "win32" or platform == "cygwin":
    from winballoontip import balloon_tip
elif platform == "linux" or platform == "linux2":
    from linuxballoontip import balloon_tip
else:
    print "System OS not supported"
    exit()

#Var to hold the dir of this file.
loc = os.path.dirname(os.path.abspath(__file__)) + '/'

# This file will log all registered call events
logfile = loc + "call.log"

# This file should be present at launch with the
# prerequisite server information on the first line.
ip_filename = loc + "ip.conf"
ip_address = ""
port = ""


try:
    ip_file = open(ip_filename)
    for line in ip_file:
        ip_address = line.split(':')[0]
        port = line.split(':')[1]
except IOError:
    print "IP file not found or corrupted! Create a file called '" + ip_filename + "' with your address and port."
    print "The format is address:port, e.g. 127.0.0.1:12345"
    exit()


@route('/', method='POST')
def index():
    # out lets us know if it's an outgoing call or not
    out = False
    postdata = request.body.read()

    # Parse the XML packet we get from the phone
    parsed = untangle.parse(postdata)

    # Write it to the log file
    lfile = open(logfile, 'ab+')
    lfile.write(postdata + "\n\n")
    lfile.close()

    # Figure out if we're dealing with an incoming or outgoing call
    if "OutgoingCallEvent" in postdata:
        out = True

    # Extract names. If it's not an outgoing call, it's probably incoming
    # (or corrupted data, which we're not accounting for here)
    if out:
        call_to = parsed.PolycomIPPhone.OutgoingCallEvent.CalledPartyName.cdata
        call_from = "You"
        call_time = parsed.PolycomIPPhone.OutgoingCallEvent.TimeStamp.cdata
        call_type = "Outgoing"
        print call_type + " call."
        print "Call from: ", call_from
        print "Call to: ", call_to
    else:
        call_from = parsed.PolycomIPPhone.IncomingCallEvent.CallingPartyName.cdata
        call_to = parsed.PolycomIPPhone.IncomingCallEvent.CalledPartyName.cdata
        call_time = parsed.PolycomIPPhone.IncomingCallEvent.TimeStamp.cdata
        call_type = "Incoming"
        print "Call from: ", call_from
        print "Call to: ", call_to
        print call_type + " call."
    print "Time: ", call_time

    # Show alert for incoming calls on the desktop.
    if not out:
        balloon_tip(call_type, "Call from " + call_from)
    return 0

# Run the listening Bottle web server
run(host=ip_address, port=port, debug=True)
