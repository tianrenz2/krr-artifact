from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import socket
import subprocess
import asyncio
import argparse

from qemu.qmp import QMPClient


async def start_record(basedir):
    try:
        socket_path = os.path.join(basedir, "test.sock")
        qmp_client = QMPClient('test-rr')

        await qmp_client.connect(socket_path)

        with qmp_client.listener() as listener:
            res = await qmp_client.execute('rr-start-record')
            print(res)
            # if res["status"] == "failed":
            #     print("end record failed: {}".format(res))
            # elif res["status"] == "completed":
            #     print("end record finished")

        await qmp_client.disconnect()
    except Exception as e:
        print("Failed to start record {}".format(str(e)))


async def end_record(basedir):
    try:
        socket_path = os.path.join(basedir, "test.sock")
        qmp_client = QMPClient('test-rr')

        await qmp_client.connect(socket_path)

        with qmp_client.listener() as listener:
            res = await qmp_client.execute('rr-end-record')
            print(res)
            # if res["status"] == "failed":
            #     print("end record failed: {}".format(res))
            # elif res["status"] == "completed":
            #     print("end record finished")

        await qmp_client.disconnect()
    except Exception as e:
        print("Failed to end record {}".format(str(e)))


class SimpleHTTPRequestHandler:
    def __init__(self, basedir):
        self.basedir = basedir

    def __call__(self, *args, **kwargs):
        handler = SimpleHTTPRequestHandlerClass(self.basedir, *args, **kwargs)
        return handler


class SimpleHTTPRequestHandlerClass(BaseHTTPRequestHandler):
    def __init__(self, basedir, *args, **kwargs):
        self.basedir = basedir
        self.socket_path = os.path.join(self.basedir, "test.sock")
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/in_record':
            if os.path.exists('/dev/shm/record'):
                self.send_response(200)
                output = {'exists': True}
            else:
                self.send_response(404)
                output = {'exists': False}

            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(output).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/launch_vm':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data)

            core_number = params['core_number']
            mode = params['mode']
            workload = params["workload"]

            try:
                subprocess.Popen(['./launch.sh', str(core_number), mode, workload, self.basedir])
                self.send_response(202)
                output = "Script started successfully."
            except Exception as e:
                self.send_response(500)
                output = str(e)

            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'output': output}).encode('utf-8'))
        elif self.path == '/end_record':
            try:
                asyncio.run(end_record(self.basedir))
                self.send_response(200)
                output = {'response': "OK"}
            except Exception as e:
                self.send_response(500)
                output = {'error': str(e)}

            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(output).encode('utf-8'))
        elif self.path == '/start_record':
            try:
                asyncio.run(start_record(self.basedir))
                self.send_response(200)
                output = {'response': "OK"}
            except Exception as e:
                self.send_response(500)
                output = {'error': str(e)}
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(output).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()


def run(basedir, server_class=HTTPServer, port=8080):
    server_address = ('', port)
    handler = SimpleHTTPRequestHandler(basedir)
    httpd = server_class(server_address, handler)
    socket_path = os.path.join(basedir, "test.sock")
    print(f'Starting http server on port {port}')
    print(f'Base directory: {basedir}')
    print(f'Using socket path: {socket_path}')
    httpd.serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP Server for QMP communication')
    parser.add_argument('--basedir', type=str, default="/users/sishuaig/sdbdir",
                        help='Base directory where the socket is located (default: /users/sishuaig/sdbdir)')
    parser.add_argument('--port', type=int, default=8080,
                        help='Port for the HTTP server (default: 8080)')
    
    args = parser.parse_args()
    
    run(args.basedir, port=args.port)
