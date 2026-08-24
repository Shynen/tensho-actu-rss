import requests
import feedparser

URLS = {
    "Crypto News": "https://fr.investing.com/rss/news_301.rss",
    "Finance actuel": "https://fr.investing.com/rss/286.rss",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

for name, url in URLS.items():
    print()
    print("=" * 60)
    print(name)
    print(url)
    print("=" * 60)

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    print("HTTP :", response.status_code)
    print("Type :", response.headers.get("content-type"))
    print("Taille :", len(response.content))

    feed = feedparser.parse(response.content)

    print("Bozo :", feed.bozo)
    print("Articles :", len(feed.entries))

    for i, entry in enumerate(feed.entries[:10], 1):
        print()
        print(i)
        print("Titre :", entry.get("title"))
        print("Date  :", entry.get("published"))
        print("Parsed:", entry.get("published_parsed"))
        print("Lien  :", entry.get("link"))
