from cac.server.announcement import start_announcing, stop_announcing
from time import sleep
import logging
import os

"""
Starts the Cards Against Cli server.
The complete configuration is done via environment variables.

CAC_ANNOUNCE_INTERFACES
            comma seperated list of network interfaces
            on which the server should be discoverable (using avahi/bonjour).
            By default, all availible network interfaces will be used.
CAC_ANNOUNCE_SERVER_NAME
            Human readable server name as shown by the client.
            Default value: "My Cards against Cli Server"
"""


def main():
    """
    Brings up the complete cac server.
    """

    # start announcing zeroconf service
    server_name = "My Cards against Cli Server"
    if "CAC_ANNOUNCE_SERVER_NAME" in os.environ:
        server_name = os.environ["CAC_ANNOUNCE_SERVER_NAME"]
    announcers = start_announcing(server_name, 9852)

    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass

    stop_announcing(announcers)


if __name__ == "__main__":
    # logging
    logging.basicConfig(
        format='%(levelname)s - %(name)s - %(message)s',
        level=logging.DEBUG
    )

    main()
