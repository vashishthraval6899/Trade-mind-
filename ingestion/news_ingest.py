import feedparser
from datetime import datetime, timedelta, timezone
from dateutil import parser as dateparser
from urllib.parse import quote


def fetch_news(ticker, days=30):
    query = f"{ticker} stock India"
    encoded_query = quote(query)

    rss_url = (
        f"https://news.google.com/rss/search?"
        f"q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
    )

    feed = feedparser.parse(rss_url)

    # Make cutoff UTC-aware
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

    articles = []

    for entry in feed.entries:
        if hasattr(entry, "published"):
            published_date = dateparser.parse(entry.published)

            # Ensure published date is UTC-aware
            if published_date.tzinfo is None:
                published_date = published_date.replace(tzinfo=timezone.utc)
            else:
                published_date = published_date.astimezone(timezone.utc)

            if published_date >= cutoff_date:
                articles.append({
                    "title": entry.title,
                    "summary": getattr(entry, "summary", ""),
                    "published": str(published_date)
                })

    return articles
