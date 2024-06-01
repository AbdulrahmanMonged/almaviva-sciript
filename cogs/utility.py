import sys
import os
import random

countries = ["eg", "it"]
proxies = [
    "socks5://customer-AlmavivaScript1337_iwH5v-cc-{0}:T8AXFwjfi9cRy@pr.oxylabs.io:7777",
    "socks5://95421323-zone-custom-region-{0}:Dwv35snj@ade.360s5.com:3600",
    "socks5://b8pb7rusmp1hwbj-country-{0}:lxccpolkxgldhaw@rp.proxyscrape.com:6060",
    "socks5://h6gpTLfsq8tdFOnF:q5eEgvQgZhRkk87P_country-{0}@geo.iproyal.com:32325",
]


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def generate_random_str():
    string = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    return "".join(random.choice(string) for _ in range(8))


def rotate_proxy(async_session=False):
    random_proxy = random.choice(proxies).format(random.choice(countries))

    if async_session:
        return random_proxy
    return {
        "http": random_proxy,
        "https": random_proxy,
    }
