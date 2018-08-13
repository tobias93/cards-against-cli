import threading
import socket

from zeroconf import ServiceBrowser, ServiceStateChange, Zeroconf

from cac.client.scenes.select_server.list_box import ListBox, ListBoxItem
from cac.client.engine.game_object import Scene
from cac.client.engine.events import EventPropagation
from cac.client.engine.curses_text import render_text, \
    TextAlignment, VerticalTextAlignment


class Server():

    def __init__(self, name="",
                 zeroconf_server_name="", address="", port=1337):
        self.address = address
        self.name = name
        self.zeroconf_server_name = zeroconf_server_name
        self.port = port


class SelectServerScene(Scene):

    def __init__(self):
        super().__init__()

        # game
        self._game = None

        # server auto discovery
        self._discovered_servers = []
        self._discovered_servers_lock = threading.Lock()
        self._zeroconf = None
        self._browser = None
        self._discovery_enabled = False

        # discovered server selection
        self._server_list_box = ListBox()
        self._server_list_box_visible = False

    def start_scene(self, game):
        self._game = game
        try:
            self.start_discovery()
            self._discovery_enabled = True
        except Exception:
            pass

    def stop_scene(self):
        if self._discovery_enabled:
            self.stop_discovery()
            self._discovery_enabled = False

    def get_child_objects(self):
        if self._server_list_box_visible:
            return [self._server_list_box]
        else:
            return []

    def process_event(self, event):
        return EventPropagation.propagate_forward(self._server_list_box)

    def update(self, delta_time):

        # update the listbox contents
        with self._discovered_servers_lock:

            # items
            self._server_list_box.items = [
                ListBoxItem(srv.name, [f"{srv.address}:{srv.port}"], srv)
                for srv in self._discovered_servers
            ]

            # only make the listbox visible,
            # if there is actually something to show...
            self._server_list_box_visible = len(self._discovered_servers) > 0

        # reposition the list box
        w, h = self.size
        self._server_list_box.position = 0, 0
        self._server_list_box.size = w, h - 1

    def render(self, win):
        w, h = self.size
        win.erase()

        if not self._server_list_box_visible:
            render_text(
                win, "Searching for servers...", 0, 0, w, h,
                alignment=TextAlignment.CENTER,
                valignment=VerticalTextAlignment.CENTER
            )

    def start_discovery(self):
        self._zeroconf = Zeroconf()
        self._browser = ServiceBrowser(
            self._zeroconf,
            "_cac._tcp.local.",
            handlers=[self.on_service_state_change]
        )

    def stop_discovery(self):
        self.zeroconf.close()

    def on_service_state_change(self, zeroconf,
                                service_type, name,
                                state_change):
        with self._discovered_servers_lock:

            # remove it
            self._discovered_servers = [
                server
                for server in self._discovered_servers
                if server.zeroconf_server_name != name
            ]

            # add service
            if state_change is ServiceStateChange.Added:
                info = zeroconf.get_service_info(service_type, name)
                if info:
                    addr = socket.inet_ntoa(info.address)
                    port = info.port
                    zc_name = name
                    name = "Unnamed Server"
                    if info.properties and b"name" in info.properties:
                        name = info.properties[b"name"].decode("utf-8")
                    self._discovered_servers.append(
                        Server(name, zc_name, addr, port))
