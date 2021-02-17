import socket


def create_error_page(conn, err_string):
    conn.send('HTTP/1.1 400 Bad Request\r\n'.encode())
    conn.send('Connection: close\r\n'.encode())
    conn.send('Content-Type: text/html\r\n\r\n'.encode())
    conn.send('<html><head><title>ERROR</title></head>\r\n'.encode())
    conn.send(f'<body><h1>Error</h1><hr/><p>{err_string}</p></body></html>'.encode())
    conn.close()


def handle_request(conn):
    data = conn.recv(1024)
    parts = data.decode().split('\r\n\r\n')
    head = parts[0]
    body = ''
    if len(parts) > 1:
        body = parts[1]

    header = {}
    values = {}

    lines = head.split('\r\n')

    if lines[0].split(' ')[1] != '/':
        create_error_page(conn, "Resource not available")
        return

    for line in lines[1:]:
        key, value = line.split(': ')
        header[key] = value

    if body:
        pairs = body.split('&')
        for pair in pairs:
            key, value = pair.split('=')
            values[key] = value

    try:
        kf = open(ACCOUNTFILE, "r")
        balance = float(kf.read(1024))
        kf.close()
    except:
        balance = 100

    amount = 0
    if 'amount' in values:
        try:
            amount = float(values['amount'])
        except:
            create_error_page(conn, f"{values['amount']} is not a float")
            return

        balance -= amount

        try:
            kf = open(ACCOUNTFILE, "w")
            kf.write(f"{balance:5.2f}")
            kf.close()

            # Form-Post-Redirect
            conn.send('HTTP/1.1 303 See Other\r\n'.encode())
            conn.send('Location: /\r\n\r\n'.encode())
            conn.close()
            return
            # ------------------

        except:
            create_error_page(conn, "There is a problem with the account file")
            return

    conn.send('HTTP/1.1 200 OK\r\n'.encode())
    conn.send('Connection: close\r\n'.encode())
    conn.send('Content-Type: text/html\r\n\r\n'.encode())

    conn.send('<html><head><title>Account</title></head>\r\n'.encode())
    conn.send('<body><h1>Account</h1><hr/>\r\n'.encode())
    if 'amount' in values:
        conn.send(f'<p>Transfer = {amount:5.2f}</p>\r\n'.encode())
    conn.send(f'<p>New balance = {balance:5.2f}</p>\r\n'.encode())
    conn.send('<form method="POST" action="/" enctype="application/x-www-form-urlencoded">\r\n'.encode())
    conn.send('<p>Amount to transfer: <input type="text" name="amount"/></p>\r\n'.encode())
    conn.send('<p><input type="submit" value="Transfer"/></p>\r\n'.encode())
    conn.send('</form>\r\n'.encode())
    conn.send('</body></html>\r\n'.encode())
    conn.close()
    return


ACCOUNTFILE = 'account.txt'

TCP_IP = ''
TCP_PORT = 5000


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)


while 1:
    conn, addr = s.accept()
    handle_request(conn)

