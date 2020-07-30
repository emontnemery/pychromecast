"""
Example on how to use the Multizone (Audio Group) Controller

"""

import argparse
import logging
import sys
import time

import pychromecast
from pychromecast.controllers.multizone import MultizoneController
import zeroconf

# Change to the name of your Chromecast
CAST_NAME = "Whole house"

parser = argparse.ArgumentParser(
    description="Example on how to use the Multizone Controller to track groupp members."
)
parser.add_argument("--show-debug", help="Enable debug log", action="store_true")
parser.add_argument("--show-zeroconf-debug", help="Enable zeroconf debug log", action="store_true")
parser.add_argument(
    "--cast", help='Name of speaker group (default: "%(default)s")', default=CAST_NAME
)
args = parser.parse_args()

if args.show_debug:
    logging.basicConfig(level=logging.DEBUG)
if args.show_zeroconf_debug:
    print("Zeroconf version: " + zeroconf.__version__)
    logging.getLogger("zeroconf").setLevel(logging.DEBUG)


class connlistener:
    def __init__(self, mz):
        self._mz = mz

    def new_connection_status(self, connection_status):
        """Handle reception of a new ConnectionStatus."""
        if connection_status.status == "CONNECTED":
            self._mz.update_members()


class mzlistener:
    def multizone_member_added(self, uuid):
        print("New member: {}".format(uuid))

    def multizone_member_removed(self, uuid):
        print("Removed member: {}".format(uuid))

    def multizone_status_received(self):
        print("Members: {}".format(mz.members))


chromecasts, browser  = pychromecast.get_listed_chromecasts(friendly_names=[args.cast])
if not chromecasts:
    print('No chromecast with name "{}" discovered'.format(args.cast))
    sys.exit(1)

cast = chromecasts[0]
# Add listeners
mz = MultizoneController(cast.uuid)
mz.register_listener(mzlistener())
cast.register_handler(mz)
cast.register_connection_listener(connlistener(mz))

# Start socket client's worker thread and wait for initial status update
cast.wait()

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        break

# Shut down discovery
pychromecast.discovery.stop_discovery(browser)
