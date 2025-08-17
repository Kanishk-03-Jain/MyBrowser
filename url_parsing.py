import socket
import ssl
import sys

class URL:
    def __init__(self, url):
        """
        Initializes a URL object by parsing the input string
        """
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https"]

        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url

        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

    def request(self):
        """
        Sends an HTTP/1.1 request and returns the response body.
        """

        # Create a socket and connect to the host on the corrent part
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
        s.connect((self.host, self.port))
       
        # If the scheme is https. wrap the socket with SSL/TLS
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        # Build the HTTP request including all the necessary headers
        request = "GET {} HTTP/1.1\r\n".format(self.path)
        
        headers = {
            "Host": self.host,
            "Connection": "close",
            "User-Agent": "MyCustomBrowser/1.0"
        }
        
        for header, value in headers.items():
            request += f"{header}: {value}\r\n"
        
        request += "\r\n"
        
        s.send(request.encode("utf8"))

        # Read the response
        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        # Read headers
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

            assert "transfer-encoding" not in response_headers
            assert "content-encoding" not in response_headers

            content = response.read()
            s.close()
            return content

def show(body):
    """
    Function to print the text content of the HTML body, ignoring the tags
    """
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")

def load(url):
    """
    Loads a URL and shows its text content.
    """
    body = url.request()
    show(body)


if __name__ == "__main__":
    import sys
    load(URL(sys.argv[1]))
