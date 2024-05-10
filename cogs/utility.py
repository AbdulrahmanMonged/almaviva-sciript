import sys
import os
import random
import pprint


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def generate_random_str():
    string = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    return "".join(random.choice(string) for _ in range(8))


def rotate_proxy():
    session = generate_random_str()
    return {
        "http": f"socks5h://h6gpTLfsq8tdFOnF:q5eEgvQgZhRkk87P_country-it_session-{session}_lifetime-2m@geo.iproyal.com:32325",
        "https": f"socks5h://h6gpTLfsq8tdFOnF:q5eEgvQgZhRkk87P_country-it_session-{session}_lifetime-2m@geo.iproyal.com:32325",
    }
