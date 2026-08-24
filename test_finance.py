import feedparser
from datetime import datetime, timezone


URL = "https://fr.investing.com/rss/286.rss"


def get_date(entry):
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")

    if not parsed:
        return None

    try:
        return datetime(*parsed[:6], tzinfo=timezone.utc)
    except Exception:
        return None


print("========================================")
print("TEST RSS INVESTING - FINANCE")
print("========================================")
print()
print(f"Flux : {URL}")
print()

feed = feedparser.parse(URL)

print(f"Articles récupérés : {len(feed.entries)}")
print(f"Erreur parser       : {feed.bozo}")
print()

if not feed.entries:
    print("❌ Aucun article récupéré.")
    raise SystemExit(1)


entries = []

for entry in feed.entries:
    date = get_date(entry)

    entries.append({
        "title": entry.get("title", "Sans titre"),
        "link": entry.get("link", ""),
        "date": date,
    })


# Affichage de l'ordre ORIGINAL du flux
print("----------------------------------------")
print("ORDRE FOURNI PAR INVESTING")
print("----------------------------------------")

for i, entry in enumerate(entries[:10], 1):
    print(
        f"{i:02d}. "
        f"{entry['date']} - "
        f"{entry['title']}"
    )


# Tri comme notre futur générateur
entries_with_date = [
    entry for entry in entries
    if entry["date"] is not None
]

entries_without_date = [
    entry for entry in entries
    if entry["date"] is None
]

entries_with_date.sort(
    key=lambda entry: entry["date"],
    reverse=True
)

entries = entries_with_date + entries_without_date


print()
print("----------------------------------------")
print("ORDRE APRÈS TRI PAR DATE")
print("----------------------------------------")

for i, entry in enumerate(entries[:10], 1):
    print(
        f"{i:02d}. "
        f"{entry['date']} - "
        f"{entry['title']}"
    )


print()
print("----------------------------------------")
print("VERIFICATION")
print("----------------------------------------")

if entries_with_date:
    first_date = entries_with_date[0]["date"]

    print(
        f"🟢 Article le plus récent : "
        f"{first_date}"
    )

    print(
        f"   {entries_with_date[0]['title']}"
    )

    if len(entries_with_date) >= 2:
        second_date = entries_with_date[1]["date"]

        if first_date >= second_date:
            print(
                "🟢 Les dates sont correctement "
                "triées du plus récent au plus ancien."
            )
        else:
            print(
                "🔴 PROBLEME : l'ordre des dates "
                "n'est pas correct."
            )

else:
    print(
        "🔴 Aucun article ne possède de date "
        "exploitable."
    )

if entries_without_date:
    print(
        f"⚠️ {len(entries_without_date)} article(s) "
        f"sans date exploitable."
    )

print()
print("========================================")
print("TEST TERMINÉ")
print("========================================")
