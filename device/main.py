import network
import asyncio
import config
from webserver import Server


def start_ap():
    ap = network.WLAN(network.AP_IF)
    ap.active(False)
    ap.active(True)
    kwargs = dict(
        essid=config.SSID,
        channel=config.CHANNEL,
        hidden=config.HIDDEN,
        max_clients=config.MAX_CLIENTS,
    )
    if config.PASSWORD:
        kwargs.update(authmode=network.AUTH_WPA2_PSK, password=config.PASSWORD)
    else:
        kwargs.update(authmode=network.AUTH_OPEN)
    ap.config(**kwargs)
    ap.ifconfig((config.AP_IP, "255.255.255.0", config.AP_IP, config.AP_IP))
    print("AP up:", config.SSID, "hidden" if config.HIDDEN else "visible", ap.ifconfig())
    return ap


ap = start_ap()
srv = Server()

# Register routes. Add new challenge modules here as they're built.
import challenges
challenges.register(srv)

asyncio.run(srv.run(port=80))
