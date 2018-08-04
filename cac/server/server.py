from announcement import start_announcing, stop_announcing
from time import sleep
import logging

def main():
    """
    Brings up the complete cac server.
    """
    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    # logging
    logging.basicConfig(format='%(levelname)s - %(name)s - %(message)s', level=logging.DEBUG)
    announcers = start_announcing("My Cards against Cli Server", 9852)
    main()
    stop_announcing(announcers)
