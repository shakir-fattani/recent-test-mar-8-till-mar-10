import os
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler
from string import Template


class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            # Get IP_ADDRESS from environment, default to localhost if not set
            ip_address = os.environ.get("IP_ADDRESS", "localhost")

            # Read the template
            template_path = os.path.join(
                os.path.dirname(__file__), "static_content/index.html.template"
            )
            with open(template_path) as f:
                template = Template(f.read())

            # Replace variables
            content = template.substitute(IP_ADDRESS=ip_address)

            # Send response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode())
        else:
            super().do_GET()


class HTTPServerV6(HTTPServer):
    address_family = socket.AF_INET6


def run_server():
    os.chdir(os.path.dirname(__file__))
    server_address = ("::", 8080)
    httpd = HTTPServerV6(server_address, CustomHandler)
    print("Starting HTTP server on port 8080...")  # noqa: T201
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
