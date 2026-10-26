"""Lädt alle Bilder aus tools/images.json ins Repo (nur fehlende).
Wird von .github/workflows/fetch-images.yml ausgeführt."""
import json, os, sys, urllib.request

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
MAGIC = (b'\xff\xd8\xff', b'\x89PNG', b'GIF8', b'RIFF')

items = json.load(open('tools/images.json', encoding='utf-8'))
report, failed = [], 0
for it in items:
    path, url = it['path'], it['url']
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        report.append(f'SKIP  {path}')
        continue
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'image/*,*/*'})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        if len(data) < 1000 or not data.startswith(MAGIC):
            raise ValueError(f'kein Bild ({len(data)} Bytes, Anfang {data[:12]!r})')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data)
        report.append(f'OK    {path}  {len(data)//1024} KB')
    except Exception as e:
        failed += 1
        report.append(f'FEHLER {path}  {url}  -> {e}')

os.makedirs('img', exist_ok=True)
with open('img/_download-report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report) + f'\n\n{len(items) - failed}/{len(items)} vorhanden, {failed} Fehler\n')
print('\n'.join(report))
print(f'{failed} Fehler')
