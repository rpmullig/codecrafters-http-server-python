import socket
import re

CRLF = "\r\n"
OK_HTTP_RESPONSE = "HTTP/1.1 200 OK"
NOT_FOUND_HTTP_RESPONSE = "HTTP/1.1 404 Not Found"
CONTENT_TYPE_TEXT = "Content-type: text/plain"

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client_socket, address = server_socket.accept() # wait for client

    request = client_socket.recv(1024)
    http_response = parse_request_path(request.decode())

    client_socket.sendall(http_response.encode())
    client_socket.close()

def parse_request_path(decoded_request_str: str) -> str:
    lines = decoded_request_str.split(CRLF)
    http_verb, path, protocol = lines[0].split(' ')

    parsed_path = re.math("/echo/w+", path)
    print(parsed_path)
    if parsed_path:
        return OK_HTTP_RESPONSE + CRLF + CONTENT_TYPE_TEXT + CRLF + CRLF + parsed_path.split('/')[-1]
    else:
        return NOT_FOUND_HTTP_RESPONSE

if __name__ == "__main__":
    main()
