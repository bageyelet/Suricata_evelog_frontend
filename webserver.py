from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse   import urlparse, parse_qs
from build_html import build_html
from eve_loader import EveLoader
from filter import Filter

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()

        # input parsing and sanitizing
        query_components = parse_qs(urlparse(self.path).query)
        try:
            page = int(query_components["page"][0])
        except:
            page = 0
        try:
            order = query_components["order"][0]
            assert ( order in ("timestamp_d", "timestamp_a", "severity_a", "severity_d") )
        except:
            order = "timestamp_d"
        f = Filter()
        try:
            f.set_source(query_components["filter_src"][0])
        except:
            f.set_source()
        try:
            f.set_destination(query_components["filter_dst"][0])
        except:
            f.set_destination()
        try:
            f.set_interface(query_components["filter_interface"][0])
        except:
            f.set_interface()
        try:
            f.set_protocol(query_components["filter_protocol"][0])
        except:
            f.set_protocol()

        eve.reload() # check if the logfile has been updated
        html = build_html(eve.get_n_lines(100, page, order, f), page, order, f)
        self.wfile.write(html)

    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write("")

def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print "\nStopping httpd..."
        eve.quit()

if __name__ == "__main__":
    from sys import argv, exit

    try:
        assert ( len(argv) in (2, 3) )
        port = int(argv[2]) if len(argv) == 3 else 80
    except:
        print "USAGE: python webserver.py /path/to/eve.json [port=80]"
        exit(1)

    global eve
    eve = EveLoader(argv[1])
    run(port=port)
