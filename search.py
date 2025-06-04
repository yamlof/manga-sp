import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0',
    'Accept': 'image/avif,image/webp,image/png,image/svg+xml,image/*;q=0.8,*/*;q=0.5',
    'Accept-Language': 'en-GB,en;q=0.5',
    'Connection': 'keep-alive',
    'Referer': 'https://chapmanganelo.com/',
    'Sec-Fetch-Dest': 'image',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'cross-site',
    'Priority': 'u=5, i',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}

def is_valid_id(id):
    url = f"https://mangakakalot.to/ajax/bookmark/info/{id}"
    response = requests.get(url, headers=headers)
    return response.status_code == 200 and response.text.strip() != ""

# Binary search range
low = 1
high = 1000000000  # adjust upward if needed

while low < high:
    mid = (low + high + 1) // 2
    if is_valid_id(mid):
        low = mid
    else:
        high = mid - 1

print(f"Max valid ID found: {low}")