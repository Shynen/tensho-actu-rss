import feedparser
import html
import xml.etree.ElementTree as ET
from email.utils import format_datetime
from datetime import datetime, timezone
from pathlib import Path
import requests


FEEDS = {
    "actualites": {
        "url": "https://www.lemonde.fr/rss/une.xml",
        "title": "Actualités",
        "sort_by_date": True,
    },
    "finance": {
        "url": "https://fr.investing.com/rss/286.rss",
        "title": "Finance",
        "sort_by_date": False,
    },
    "sport": {
        "url": "https://www.lemonde.fr/sport/rss_full.xml",
        "title": "Sport",
        "sort_by_date": True,
    },
    "crypto": {
        "url": "https://fr.investing.com/rss/302.rss",
        "title": "Crypto",
        "sort_by_date": False,
    },
}


MAX_ITEMS = 10


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/149.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}


def get_entry_date(entry):
    parsed = (
        entry.get("published_parsed")
        or entry.get("updated_parsed")
    )

    if not parsed:
        return None

    try:
        return datetime(
            *parsed[:6],
            tzinfo=timezone.utc
        )
    except Exception:
        return None


def clean_text(value):
    if not value:
        return ""

    return html.unescape(str(value)).strip()


def get_description(entry):
    description = entry.get("summary")

    if not description:
        description = entry.get("description")

    return clean_text(description)


def fetch_feed(url):
    print("   🌐 Requête HTTP...")

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
        allow_redirects=True,
    )

    print(f"   📡 HTTP {response.status_code}")
    print(f"   📍 URL finale : {response.url}")
    print(f"   📦 Taille : {len(response.content)} octets")

    response.raise_for_status()

    feed = feedparser.parse(response.content)

    if not feed.entries:
        raise RuntimeError(
            "Le flux RSS ne contient aucun article."
        )

    return feed


def prepare_entries(feed, config):
    entries = list(feed.entries)

    if config["sort_by_date"]:
        dated_entries = []
        undated_entries = []

        for entry in entries:
            date = get_entry_date(entry)

            if date is None:
                undated_entries.append(entry)
            else:
                dated_entries.append(
                    (date, entry)
                )

        dated_entries.sort(
            key=lambda item: item[0],
            reverse=True
        )

        entries = (
            [entry for _, entry in dated_entries]
            + undated_entries
        )

        print(
            "   📅 Tri chronologique effectué."
        )

    else:
        print(
            "   📋 Ordre source conservé "
            "(date RSS non fiable)."
        )

    return entries


def create_feed(category, config, entries):
    rss = ET.Element(
        "rss",
        {"version": "2.0"}
    )

    channel = ET.SubElement(
        rss,
        "channel"
    )

    ET.SubElement(
        channel,
        "title"
    ).text = f"Actualités - {config['title']}"

    ET.SubElement(
        channel,
        "link"
    ).text = config["url"]

    ET.SubElement(
        channel,
        "description"
    ).text = f"Flux RSS {config['title']} - Tensho"

    for entry in entries[:MAX_ITEMS]:
        item = ET.SubElement(
            channel,
            "item"
        )

        title = clean_text(
            entry.get(
                "title",
                "Sans titre"
            )
        )

        link = entry.get(
            "link",
            ""
        ).strip()

        guid = (
            entry.get("id")
            or entry.get("guid")
            or link
        )

        description = get_description(
            entry
        )

        pub_date = get_entry_date(
            entry
        )

        ET.SubElement(
            item,
            "title"
        ).text = title

        ET.SubElement(
            item,
            "link"
        ).text = link

        guid_element = ET.SubElement(
            item,
            "guid",
            {
                "isPermaLink": "false"
            }
        )

        guid_element.text = guid

        ET.SubElement(
            item,
            "description"
        ).text = description

        # On conserve la date fournie par la source.
        # On n'invente jamais une date avec datetime.now().
        if pub_date is not None:
            ET.SubElement(
                item,
                "pubDate"
            ).text = format_datetime(
                pub_date
            )

    tree = ET.ElementTree(rss)

    ET.indent(
        tree,
        space=" "
    )

    output = Path(
        f"{category}.xml"
    )

    tree.write(
        output,
        encoding="UTF-8",
        xml_declaration=True
    )

    print(
        f"   🟢 {output} généré."
    )


def main():
    print(
        "========================================"
    )
    print(
        "Tensho Actualités RSS"
    )
    print(
        "========================================"
    )

    successful = 0
    failed = 0

    for category, config in FEEDS.items():
        print()
        print(
            f"🔎 Récupération : "
            f"{config['title']}"
        )

        print(
            f"   {config['url']}"
        )

        try:
            feed = fetch_feed(
                config["url"]
            )

            entries = prepare_entries(
                feed,
                config
            )

            print(
                f"   📰 {len(entries)} "
                f"articles récupérés."
            )

            create_feed(
                category,
                config,
                entries
            )

            successful += 1

        except Exception as error:
            print(
                f"   ❌ Échec : {error}"
            )

            failed += 1

    print()
    print(
        "========================================"
    )

    print(
        f"RSS TERMINÉ — "
        f"{successful} OK / "
        f"{failed} échec(s)"
    )

    print(
        "========================================"
    )


if __name__ == "__main__":
    main()
