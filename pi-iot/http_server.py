#!/usr/bin/env python3

import socket
from gpiozero import LEDBoard
from bs4 import BeautifulSoup


HOST = '0.0.0.0'
PORT = 8000

SUPPORTED_PINS = {
    'D1': 6,
    'D2': 13,
    'D3': 12,
    'D4': 26,
    'D5': 20,
    'D6': 21,
    'D7': 4
}


def main():
    '''
    HTTP Server designed to run on a Raspberry Pi to control LEDs on a Pi Hat

    The supported LEDs are found in `SUPPORTED_PINS`
    '''
    board = LEDBoard(*(SUPPORTED_PINS[led_name] for led_name in SUPPORTED_PINS), active_high=False)

    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mysocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
    mysocket.bind((HOST, PORT))

    mysocket.listen()
    print(f'Listening on port {PORT}...')
    while True:
        conn, addr = mysocket.accept()

        # get HTTP request
        request_line = conn.recv(1024).decode().splitlines()[0]
        command, query, version = request_line.rstrip().split(" ")

        # parse GET queries
        full_query = query.split('?')
        if len(full_query) > 1:
            path, queries = full_query
            handle_pin_queries(board, queries)
        else:
            path = full_query[0]

        send_response(conn, path)


def send_response(conn, path):
    if path == '/':
        path = '/index.html'
    path = path.lstrip('/')
    response_code = 200
    status = 'OK'
    try:
        f = open(path, 'r')
    except OSError:
        response_code = 404
        status = 'NOT FOUND'
        f = open('404.html', 'r')
    content = f.read()
    response = f'HTTP/1.1 {response_code} {status}\r\n' \
                'Connection: close\r\n' \
                f'Content-Length: {len(content)}\r\n\r\n' \
                f'{content}'
    conn.sendall(response.encode())
    conn.close()
    f.close()

def handle_pin_queries(board, queries):
    '''
    Turn LEDs on/off according to GET request queries
    '''
    queries = queries.split("&")

    # determine which pins should be on
    if queries[0] is not '':
        on_leds = list(map(lambda token: int(token.rstrip('=on').lstrip('D')) - 1, queries))
    else:
        on_leds = []
    board.on(*on_leds)

    # determine which pins should be off
    off_leds = [led for led in range(len(board)) if led not in on_leds]
    board.off(*off_leds)
    update_html(on_leds)


def update_html(on_leds):
    '''
    Update html file to have checked boxes persist
    '''
    with open("index.html", 'r+') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        for checkbox in soup.find_all('input', {'type':'checkbox'}):
            led_idx = int(checkbox['name'].lstrip('D')) - 1
            if led_idx in on_leds:
                checkbox['checked'] = None
            else:
                del checkbox['checked']
        f.truncate(0)
        f.seek(0)
        f.write(soup.prettify())


if __name__ == '__main__':
    main()
