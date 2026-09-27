# Local Board

A tiny offline notice board for devices on the same Wi-Fi. Your Mac hosts the page; your Airtel router connects the devices. It uses only Python's standard library. Messages are stored in `messages.json` beside `server.py` and the latest 200 are kept.

## Run on your Mac

1. Connect the Mac and phone to **Network-Wifi**. Internet access is not needed.
2. In Terminal, enter the unzipped folder and run `python3 server.py` (or `python server.py` if that is your Python command).
3. If macOS asks whether Python can accept incoming connections, allow it.
4. On the phone, visit `http://192.168.X.X:8000`. If your Mac's IP changes, find its new address in macOS Wi-Fi Details and replace `192.168.X.X`.
5. Open the same URL on the Mac or another phone, post messages, and watch them appear within about 3 seconds.
6. Press **Control+C** in Terminal to stop the server. Reconnect the Mac to your usual Wi-Fi for internet.

If port 8000 is already in use, stop the earlier `python3 -m http.server` session with Control+C before starting this app.

This is a learning project for your own local network. Anyone connected to that Wi-Fi can read and post messages; it has no accounts or encryption. Do not use it for private information or expose its port to the internet.
