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
    },
    "finance": {
        "url": "https://services.lesechos.fr/rss/les-echos-finance-marches.xml",
        "title": "Finance",
    },
    "sport": {
        "url": "https://www.lemonde.fr/sport/rss_full.xml",
        "title": "Sport",
    },
    "crypto": {
        "url": "https://fr.investing.com/rss/302.rss",
        "title": "Crypto",
    },
}

MAX_ITEMS = 10

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "application/rss+xml, application/xml, "
        "text/xml, */*"
    ),
}


def get_entry_date(entry):
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")

    if parsed:
        try:
            return datetime(*parsed[:6], tzinfo=timezone.utc)
        except Exception:
            pass

    return datetime.now(timezone.utc)


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
    print(f"   🌐 Connexion au flux...")

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    print(
        f"   🟢 HTTP {response.status_code} "
        f"({len(response.content)} octets)"
    )

    feed = feedparser.parse(response.content)

    if not feed.entries:
        raise RuntimeError(
            "Le flux ne contient aucun article."
        )

    return feed


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
            {"isPermaLink": "true"}
        )

        guid_element.text = guid

        ET.SubElement(
            item,
            "description"
        ).text = description

        ET.SubElement(
            item,
            "pubDate"
        ).text = format_datetime(
            pub_date
        )

    tree = ET.ElementTree(
        rss
    )

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
    print("========================================")
    print("Tensho Actualités RSS")
    print("========================================")

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

            entries = list(
                feed.entries
            )

            entries.sort(
                key=get_entry_date,
                reverse=True
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
    print("========================================")
    print(
        f"RSS TERMINÉ — "
        f"{successful} OK / {failed} échec(s)"
    )
    print("========================================")


if __name__ == "__main__":
    main()
