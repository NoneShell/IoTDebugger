
import http.server
import socketserver
import argparse 

from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from tftpy import TftpServer
import threading
import os 

cur_dir = os.path.dirname(os.path.realpath(__file__))

class MultiServer:
    HTTP_PORT = 8000
    FTP_PORT = 8021
    TFTP_PORT = 8069
    ROOTFS = os.path.join(os.path.dirname(cur_dir), "tools")

    def __init__(self, rootfs=None) -> None:
        self.http_server = None
        self.ftp_server = None
        self.tftp_server = None
        self.rootfs = rootfs if rootfs else self.ROOTFS

        os.chdir(self.rootfs)

    def start_http_server(self):
        handler = http.server.SimpleHTTPRequestHandler
        self.http_server = socketserver.TCPServer(("", self.HTTP_PORT), handler)
        print(f"HTTP server started at port {self.HTTP_PORT}")
        self.http_server.serve_forever()
    
    def start_ftp_server(self):
        from pyftpdlib.authorizers import DummyAuthorizer
        handler = FTPHandler
        authorizer = DummyAuthorizer()
        authorizer.add_anonymous(self.rootfs)
        handler.authorizer = authorizer
        self.ftp_server = FTPServer(("", self.FTP_PORT), handler)
        print(f"FTP server started at port {self.FTP_PORT}")
        self.ftp_server.serve_forever()

    def start_tftp_server(self):
        self.tftp_server = TftpServer(self.rootfs)
        self.tftp_server.listen("0.0.0.0", self.TFTP_PORT)
        print(f"TFTP server started at port {self.TFTP_PORT}")
    
    def run_all_servers(self):
        http_thread = threading.Thread(target=self.start_http_server)
        http_thread.start()

        ftp_thread = threading.Thread(target=self.start_ftp_server)
        ftp_thread.start()

        tftp_thread = threading.Thread(target=self.start_tftp_server)
        tftp_thread.start()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("rootfs", help="The root filesystem to serve")
    args = parser.parse_args()

    rootfs = args.rootfs


    server = MultiServer(rootfs=rootfs)
    server.run_all_servers()