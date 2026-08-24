import feedparser
import html
import xml.etree.ElementTree as ET
from email.utils import format_datetime
from datetime import datetime, timezone
from pathlib import Path


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


def create_feed(category, config, entries):
    rss = ET.Element("rss", {"version": "2.0"})

    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = f"Actualités - {config['title']}"
    ET.SubElement(channel, "link").text = config["url"]
    ET.SubElement(channel, "description").text = (
        f"Flux RSS {config['title']} - Tensho"
    )

    for entry in entries[:MAX_ITEMS]:
        item = ET.SubElement(channel, "item")

        title = clean_text(entry.get("title", "Sans titre"))
        link = entry.get("link", "").strip()

        guid = entry.get("id") or entry.get("guid") or link

        description = get_description(entry)
        pub_date = get_entry_date(entry)

        ET.SubElement(item, "title").text = title
        ET.SubElement(item, "link").text = link

        guid_element = ET.SubElement(
            item,
            "guid",
            {"isPermaLink": "true"}
        )
        guid_element.text = guid

        ET.SubElement(item, "description").text = description
        ET.SubElement(item, "pubDate").text = format_datetime(pub_date)

    tree = ET.ElementTree(rss)

    output = Path(f"{category}.xml")

    ET.indent(tree, space=" ")

    tree.write(
        output,
        encoding="UTF-8",
        xml_declaration=True
    )

    print(f"OK : {output}")


def main():
    print("========================================")
    print("Tensho Actualités RSS")
    print("========================================")

    for category, config in FEEDS.items():
        print()
        print(f"🔎 Récupération : {config['title']}")
        print(f"   {config['url']}")

        try:
            feed = feedparser.parse(config["url"])

            if feed.bozo and not feed.entries:
                print("❌ Flux inaccessible ou invalide.")
                continue

            entries = list(feed.entries)

            entries.sort(
                key=get_entry_date,
                reverse=True
            )

            print(f"🟢 {len(entries)} articles récupérés.")

            create_feed(category, config, entries)

        except Exception as error:
            print(f"❌ Erreur : {error}")

    print()
    print("========================================")
    print("RSS TERMINÉ")
    print("========================================")


if __name__ == "__main__":
    main()
