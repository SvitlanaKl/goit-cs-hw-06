from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
import threading
from datetime import datetime
import json
from pymongo import MongoClient

# HTTP Server
class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == '/' or self.path == '/index.html':
                self.serve_file('index.html')
            elif self.path == '/message.html':
                self.serve_file('message.html')
            elif self.path == '/style.css':
                self.serve_file('style.css')
            elif self.path == '/logo.png':
                self.serve_file('logo.png', 'image/png')
            else:
                self.serve_file('error.html', status=404)
        except Exception:
            self.serve_file('error.html', status=500)

    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = dict(kv.split('=') for kv in post_data.split('&'))
            forward_to_socket(data)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Message sent!")

    def serve_file(self, filename, content_type='text/html', status=200):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())

def forward_to_socket(data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 5000))
        s.sendall(json.dumps(data).encode('utf-8'))

# Socket Server
def socket_server():
    client = MongoClient('mongodb://mongo:27017/')
    db = client.messages_db
    collection = db.messages

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 5000))
        s.listen()
        while True:
            conn, _ = s.accept()
            with conn:
                data = conn.recv(1024)
                if data:
                    message = json.loads(data.decode('utf-8'))
                    message['date'] = datetime.now().isoformat()
                    collection.insert_one(message)

# Run servers
if __name__ == '__main__':
    threading.Thread(target=socket_server, daemon=True).start()
    httpd = HTTPServer(('localhost', 3000), MyHandler)
    httpd.serve_forever()
