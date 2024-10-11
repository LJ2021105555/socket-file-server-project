import os
import socket
from datetime import datetime

class SocketServer:
    def __init__(self):
        self.bufsize = 8192  # 增大缓冲区大小
        self.DIR_PATH = './request'  # 文件夹路径
        self.createDir(self.DIR_PATH)  # 创建存储请求文件的文件夹
        self.host = '127.0.0.1'  # 服务器监听的地址
        self.port = 8000  # 服务器监听的端口
        self.start_server()  # 启动服务器

    def createDir(self, path):
        """创建目录的方法"""
        try:
            if not os.path.exists(path):
                os.makedirs(path)  # 如果目录不存在则创建
                print(f"目录已创建: {path}")
        except OSError:
            print("Error: Failed to create the directory.")  # 处理创建目录失败的情况

    def start_server(self):
        """启动服务器的方法"""
        try:
            # 创建一个socket对象
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 允许重用地址
            server_socket.bind((self.host, self.port))  # 绑定IP地址和端口
            server_socket.listen(5)  # 监听，允许最多5个连接
            print(f"Server started at {self.host}:{self.port}")
            
            while True:
                print("等待客户端连接...")
                client_socket, addr = server_socket.accept()  # 接受客户端连接
                print(f"Connection from {addr}")
                self.handle_client(client_socket)  # 处理客户端连接
        except Exception as e:
            print(f"Error: {e}")
        finally:
            server_socket.close()  # 关闭服务器socket

    def handle_client(self, client_socket):
        """处理客户端连接的方法"""
        try:
            print("等待客户端发送数据...")
            data = b""  # 初始化空的二进制数据
            while True:
                part = client_socket.recv(self.bufsize)
                data += part
                if len(part) < self.bufsize:
                    # 如果收到的数据块小于缓冲区大小，说明可能是数据结束
                    break
            
            if data:
                print("已接收到数据，开始处理...")
                
                # 简单判断是否为多部分文件上传请求
                if b"Content-Disposition: form-data" in data:
                    self.handle_multipart(data)  # 处理文件上传请求
                else:
                    # 如果是纯文本请求（例如 curl 发送的普通请求）
                    try:
                        data_str = data.decode()  # 尝试解码为字符串
                        print(f"Received data: {data_str}")
                        self.save_request(data)  # 保存请求到文件
                    except UnicodeDecodeError:
                        print("收到的数据不是有效的UTF-8文本，跳过文本处理")
                
                # 响应客户端
                response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nData received successfully."
                client_socket.send(response.encode())  # 发送响应数据给客户端
            else:
                print("接收到的数据为空")
        except Exception as e:
            print(f"Error while handling client: {e}")
        finally:
            client_socket.close()  # 关闭客户端连接
            print("客户端连接已关闭。")

    def handle_multipart(self, data):
        """处理多部分请求以保存文件"""
        try:
            boundary = data.split(b"\r\n")[0]  # 获取请求的边界字符串
            parts = data.split(boundary)
            for part in parts:
                if b"Content-Disposition: form-data; name=\"image\"" in part:
                    # 找到文件部分，提取文件数据
                    file_data_start = part.find(b"\r\n\r\n") + 4
                    file_data = part[file_data_start:-4]  # 去掉结尾的 "\r\n--"
                    filename = datetime.now().strftime("%Y-%m-%d-%H-%M-%S.jpg")
                    file_path = os.path.join(self.DIR_PATH, filename)
                    with open(file_path, 'wb') as f:
                        f.write(file_data)
                    print(f"图片已保存到 {file_path}")
        except Exception as e:
            print(f"Error while handling multipart data: {e}")

    def save_request(self, data):
        """保存客户端请求到文件"""
        filename = datetime.now().strftime("%Y-%m-%d-%H-%M-%S.bin")  # 使用时间戳作为文件名
        file_path = os.path.join(self.DIR_PATH, filename)  # 拼接文件路径
        try:
            with open(file_path, 'wb') as f:  # 打开文件并写入数据
                f.write(data)
            print(f"请求已保存到 {file_path}")
        except Exception as e:
            print(f"Error saving request: {e}")

if __name__ == "__main__":
    server = SocketServer()  # 启动服务器
