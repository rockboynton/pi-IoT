from bs4 import BeautifulSoup

with open("index.html", 'r+') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')
    for checkbox in soup.find_all('input', {'type':'checkbox'}):
        del checkbox['checked']
    f.truncate(0)
    f.seek(0)
    f.write(soup.decode())
