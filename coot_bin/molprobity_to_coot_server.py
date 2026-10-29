# This is not a standalone script.
# It must be run in coot using the run_script(r"/path/to/molprobity_to_coot_server.py")
# (plumage.py does this for you, and must be run first as it sets up the plumage_compat module.)
# Then it used in conjunction with a separate molprobity_to_coot.py script.
# Part of coot_plumage (github.com/robertstass/coot_plumage). Written by Robert Stass, Bowden group, STRUBI/OPIC (2024)
############################################

previous_key = "q"
next_key = "w"

############################################

import plumage_compat as pc  # holds COOT_VERSION (set in plumage.py) and the version-specific wrappers.

# The residue list that is sent from molprobity_to_coot.py and the position in that list.
residue_list = None
current_residue_index = 0

def update_residue_list(residues):
    global residue_list
    global current_residue_index
    residue_list = residues
    current_residue_index = 0
    to_residue(0)

def to_residue(add=0):
    global current_residue_index
    if residue_list is None:
        pc.coot.add_status_bar_text("Load residue list first! (eg with the molprobity_to_coot.py script).")
        return
    current_residue_index = current_residue_index + add
    if current_residue_index >= len(residue_list):
        current_residue_index = current_residue_index - add
        pc.coot.add_status_bar_text("End of residue list.")
    elif current_residue_index < 0:
        current_residue_index = 0
        pc.coot.add_status_bar_text("Start of residue list.")
    else:
        residue = residue_list[current_residue_index]
        pc.coot.set_go_to_atom_chain_residue_atom_name(residue[0], residue[1], "CA")
        pc.coot.add_status_bar_text("Go to: %s %d. Residue %d of %d in list." % (residue[0], residue[1], current_residue_index+1, len(residue_list)))


def go_to_next_residue():
    to_residue(1)

def go_to_previous_residue():
    to_residue(-1)


allowed_methods = {"update_residue_list": update_residue_list}

import socket
import traceback
import sys
import os
import threading
import coot  # the coot module. The xml-rpc server looks up the functions to run in here.
try:
    from SimpleXMLRPCServer import SimpleXMLRPCServer  # python 2 (Coot 0.9)
    import Queue as queue
except ImportError:
    from xmlrpc.server import SimpleXMLRPCServer  # python 3 (Coot 1)
    import queue

command_queue = queue.Queue()

class coot_xmlrpc_server (SimpleXMLRPCServer) :
    def __init__ (self, addr) :
        SimpleXMLRPCServer.__init__(self, addr, logRequests=0, allow_none=True)
        self.timeout = 0.01
    def _dispatch (self, method, params) :
        result = -1
        func = None
        if hasattr(coot, method) :
            func = getattr(coot, method)
        elif method in allowed_methods:
            func = allowed_methods[method]
        #elif method in globals().keys(): #removed to make it more secure.
        #    func = globals()[method]
        if not hasattr(func, "__call__") :
            print("%s is not a callable object!" % method)
        else :
            command_queue.put((func, params))
            return "Command enqueued: {}".format(method)
        return None

    def serve(self):
        while True:
            self.handle_request()

def is_port_in_use(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    in_use = s.connect_ex(("127.0.0.1", port)) == 0
    s.close()
    return in_use

def start_server(port):
    try:
        xmlrpc_server = coot_xmlrpc_server(("127.0.0.1", port))
        xmlrpc_server.socket.settimeout(0.01)
        xmlrpc_server.serve()
    except Exception as e:
        print("Error starting XML-RPC server:")
        print(str(e))


port = 5007
for i in range(0,10): #in case port already in use
    if is_port_in_use(port):
        port = port+1
    else:
        break
server_thread = threading.Thread(target=start_server, args=[port])
server_thread.daemon = True  # This allows the thread to exit when the main program ends
server_thread.start()
print("xml-rpc server running on port %d in a background thread" % port)
print("Send a list of residues using the molprobity_to_coot.py script.")
print("Then cycle through residues using the %s and %s keys" % (previous_key, next_key))


def process_queue():
    while not command_queue.empty():
        func, params = command_queue.get()
        try:
            result = func(*params)
            print("Executed: %s Result: %s" % (func.__name__, result))
        except Exception as e:
            print("Error executing {}: {}".format(func.__name__, str(e)))
            traceback.print_exc()
    return True  # Keeps the timeout running

# Schedule the queue processing to run every 10ms in the main (GUI) thread (non-blocking).
# This is what allows the xml-rpc thread to safely hand commands over to coot.
pc.idle_add(10, process_queue)


# on the client side
# import xmlrpc.client; coot = xmlrpc.client.ServerProxy("http://127.0.0.1:2668")
# coot.set_map_radius_em(40) # or any other coot function


pc.toolbar_button("Previous residue", go_to_previous_residue, icon="go-to-atom.png", tooltip="Cycle through supplied residue list. Supply this list via an external script (to 127.0.0.1/%d) such as molprobity_to_coot.py. Part of the coot_plumage set of scripts. Hotkey: %s" % (port, previous_key))
pc.add_key_binding("Previous residue", previous_key, lambda: go_to_previous_residue())

pc.toolbar_button("Next residue", go_to_next_residue, icon="go-to-atom.png", tooltip="Cycle through supplied residue list. Supply this list via an external script (to 127.0.0.1/%d) such as molprobity_to_coot.py. Part of the coot_plumage set of scripts. Hotkey: %s" % (port, next_key))
pc.add_key_binding("Next residue", next_key, lambda: go_to_next_residue())
