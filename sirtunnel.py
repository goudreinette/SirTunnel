#!/usr/bin/env python3

import sys
import json
import time
from urllib import request
import requests
import qrcode
import io
from datetime import datetime


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


# TODO
def delete_request_logs(host):
    pass
    

def delete_tunnel(tunnel_id):
    print("Cleaning up tunnel...")
    delete_url = 'http://127.0.0.1:2019/id/' + tunnel_id
    req = request.Request(method='DELETE', url=delete_url)
    request.urlopen(req)

    

def print_qrcode(url):
    qr = qrcode.QRCode()
    qr.add_data(url)
    f = io.StringIO()
    qr.print_ascii(out=f)
    f.seek(0)
    print(f.read())


last_timestamp = time.time()


def print_new_request_logs(host):
    global last_timestamp
    with open('requests.log', 'r') as f:
        for line in f:
            log = json.loads(line)
            if log['ts'] > last_timestamp:
                #print(line)
                last_timestamp = log['ts']
                
                if log['msg'] == 'handled request':
                    req = log['request']
                    if req['host'] == host:
                        print(f'{datetime.fromtimestamp(log['ts']).strftime('%H:%M:%S') } {req['method']} {req['uri']} {log['status']} ')



if __name__ == '__main__':
    host = sys.argv[1]
    port = sys.argv[2]
    tunnel_id = host

    print("Welcome to comphost.club! :) \n")

    
    # x = requests.get('http://127.0.0.1:2019/config/apps/http/servers/sirtunnel/routes')
    # print(x.content)


    x = requests.get('http://127.0.0.1:2019/id/' + tunnel_id)
    
    # Optional for debugging":
    # print(x.status_code)
    # print(x.content)

    
    # Clean up existing 
    if (x.status_code != 500):
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

    print("Request log:")
    
    while True:
        try:
            if not check_tunnel_health(tunnel_id):
                print("Tunnel disconnected unexpectedly")
                delete_tunnel(tunnel_id)
                break
        except KeyboardInterrupt:
            delete_tunnel(tunnel_id)
            print("Bye!")
            break
        
        print_new_request_logs(host)
        time.sleep(1)
