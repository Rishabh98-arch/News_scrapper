import streamlit as st
import feedparser
import time
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Tech News Aggregator",
    page_icon="🚀",
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
}

# --- Functions ---

@st.cache_data(ttl=1800)  # Cache the data for 30 minutes
def fetch_latest_news(selected_feeds):
    all_articles = []
    for name, url in selected_feeds.items():
        try:
            feed = feedparser.parse(url)
            if feed.bozo:
                st.warning(f"Could not properly parse feed for {name}. It might be malformed.")
                continue

            for entry in feed.entries:
                published_time = entry.get('published_parsed') or entry.get('updated_parsed')
                summary = entry.get('summary', 'No summary available.')
                
                # Basic HTML tag cleaning for summary
                summary = summary.split('<')[0]

                all_articles.append({
                    "source": name,
                    "title": entry.title,
                    "link": entry.link,
                    "published": published_time,
                    "summary": summary
                })
        except Exception as e:
            st.error(f"Error fetching or parsing feed for {name}: {e}")

    all_articles.sort(key=lambda x: x["published"] or time.gmtime(0), reverse=True)
    return all_articles

# --- UI Layout ---

# --- Header ---
st.title("🚀 AI Tech News Aggregator")
st.markdown("<p>Your daily briefing from the world of technology and innovation. Select your sources and get the latest updates.</p>", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Controls")
    
    # Feed Selector
    st.subheader("Select News Sources")
    all_sources = list(NEWS_FEEDS.keys())
    selected_sources = st.multiselect(
        "Choose your favorite tech news sources:",
        options=all_sources,
        default=all_sources[:3] # Default to the first 3 sources
    )

    # Article Count Slider
    st.subheader("Number of Articles")
    num_articles = st.slider("How many articles would you like to see?", 5, 50, 25)

    # Refresh Button
    if st.button("🔄 Refresh News"):
        st.cache_data.clear()
        st.success("News feed refreshed!")
        
    st.markdown("---")
    st.info("This app fetches the latest news and caches it for 30 minutes to improve speed.")

# --- Main Content ---
if not selected_sources:
    st.warning("Please select at least one news source from the sidebar to see the latest articles.")
else:
    selected_feeds_dict = {name: NEWS_FEEDS[name] for name in selected_sources}
    
    with st.spinner("Fetching the latest headlines..."):
        articles = fetch_latest_news(selected_feeds_dict)

    if not articles:
        st.error("Could not fetch any articles. Please check your connection or try again later.")
    else:
        st.subheader(f"Top {num_articles} Latest Articles")
        st.markdown(f"Last updated: {datetime.now().strftime('%I:%M %p, %d %B %Y')}")
        st.markdown("---")

        for article in articles[:num_articles]:
            with st.container():
                st.markdown(
                    f"""
                    <div style="background-color: #f9f9f9; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
                        <h3 style="margin: 0;"><a href="{article['link']}" target="_blank" style="text-decoration: none; color: #333;">{article['title']}</a></h3>
                        <p style="margin: 5px 0; color: #777;">{article['source']} | {time.strftime('%a, %d %b %Y', article['published']) if article['published'] else 'N/A'}</p>
                        <p style="margin: 5px 0; color : black">{article['summary']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

