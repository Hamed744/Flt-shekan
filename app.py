import os
import subprocess
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

CURRENT_DIR = os.getcwd()

html_content = """<!DOCTYPE html>
<html>
<head><title>System Status</title>
<style>body{font-family:sans-serif;text-align:center;padding:50px;background:#f0f2f5;}
.card{background:#fff;padding:30px;border-radius:12px;display:inline-block;box-shadow:0 4px 6px rgba(0,0,0,0.1);}
h1{color:#1a73e8;} .ok{color:#34a853;font-weight:bold;}</style></head>
<body><div class="card"><h1>AI Inference Node</h1>
<p>Status: <span class="ok">OPERATIONAL</span></p><p>Region: US-East-1</p></div></body></html>"""

with open("index.html", "w") as f:
    f.write(html_content)

# اینجا listen 7860 به listen 10000 تغییر کرده است
nginx_conf = f"""
worker_processes 1;
daemon off;
pid /tmp/nginx.pid;
error_log /dev/null;
events {{ worker_connections 1024; }}
http {{
    access_log off;
    client_body_temp_path /tmp/client_body;
    proxy_temp_path /tmp/proxy;
    fastcgi_temp_path /tmp/fastcgi;
    uwsgi_temp_path /tmp/uwsgi;
    scgi_temp_path /tmp/scgi;

    server {{
        listen 10000;
        root {CURRENT_DIR};
        index index.html;

        location / {{
            try_files $uri $uri/ =404;
        }}

        location /vl {{
            proxy_redirect off;
            proxy_pass http://127.0.0.1:3000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }}
    }}
}}
"""

with open("nginx.conf", "w") as f:
    f.write(nginx_conf)

xray_config = """
{
  "log": { "loglevel": "none" },
  "inbounds": [
    {
      "port": 3000,
      "listen": "127.0.0.1",
      "protocol": "vless",
      "settings": {
        "clients": [
          {
            "id": "11111111-2222-3333-4444-555555555555",
            "level": 0
          }
        ],
        "decryption": "none"
      },
      "streamSettings": {
        "network": "ws",
        "wsSettings": {
          "path": "/vl"
        }
      }
    }
  ],
  "outbounds": [{ "protocol": "freedom" }]
}
"""

with open("config.json", "w") as f:
    f.write(xray_config)

subprocess.Popen(["./xray", "-c", "config.json"])

nginx_config_path = os.path.join(CURRENT_DIR, "nginx.conf")
subprocess.run(["nginx", "-c", nginx_config_path])
