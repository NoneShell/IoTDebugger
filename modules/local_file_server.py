import http.server
import socketserver
import argparse
import logging
import os

from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from tftpy import TftpServer
import threading

def setup_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

class CustomHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        logging.info("%s - %s",
                     self.client_address[0],
                     self.requestline)

class CustomFTPHandler(FTPHandler):
    def log(self, msg, *args, **kwargs):
        text = msg % args
        logging.info("%s - %s",
                     self.remote_ip,
                     text)

class MultiServer:
    HTTP_PORT = 8080
    FTP_PORT = 8021
    TFTP_PORT = 8069
    ROOTFS = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../tools")

    def __init__(self, rootfs=None):
        self.http_server = None
        self.ftp_server = None
        self.tftp_server = None
        self.rootfs = rootfs if rootfs else self.ROOTFS
        os.chdir(self.rootfs)

    def start_http_server(self):
        handler = CustomHTTPHandler
        self.http_server = socketserver.TCPServer(("", self.HTTP_PORT), handler)
        self.http_server.serve_forever()

    def start_ftp_server(self):
        from pyftpdlib.authorizers import DummyAuthorizer
        handler = CustomFTPHandler
        authorizer = DummyAuthorizer()
        authorizer.add_anonymous(self.rootfs)
        handler.authorizer = authorizer
        self.ftp_server = FTPServer(("", self.FTP_PORT), handler)
        self.ftp_server.serve_forever()

    def start_tftp_server(self):
        self.tftp_server = TftpServer(self.rootfs)
        self.tftp_server.listen("0.0.0.0", self.TFTP_PORT)

    def run_all_servers(self):
        threading.Thread(target=self.start_http_server).start()
        threading.Thread(target=self.start_ftp_server).start()
        threading.Thread(target=self.start_tftp_server).start()

if __name__ == "__main__":
    setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rootfs", help="The root filesystem to serve", required=False)
    args = parser.parse_args()

    server = MultiServer(rootfs=args.rootfs)
    server.run_all_servers()