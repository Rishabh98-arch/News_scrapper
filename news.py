import streamlit as st
import feedparser
import time
from datetime import datetime
from bs4 import BeautifulSoup

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Tech News Aggregator",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- News Feed Configuration ---
NEWS_FEEDS = {
    "TechCrunch": "http://feeds.feedburner.com/TechCrunch/",
    "The Verge": "http://www.theverge.com/rss/index.xml",
    "Wired": "https://www.wired.com/feed/rss",
    "Ars Technica": "http://feeds.arstechnica.com/arstechnica/index",
    "Forbes (Innovation)": "https://www.forbes.com/innovation/feed/",
    "R&D World": "https://www.rdworldonline.com/feed/",
    "MIT Technology Review": "https://www.technologyreview.com/feed/",
    "Entrepreneur (Startups)": "https://www.entrepreneur.com/latest.rss",
    "Harvard Business Review": "https://hbr.org/rss/regular",
}

# --- Functions ---

def get_image_from_entry(entry):
    """
    Tries to extract an image URL from an RSS feed entry.
    """
    if 'media_thumbnail' in entry and entry.media_thumbnail:
        return entry.media_thumbnail[0]['url']
    if 'media_content' in entry and entry.media_content:
        for item in entry.media_content:
            if 'url' in item and item.get('medium') == 'image':
                return item['url']
    if 'summary' in entry:
        soup = BeautifulSoup(entry.summary, 'html.parser')
        img_tag = soup.find('img')
        if img_tag and img_tag.get('src'):
            return img_tag['src']
    return None

@st.cache_data(ttl=1800)
def fetch_latest_news(selected_feeds):
    """
    Parses the RSS feeds and returns a sorted list of articles.
    """
    all_articles = []
    for name, url in selected_feeds.items():
        try:
            feed = feedparser.parse(url)
            if feed.bozo:
                st.warning(f"Could not properly parse feed for {name}. It might be malformed.")
                continue

            for entry in feed.entries:
                published_time = entry.get('published_parsed') or entry.get('updated_parsed')
                summary_html = entry.get('summary', 'No summary available.')
                summary_text = BeautifulSoup(summary_html, 'html.parser').get_text()
                image_url = get_image_from_entry(entry)

                all_articles.append({
                    "source": name,
                    "title": entry.title,
                    "link": entry.link,
                    "published": published_time,
                    "summary": summary_text,
                    "image_url": image_url
                })
        except Exception as e:
            st.error(f"Error fetching or parsing feed for {name}: {e}")

    all_articles.sort(key=lambda x: x["published"] or time.gmtime(0), reverse=True)
    return all_articles

def display_article_text(article):
    """
    Displays the textual content of an article inside the card.
    """
    st.markdown(f'<a href="{article["link"]}" target="_blank" class="article-title">{article["title"]}</a>', unsafe_allow_html=True)
    published_str = time.strftime('%b %d, %Y', article['published']) if article['published'] else "N/A"
    st.markdown(f'<p class="article-meta"><strong>{article["source"]}</strong> | {published_str}</p>', unsafe_allow_html=True)
    summary = article['summary']
    max_len = 500  # Set the maximum length for the summary
    if len(summary.split()) > max_len:
        summary = ' '.join(summary.split()[:max_len]) + "..."
    st.markdown(f'<p class="article-summary">{summary}</p>', unsafe_allow_html=True)

# --- UI Layout ---

# Inject custom CSS for the modern card design
st.markdown("""
<style>
    .article-card {
        background-color: #ffff;
        border-radius: 10px;
        padding: 3px;
        margin-bottom: 25px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .article-title {
        text-decoration: none;
        color: #ffff !important;
        font-size: 1.3rem;
        font-weight: 600;
        line-height: 1.3;
        display: block;
        margin-bottom: 5px;
    }
    .article-meta {
        font-size: 0.9rem;
        color: #ffff;
        margin-bottom: 10px;
    }
    .article-summary {
        font-size: 1rem;
        color: #ffff;
        line-height: 1.6;
    }
    /* Make Streamlit columns more flexible */
    .st-emotion-cache-1r6slb0 { 
        gap: 25px;
    }
</style>
""", unsafe_allow_html=True)


# --- Header ---
st.title("🚀 AI Tech News Aggregator")
st.markdown("Your daily briefing from the world of technology, startups, and business. Select your sources and get the latest updates.")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Controls")
    all_sources = list(NEWS_FEEDS.keys())
    selected_sources = st.multiselect(
        "Choose your news sources:",
        options=all_sources,
        default=["R&D World", "Forbes (Innovation)"]
    )
    num_articles = st.slider("Number of articles to display:", 5, 50, 25)
    if st.button("🔄 Refresh News"):
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    st.info("News is cached for 30 minutes to improve speed.")

# --- Main Content ---
if not selected_sources:
    st.warning("Please select at least one news source from the sidebar.")
else:
    selected_feeds_dict = {name: NEWS_FEEDS[name] for name in selected_sources}
    with st.spinner("Fetching the latest headlines..."):
        articles = fetch_latest_news(selected_feeds_dict)

    if not articles:
        st.error("Could not fetch any articles. Please check your connection or try again.")
    else:
        st.subheader(f"Top {num_articles} Latest Articles")
        st.markdown(f"Last updated: {datetime.now().strftime('%I:%M %p, %d %B %Y')}")
        st.markdown("<hr>", unsafe_allow_html=True)

        for article in articles[:num_articles]:
            # Wrap each card in a container and apply the CSS class via markdown
            with st.container():
                st.markdown('<div class="article-card">', unsafe_allow_html=True)
                
                if article.get("image_url"):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(article["image_url"], use_container_width='always')
                    with col2:
                        display_article_text(article)
                else:
                    # If no image, display text in a single column
                    display_article_text(article)
                
                st.markdown('</div>', unsafe_allow_html=True)
