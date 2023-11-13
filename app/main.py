import socket
import re
from threading import Thread
import argparse
import os

CRLF = "\r\n"
OK_HTTP_RESPONSE = "HTTP/1.1 200 OK"
NOT_FOUND_HTTP_RESPONSE = "HTTP/1.1 404 Not Found"
CONTENT_TYPE_TEXT_HEADER = "Content-type: text/plain"
CONTENT_LENGTH_HEADER = "Content-Length: "
CONTENT_TYPE_OCTET_STREAM_HEADER = "Content-Type: application/octet-stream"

parser = argparse.ArgumentParser()
parser.add_argument('--directory', type=str)
args = parser.parse_args()

def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        client_socket, address = server_socket.accept()
        Thread(target=server_thread, args=(client_socket,)).start()


def server_thread(client_socket):
    request = client_socket.recv(1024)
    http_response = parse_request_path(request.decode())
    client_socket.sendall(http_response.encode())
    client_socket.close()



def parse_request_path(decoded_request_str: str) -> str:
    lines = decoded_request_str.split(CRLF)
    http_verb, path, protocol = lines[0].split(' ')
    headers = parse_headers(lines)
    print("Headers: ", headers)

    if path == "/":
        return OK_HTTP_RESPONSE + CRLF + CRLF

    if path == "/user-agent":
        response_body = headers["User-Agent"]
        print("User agent found to be: ", headers["User-Agent"])
        response_headers = [OK_HTTP_RESPONSE, CONTENT_TYPE_TEXT_HEADER,
                            f'Content-Length: {len(response_body)}', str(), str()]

        return CRLF.join(response_headers) + response_body

    parsed_echo_path = re.match("\/(echo\/(.+))?", path)
    print(f'Parsed path group: {parsed_echo_path.group(0)}')

    if parsed_echo_path.group(2):
        print(f"Prased Path capture group return: {parsed_echo_path.group(2)}")
        response_body = parsed_echo_path.group(2)
        response_headers = [OK_HTTP_RESPONSE, CONTENT_TYPE_TEXT_HEADER,
                            f'Content-Length: {len(response_body)}', str(), str()]
        return CRLF.join(response_headers) + response_body

    parsed_files_path = re.match("\/(files\/(.+))?", path)
    print(f'Parsed path group: {parsed_files_path.group(0)}')

    if parsed_files_path.group(2):
        print(f"Prased Path capture group return: {parsed_files_path.group(2)}")
        if not os.path.exists(args.directory + parsed_echo_path.group(2)):
            return CRLF.join(NOT_FOUND_HTTP_RESPONSE, str())
        response_body = fetch_file_contents(args.directory, parsed_files_path.group(2))
        response_headers = [OK_HTTP_RESPONSE, CONTENT_TYPE_OCTET_STREAM_HEADER,
                            f'Content-Length: {len(response_body)}', str(), str()]
        return CRLF.join(response_headers) + response_body


    return NOT_FOUND_HTTP_RESPONSE + CRLF + CRLF

def parse_headers(request_lines: str) -> dict:
    i: int = 2
    headers = dict()
    while i < len(request_lines) and request_lines[i] != '':
        key, value = re.split(r':\s', request_lines[i])
        headers[key] = value
        i += 1
    return headers


def fetch_file_contents(dir: str, file: str) -> str:
    filepath: str = dir + file
    contents: str = ""
    with open(filepath, 'r') as r:
        contents = r.read()
    return contents

if __name__ == "__main__":
    main()
