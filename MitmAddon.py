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
    filename='/mitmdump.log',
    mode='a',
    maxBytes=1000000000,
    backupCount=0,
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
        self.rate = 20000000 # per second
        self.tokens = 3600
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
        for flow_msg in flow.messages:
            #pprint (vars(flow_msg))
            direction="->" if flow_msg.from_client else "<-",

            client_ip = flow.client_conn.address[0]
            # pass

            now = time()

            if client_ip not in self.buckets.keys():
                self.buckets[client_ip]=dict()
                self.buckets[client_ip]['tokens'] = self.rate
                self.buckets[client_ip]['last'] = now

            lapse = now - self.buckets[client_ip]['last']
            self.buckets[client_ip]['last'] = now

            self.buckets[client_ip]['tokens'] += lapse * self.rate
            if self.buckets[client_ip]['tokens'] > self.rate:
                self.buckets[client_ip]['tokens'] = self.rate

            if self.buckets[client_ip]['tokens'] >= self.tokens:
                # print("{t} {timestamp} {client} {direction} {type} {server}".format(
                #     timestamp=flow_msg.timestamp,
                #     type=flow_msg.type,
                #     client=human.format_address(flow.client_conn.address),
                #     server=human.format_address(flow.server_conn.address),
                #     direction="->" if flow_msg.from_client else "<-",
                #     endpoint=flow.handshake_flow.request.path,
                #     t=self.buckets[client_ip]['tokens'],
                # ))
                logger.info("{timestamp} {client} {direction} {type} {server} {t} {packet}".format(
                    timestamp=human.format_timestamp_with_milli(flow_msg.timestamp),
                    type=flow_msg.type,
                    client=human.format_address(flow.client_conn.address),
                    server=human.format_address(flow.server_conn.address),
                    direction="->" if flow_msg.from_client else "<-",
                    endpoint=flow.handshake_flow.request.path,
                    t=self.buckets[client_ip]['tokens'],
                    packet=flow_msg.content
                ))

                self.buckets[client_ip]['tokens'] -= self.tokens
                # return True

            else:
                # print(client_ip+" killed")
                logger.info("{timestamp} {client} {direction} {type} {server} {t} {packet}".format(
                    timestamp=human.format_timestamp_with_milli(flow_msg.timestamp),
                    type=flow_msg.type,
                    client=human.format_address(flow.client_conn.address),
                    server=human.format_address(flow.server_conn.address),
                    direction="->" if flow_msg.from_client else "<-",
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
