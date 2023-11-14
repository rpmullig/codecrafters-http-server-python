import socket
import re
from threading import Thread
import argparse
import os

# Constants
CRLF = "\r\n"
HTTP_404 = "HTTP/1.1 404 Not Found"
HTTP_200 = "HTTP/1.1 200 OK"
HTTP_201 = "HTTP/1.1 201 Created"
CONTENT_TYPE_TEXT = "Content-type: text/plain"
CONTENT_TYPE_OCTET_STREAM = "Content-Type: application/octet-stream"
CONTENT_LENGTH = "Content-Length: "

# Argument Parser
parser = argparse.ArgumentParser()
parser.add_argument('--directory', type=str)
args = parser.parse_args()

def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        client_socket, _ = server_socket.accept()
        Thread(target=handle_client, args=(client_socket,)).start()

def handle_client(client_socket):
    try:
        request = client_socket.recv(1024).decode()
        response = process_request(request)
        client_socket.sendall(response.encode())
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

def process_request(request: str) -> str:
    try:
        lines = request.split(CRLF)
        verb, path, _ = lines[0].split()
        headers, body_start = parse_headers(lines)
        body = lines[body_start:]

        if path == "/":
            return format_response(HTTP_200)

        elif path == "/user-agent":
            return format_response(HTTP_200, CONTENT_TYPE_TEXT, headers.get("User-Agent", ""))

        elif match := re.match(r"/echo/(.*)", path):
            return format_response(HTTP_200, CONTENT_TYPE_TEXT, match.group(1))

        elif match := re.match(r"/files/(.*)", path):
            filepath = os.path.join(args.directory, match.group(1))
            if verb == "GET":
                return handle_file_get(filepath)
            elif verb == "POST":
                return handle_file_post(filepath, body)

    except Exception as e:
        print(f"Error processing request: {e}")

    return format_response(HTTP_404)

def parse_headers(request_lines: list) -> (dict, int):
    headers = {}
    for i, line in enumerate(request_lines[1:], 1):
        if line == '':
            return headers, i + 1
        key, value = re.split(r':\s', line, maxsplit=1)
        headers[key] = value
    return headers, i

def handle_file_get(filepath: str) -> str:
    if not os.path.exists(filepath):
        return format_response(HTTP_404)
    with open(filepath, 'rb') as file:
        content = file.read()
        return format_response(HTTP_200, CONTENT_TYPE_OCTET_STREAM, content)

def handle_file_post(filepath: str, body: list) -> str:
    with open(filepath, 'w') as file:
        file.write(''.join(body))
    return format_response(HTTP_201)

def format_response(status: str, content_type: str = None, body: str = "") -> str:
    headers = [status]
    if content_type:
        headers.append(content_type)
        headers.append(f"{CONTENT_LENGTH}{len(body)}")
    return CRLF.join(headers) + CRLF * 2 + body

if __name__ == "__main__":
    main()

