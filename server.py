#!/usr/bin/env python3
"""Offline LAN message board. Run: python3 server.py"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
import json
import time

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'messages.json'
LOCK = Lock()
PORT = 8000
MAX_BODY = 4096

PAGE = r'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Local Board</title>
<style>
:root{font-family:system-ui,sans-serif;color:#eaf0f7;background:#101827}body{max-width:680px;margin:30px auto;padding:0 18px}h1{margin-bottom:4px}small{color:#a9b8c9}form,.card{background:#1d2a3c;border:1px solid #34445a;border-radius:14px;padding:16px;margin:16px 0}input,textarea,button{font:inherit;box-sizing:border-box;width:100%;padding:12px;border-radius:9px}input,textarea{color:#fff;background:#101827;border:1px solid #52647b;margin:7px 0}textarea{min-height:90px;resize:vertical}button{background:#70d6b2;color:#10231d;border:0;font-weight:700;cursor:pointer}button:disabled{opacity:.5}.card p{white-space:pre-wrap;overflow-wrap:anywhere;margin-bottom:0}.meta{color:#a9b8c9;font-size:.85rem}#status{min-height:1.3em}
</style>
<h1>Local Board</h1><small>Messages shared over your Wi-Fi. No internet needed.</small>
<form id="form"><label>Name<input id="name" maxlength="30" required placeholder="Your name"></label><label>Message<textarea id="message" maxlength="500" required placeholder="Say something..."></textarea></label><button id="send">Post message</button></form>
<p id="status" role="status"></p><section id="posts" aria-live="polite"></section>
<script>
const form=document.querySelector('#form'), posts=document.querySelector('#posts'), status=document.querySelector('#status');
const nameField=document.querySelector('#name'), message=document.querySelector('#message');
nameField.value=localStorage.getItem('board-name')||'';
async function refresh(){
 try{const res=await fetch('/api/messages',{cache:'no-store'});if(!res.ok)throw Error('Server error');const items=await res.json();posts.replaceChildren();
 for(const item of items.slice().reverse()){const card=document.createElement('article');card.className='card';const meta=document.createElement('div');meta.className='meta';meta.textContent=item.name+' · '+new Date(item.time*1000).toLocaleString();const p=document.createElement('p');p.textContent=item.message;card.append(meta,p);posts.append(card)}
 status.textContent=items.length+' messages';}catch(e){status.textContent='Cannot reach the Mac server. Check Wi-Fi and Terminal.'}}
form.addEventListener('submit',async e=>{e.preventDefault();const button=document.querySelector('#send');button.disabled=true;localStorage.setItem('board-name',nameField.value.trim());try{const res=await fetch('/api/messages',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:nameField.value.trim(),message:message.value.trim()})});if(!res.ok)throw Error('Could not post');message.value='';await refresh()}catch(e){status.textContent=e.message}finally{button.disabled=false}});
refresh();setInterval(refresh,2500);
</script></html>'''


def read_messages():
    try:
        value = json.loads(DATA.read_text(encoding='utf-8'))
        return value if isinstance(value, list) else []
    except (FileNotFoundError, ValueError):
        return []


class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, status, body, content_type):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/':
            self.send_bytes(200, PAGE.encode(), 'text/html; charset=utf-8')
        elif self.path == '/api/messages':
            with LOCK:
                body = json.dumps(read_messages()).encode()
            self.send_bytes(200, body, 'application/json; charset=utf-8')
        else:
            self.send_bytes(404, b'Not found', 'text/plain')

    def do_POST(self):
        if self.path != '/api/messages':
            return self.send_bytes(404, b'Not found', 'text/plain')
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= MAX_BODY:
                raise ValueError()
            data = json.loads(self.rfile.read(length))
            name, message = data['name'], data['message']
            if not isinstance(name, str) or not isinstance(message, str):
                raise ValueError()
            name, message = name.strip(), message.strip()
            if not 1 <= len(name) <= 30 or not 1 <= len(message) <= 500:
                raise ValueError()
        except (ValueError, KeyError, TypeError):
            return self.send_bytes(400, b'Invalid message', 'text/plain')
        with LOCK:
            items = read_messages()
            items.append({'name': name, 'message': message, 'time': time.time()})
            DATA.write_text(json.dumps(items[-200:], ensure_ascii=False, indent=2), encoding='utf-8')
        self.send_bytes(201, b'{}', 'application/json')


if __name__ == '__main__':
    print(f'Local Board running on port {PORT}. Press Control+C to stop.', flush=True)
    ThreadingHTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
