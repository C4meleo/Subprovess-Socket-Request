import requests as r

target = input("Enter target domain name : ")

with open("subdomains.txt", "r") as f:
    for subdomain in f.readlines():
        subdomain = subdomain.strip()
        try:
            url = f"http://{subdomain}.{target}"
            r.get(url)
            print(url)
        except r.ConnectionError:
            pass