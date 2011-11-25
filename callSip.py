# $Id$
#
# SIP account and registration sample. In this sample, the program
# will block to wait until registration is complete
#
# Copyright (C) 2003-2008 Benny Prijono <benny@prijono.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA 
#
import sys
import pjsua as pj
import threading
import time

#sip_srv = "192.168.110.30"
sip_srv = "10.0.2.7"
sip_user = "101"
sip_pass = "1qaz2wsx"
c_c = ""

def log_cb(level, str, len):
    print str,

class MyAccountCallback(pj.AccountCallback):
    sem = None

    def __init__(self, account):
        pj.AccountCallback.__init__(self, account)

    def wait(self):
        self.sem = threading.Semaphore(0)
        self.sem.acquire()

    def on_reg_state(self):
        if self.sem:
            if self.account.info().reg_status >= 200:
                self.sem.release()
    
    # Notification on incoming call
    def on_incoming_call(self, call):
        global current_call 
        if current_call:
            call.answer(486, "Busy")
            return
            
        print "Incoming call from ", call.info().remote_uri
        print "Press 'a' to answer"

        current_call = call

        call_cb = MyCallCallback(current_call)
        current_call.set_callback(call_cb)

        current_call.answer(180)
        
# Callback to receive events from Call
class MyCallCallback(pj.CallCallback):

    def __init__(self, call=None):
        pj.CallCallback.__init__(self, call)

    # Notification when call state has changed
    def on_state(self):
        global current_call
        print "Call with", self.call.info().remote_uri,
        print "is", self.call.info().state_text,
        print "last code =", self.call.info().last_code, 
        print "(" + self.call.info().last_reason + ")"
        
        if self.call.info().state == pj.CallState.DISCONNECTED:
            current_call = None
            print 'Current call is', current_call

    # Notification when call's media state has changed.
    def on_media_state(self):
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            # Connect the call to sound device
            call_slot = self.call.info().conf_slot
            c_c = call_slot
            pj.Lib.instance().conf_connect(call_slot, 0)
            pj.Lib.instance().conf_connect(0, call_slot)
            print "Media is now active"
            #print "Connecting Player"
            #m_plyr = pj.Lib.instance().create_player(sys.argv[2])
            #m_slot = pj.Lib.instance().player_get_slot(m_plyr)
            #pj.Lib.instance().conf_connect(m_slot, call_slot)
            #pj.Lib.instance().conf_connect(m_slot, 0)
        else:
            print "Media is inactive"

# Function to make call
def make_call(uri):
    try:
        print "Making call to", uri
        return acc.make_call(uri, cb=MyCallCallback())
    except pj.Error, e:
        print "Exception: " + str(e)
        return None

lib = pj.Lib()

def play_wav():
    if len(sys.argv) > 2:
        m_plyr = lib.create_player(sys.argv[2])
        m_slot = lib.player_get_slot(m_plyr)
        c_slot = current_call.info().conf_slot
        lib.conf_connect(m_slot, c_slot)

try:
    lib.init(log_cfg = pj.LogConfig(level=0, callback=log_cb))
    lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(5080))
    lib.start()

    acc = lib.create_account(pj.AccountConfig(sip_srv, sip_user, sip_pass))

    acc_cb = MyAccountCallback(acc)
    acc.set_callback(acc_cb)
    acc_cb.wait()

    print "\n"
    print "Registration complete, status=", acc.info().reg_status, \
          "(" + acc.info().reg_reason + ")"
    
    
    if len(sys.argv) > 1:
        lck = lib.auto_lock()
        current_call = make_call(sys.argv[1])
        print 'Current call is', current_call
        #while (current_call.info().media_state <> pj.MediaState.ACTIVE):
        #    time.sleep(1)
        #    print "Stuck because: ", current_call.info().media_state
        time.sleep(10)
        print "Connecting Player"
        #call_slot = current_call.info().conf_slot
        #print "call_slot", call_slot
        #m_plyr = lib.create_player(sys.argv[2])
        #m_slot = lib.player_get_slot(m_plyr)
        #lib.conf_connect(m_slot, call_slot)
        #lib.conf_connect(m_slot, 0)
        del lck
    time.sleep(10)
    call_slot = current_call.info().conf_slot
    print "call_slot", call_slot
    m_plyr = lib.create_player(sys.argv[2])
    m_slot = lib.player_get_slot(m_plyr)
    lib.conf_connect(m_slot, call_slot)
    lib.conf_connect(m_slot, 0)
    
    print "\nPress ENTER to quit"
    sys.stdin.readline()

    lib.destroy()
    lib = None

except pj.Error, e:
    print "Exception: " + str(e)
    lib.destroy()

