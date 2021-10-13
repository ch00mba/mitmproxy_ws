#!mitmdump -s
import mitmproxy.addonmanager
import mitmproxy.connections
import mitmproxy.http
import mitmproxy.log
import mitmproxy.tcp
import mitmproxy.websocket
import mitmproxy.proxy.protocol
import logging
from logging import handlers
from pprint import pprint
from mitmproxy.utils import strutils, human
from throttler import Throttler
from time import time

rfh = logging.handlers.RotatingFileHandler(
    filename='/media/LogSpace/mitmdump.log',
    mode='a',
    maxBytes=0,
    backupCount=1,
    encoding=None,
    delay=0
)
logging.basicConfig(
    level=logging.INFO,
    # format="%(asctime)s %(message)s",
    format="%(message)s",
    datefmt="%y-%m-%d %H:%M:%S",
    handlers=[
        rfh
    ]
)
logger = logging.getLogger('main')

class SniffWebSocket:
    def __init__(self):
        self.buckets = dict()
        self.rate = 20000000000 # per interval
        self.interval = 6000 # seconds
        pass

    # Websocket lifecycle
    def websocket_handshake(self, flow: mitmproxy.http.HTTPFlow):
        """
            Called when a client wants to establish a WebSocket connection. The
            WebSocket-specific headers can be manipulated to alter the
            handshake. The flow object is guaranteed to have a non-None request
            attribute.
        """

    def websocket_start(self, flow: mitmproxy.websocket.WebSocketFlow):
        """
            A websocket connection has commenced.
        """

    def websocket_message(self, flow: mitmproxy.websocket.WebSocketFlow):
        """
            Called when a WebSocket message is received from the client or
            server. The most recent message will be flow.messages[-1]. The
            message is user-modifiable. Currently there are two types of
            messages, corresponding to the BINARY and TEXT frame types.
        """
        # pprint (vars(flow))
        now = int(time())
        for flow_msg in flow.messages:
            if flow_msg.from_client:
                client_ip = flow.client_conn.address[0]

                if client_ip not in self.buckets.keys():
                    self.buckets[client_ip]=dict()
                    self.buckets[client_ip]['tokens'] = self.rate
                    self.buckets[client_ip]['last'] = now

                lapse = now - self.buckets[client_ip]['last']
                self.buckets[client_ip]['last'] = now

                self.buckets[client_ip]['tokens'] += lapse * self.rate // self.interval
                if self.buckets[client_ip]['tokens'] > self.rate:
                    self.buckets[client_ip]['tokens'] = self.rate

                if self.buckets[client_ip]['tokens'] > 0:
                    self.buckets[client_ip]['tokens'] -= 1

                    # logger.info("{timestamp} -> tokens: {tokens}, Client IP: {client_ip}, now: {ts_now}".format(
                    #     timestamp=human.format_timestamp_with_milli(flow_msg.timestamp),
                    #     tokens=self.buckets[client_ip]['tokens'],
                    #     client_ip=client_ip,
                    #     ts_now=now
                    # ))

                else:
                    # print(client_ip+" killed")
                    logger.info("{timestamp} {client} -> {type} {server} {t} {packet}".format(
                        timestamp=human.format_timestamp_with_milli(flow_msg.timestamp),
                        type=flow_msg.type,
                        client=human.format_address(flow.client_conn.address),
                        server=human.format_address(flow.server_conn.address),
                        endpoint=flow.handshake_flow.request.path,
                        t=self.buckets[client_ip]['tokens'],
                        packet="KILLED!!!"
                    ))
                    flow.kill()
                    return


    def websocket_error(self, flow: mitmproxy.websocket.WebSocketFlow):
        """
            A websocket connection has had an error.
        """

    def websocket_end(self, flow: mitmproxy.websocket.WebSocketFlow):
        """
            A websocket connection has ended.
        """

addons = [
    SniffWebSocket()
]

