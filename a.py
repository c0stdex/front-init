from flask import Flask, request, send_from_directory, render_template
import threading
import socket
import json
import os
from datetime import datetime

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')
                                
@app.route('/message.html')
def message():
    return render_template('message.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404


@app.route('/message', methods=['POST'])
def handle_message():
    username = request.form['username']
    message = request.form['message']
    data = {
        'username': username,
        'message': message
    }
    send_data_to_socket_server(data)
    return 'Message sent!'

def send_data_to_socket_server(data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 5000)
    message = json.dumps(data).encode()
    client_socket.sendto(message, server_address)
    client_socket.close()


def udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('localhost', 5000))

    if not os.path.exists('storage'):
        os.makedirs('storage')

    if not os.path.isfile('storage/data.json'):
        with open('storage/data.json', 'w') as f:
            json.dump({}, f)

    while True:
        message, address = server_socket.recvfrom(1024)
        data = json.loads(message.decode())
        timestamp = datetime.now().isoformat()
        with open('storage/data.json', 'r+') as f:
            content = json.load(f)
            content[timestamp] = data
            f.seek(0)
            json.dump(content, f, indent=4)

if __name__ == '__main__':
   
    udp_thread = threading.Thread(target=udp_server)
    udp_thread.daemon = True
    udp_thread.start()

    
    app.run(port=3000)
