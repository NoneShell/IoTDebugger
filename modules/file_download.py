'''
Author: error: error: git config user.name & please set dead value or install git && error: git config user.email & please set dead value or install git & please set dead value or install git
Date: 2024-06-06 10:47:11
LastEditors: error: error: git config user.name & please set dead value or install git && error: git config user.email & please set dead value or install git & please set dead value or install git
LastEditTime: 2024-06-06 17:50:41
FilePath: /IoTDebugger/modules/file_download.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import ftplib
import os
import argparse
from queue import Queue

class FTPDownload:
    def __init__(self, server, port):
        self.server = server
        self.port = port
        self.ftp = ftplib.FTP()
        self.ftp.connect(self.server, self.port)
        self.ftp.login()

    def download_file(self, remote_path, local_path):
        try:
            with open(local_path, "wb") as f:
                self.ftp.retrbinary("RETR " + remote_path, f.write)
        except Exception as e:
            print(f"Error downloading {remote_path}: {e}")            

    def close(self):
        self.ftp.quit()

    def download_dir(self, remote_path, local_path):
        os.makedirs(local_path, exist_ok=True)
        queue = Queue()
        queue.put((remote_path, local_path))

        while not queue.empty():
            cur_remote_path, cur_local_path = queue.get()
            os.makedirs(cur_local_path, exist_ok=True)

            self.ftp.cwd(cur_remote_path)

            files_list = self.ftp.nlst()
            files_info = []
            self.ftp.dir(files_info.append)
            files_info.pop(0)

            for cur_file, cur_file_info in zip(files_list, files_info):
                file_type = cur_file_info.split()[0][0]

                next_remote_path = os.path.join(cur_remote_path, cur_file)
                next_local_path = os.path.join(cur_local_path, cur_file)

                if file_type == "d":
                    queue.put((next_remote_path, next_local_path))
                else:
                    self.download_file(next_remote_path, next_local_path)

        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("server", help="The TFTP server IP address")
    parser.add_argument("port", help="The TFTP server port", type=int)
    parser.add_argument("rpath", help="The file to download")
    parser.add_argument("lpath", help="The local path to save the file")
    args = parser.parse_args()

    server = args.server
    port = args.port
    remote_path = args.rpath
    try:
        local_path = args.lpath
    except:
        local_path = os.path.basename(remote_path)

    ftp = FTPDownload(server, port)
    ftp.download_dir(remote_path, local_path)