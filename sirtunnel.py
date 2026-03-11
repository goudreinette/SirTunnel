#!/usr/bin/env python3

import sys
import json
import time
from urllib import request
import requests
import qrcode
import io

routes_data = []


def check_tunnel_health(tunnel_id):
    check_url = 'http://127.0.0.1:2019/id/' + tunnel_id
    try:
        request.urlopen(check_url)
    except error.HTTPError as e:
        if e.code == 404:  # Not Found
            return False
    except error.URLError:
        return False
    return True


def delete_tunnel(tunnel_id):
    print("Cleaning up tunnel")
    delete_url = 'http://127.0.0.1:2019/id/' + tunnel_id
    req = request.Request(method='DELETE', url=delete_url)
    request.urlopen(req)

    # with open('routes.json', 'r') as f:
    #     routes_data = json.load(f)
    #     del routes_data[host]
# 
    # with open('routes.json', 'w') as f:
    #     json.dump(routes_data, f)
    #                 


def print_qrcode(url):
    qr = qrcode.QRCode()
    qr.add_data(url)
    f = io.StringIO()
    qr.print_ascii(out=f)
    f.seek(0)
    print(f.read())



if __name__ == '__main__':

    host = sys.argv[1]
    port = sys.argv[2]
    # tunnel_id = host + '-' + port
    tunnel_id = host

    
    # x = requests.get('http://127.0.0.1:2019/config/apps/http/servers/sirtunnel/routes')
    # print(x.content)
    # 
    #
    x = requests.get('http://127.0.0.1:2019/id/' + tunnel_id)
    
    # Optional for debugging":
    # print(x.status_code)
    # print(x.content)

    
    # Clean up existing 
    if (x.status_code != 500):
        print(x.status_code)
        print("Existing tunnel found for " + tunnel_id)
        delete_tunnel(tunnel_id)
    

    caddy_add_route_request = {
        "@id": tunnel_id,
        "match": [{
            "host": [host],
        }],
        "handle": [{
            "handler": "reverse_proxy",
            "upstreams":[{
                "dial": ':' + port
            }]
        }]
    }

    body = json.dumps(caddy_add_route_request).encode('utf-8')
    headers = {
        'Content-Type': 'application/json'
    }
    create_url = 'http://127.0.0.1:2019/config/apps/http/servers/sirtunnel/routes'
    req = request.Request(method='POST', url=create_url, headers=headers)
    request.urlopen(req, body)

    protocol_and_host = 'https://' + host
    print("Tunnel created successfully: ")
    # print("localhost:" + port + " -> ")  # + protocol_and_host
    print(protocol_and_host)
    print_qrcode(protocol_and_host)


    
    # with open('routes.json', 'r') as f:
    #     routes_data = json.load(f)
    #     routes_data[host] = port
# 
# 
    # with open('routes.json', 'w') as f:
    #     json.dump(routes_data, f)


    
    while True:
            try:
                if not check_tunnel_health(tunnel_id):
                    print("Tunnel disconnected unexpectedly")
                    delete_tunnel(tunnel_id)
                    break
                time.sleep(1)
            except KeyboardInterrupt:
                delete_tunnel(tunnel_id)
                break
