import usocket


# https://github.com/lucien2k/wipy-urllib
class Requests():
    def __init__(self, method, url, data=None, headers={}, stream=None):
        self.method = method
        self.url = url
        self.data = data
        self.headers = headers
        self.stream = stream
        try:
            self.proto, self.dummy, self.host, self.path = \
                self.url.split("/", 3)
        except ValueError:
            self.proto, self.dummy, self.host = self.url.split("/", 2)
            self.path = ""
        if self.proto == "http:":
            self.port = 80
        elif self.proto == "https:":
            self.port = 443
        else:
            raise ValueError("Unsupported protocol: " + self.proto)

        if ":" in self.host:
            self.host, self.port = self.host.split(":", 1)
            self.port = int(self.port)

    def makeRequest(self):
        ai = usocket.getaddrinfo(self.host, self.port)
        addr = ai[0][-1]
        s = usocket.socket()
        s.connect(addr)
        if self.proto == "https:":
            import ussl
            s = ussl.wrap_socket(s)
        s.write(b"%s /%s HTTP/1.0\r\n" % (self.method, self.path))
        if "Host" not in self.headers:
            s.write(b"Host: %s\r\n" % self.host)
        # Iterate over keys to avoid tuple alloc
        for k in self.headers:
            s.write(k)
            s.write(b": ")
            s.write(self.headers[k])
            s.write(b"\r\n")
        if self.data:
            s.write(b"Content-Length: %d\r\n" % len(self.data))
        s.write(b"\r\n")
        if self.data:
            s.write(self.data)

        l = s.readline()
        protover, status, msg = l.split(None, 2)
        status = int(status)
        while True:
            l = s.readline()
            if not l or l == b"\r\n":
                break
            if l.startswith(b"Transfer-Encoding:"):
                if b"chunked" in l:
                    raise ValueError("Unsupported " + l)
            elif l.startswith(b"Location:") and not 200 <= status <= 299:
                print(status)
                raise NotImplementedError("Redirects not yet supported")
        s.close()
        self.status_code = status
        self.status_reason = msg.rstrip()
