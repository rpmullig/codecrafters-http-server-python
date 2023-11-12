import socket
import re

CRLF = "\r\n"
OK_HTTP_RESPONSE = "HTTP/1.1 200 OK"
NOT_FOUND_HTTP_RESPONSE = "HTTP/1.1 404 Not Found"
CONTENT_TYPE_TEXT_HEADER = "Content-type: text/plain"
CONTENT_LENGTH_HEADER = "Content-length: " 

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

    if path == "/":
        return OK_HTTP_RESPONSE + CRLF + CRLF

    parsed_path = re.match("\/(echo\/(.+))?", path)
    print(f'Parsed path group: {parsed_path.group(0)}')

    if parsed_path.group(2):
        print(f"Prased Path capture group return: {parsed_path.group(2)}")
        path_end = parsed_path.group(2)
        response_body = parsed_path.group(2) 
        response_list = [OK_HTTP_RESPONSE, CONTENT_TYPE_TEXT_HEADER,
                            f'Content-length: {len(path_end)}', str(), str(), response_body]
        print("Response: ", response_list) 
        return CRLF.join(response_list)  

    return NOT_FOUND_HTTP_RESPONSE + CRLF + CRLF 

if __name__ == "__main__":
    main()
