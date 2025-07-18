import smtplib
import schedule
import time
import requests
import feedparser
import random
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import re
import ssl
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Email configuration from environment variables
import os
GMAIL_USER = os.environ.get('GMAIL_USER')
GMAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD')
RECIPIENT = os.environ.get('RECIPIENT')

# News sources for comprehensive coverage
NEWS_SOURCES = {
    'ai': [
        'https://feeds.feedburner.com/oreilly/radar',
        'https://techcrunch.com/category/artificial-intelligence/feed/',
        'https://www.wired.com/feed/tag/ai/rss',
        'https://venturebeat.com/ai/feed/',
        'https://www.theverge.com/ai-artificial-intelligence/rss/index.xml'
    ],
    'environment': [
        'https://www.treehugger.com/feeds/rss',
        'https://www.greentechmedia.com/rss/all',
        'https://www.renewableenergyworld.com/news/rss',
        'https://www.climatechangenews.com/feed/',
        'https://www.nationalgeographic.com/environment/rss/'
    ],
    'us_politics': [
        'https://feeds.npr.org/1001/rss.xml',
        'https://www.politico.com/rss/politicopicks.xml',
        'https://www.washingtonpost.com/politics/rss_feed/',
        'https://www.reuters.com/politics/rss',
        'https://www.axios.com/politics/feed'
    ],
    'global_politics': [
        'https://www.bbc.com/news/world/rss.xml',
        'https://feeds.reuters.com/reuters/worldNews',
        'https://www.aljazeera.com/xml/rss/all.xml',
        'https://www.theguardian.com/world/rss',
        'https://www.foreignaffairs.com/rss.xml'
    ]
}

# Tarot cards and meanings
TAROT_CARDS = {
    "The Fool": "New beginnings, innocence, spontaneity",
    "The Magician": "Manifestation, resourcefulness, power",
    "The High Priestess": "Intuition, sacred knowledge, divine feminine",
    "The Empress": "Femininity, beauty, nature, abundance",
    "The Emperor": "Authority, structure, control, father-figure",
    "The Hierophant": "Spiritual wisdom, religious beliefs, conformity",
    "The Lovers": "Love, harmony, relationships, values alignment",
    "The Chariot": "Control, willpower, success, determination",
    "Strength": "Strength, courage, patience, control",
    "The Hermit": "Soul searching, introspection, inner guidance",
    "Wheel of Fortune": "Good luck, karma, life cycles, destiny",
    "Justice": "Justice, fairness, truth, cause and effect",
    "The Hanged Man": "Waiting, surrender, letting go, new perspective",
    "Death": "Endings, change, transformation, transition",
    "Temperance": "Balance, moderation, patience, purpose",
    "The Devil": "Bondage, addiction, sexuality, materialism",
    "The Tower": "Sudden change, upheaval, chaos, revelation",
    "The Star": "Hope, faith, purpose, renewal, spirituality",
    "The Moon": "Illusion, fear, anxiety, subconscious, intuition",
    "The Sun": "Optimism, joy, success, vitality, enlightenment",
    "Judgement": "Judgement, rebirth, inner calling, absolution",
    "The World": "Completion, accomplishment, travel, fulfillment"
}

def fetch_article_content(url):
    """Fetch full article content from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try to find article content
        article_selectors = [
            'article', '[role="main"]', '.post-content', '.entry-content',
            '.article-body', '.story-body', '.content', 'main p'
        ]
        
        content = ""
        for selector in article_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    content += element.get_text(strip=True) + " "
                break
        
        if not content:
            # Fallback to all paragraphs
            paragraphs = soup.find_all('p')
            content = ' '.join([p.get_text(strip=True) for p in paragraphs])
        
        # Clean up the content
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()
        
        return content[:2000]  # Limit to first 2000 characters
        
    except Exception as e:
        logger.error(f"Error fetching article content from {url}: {str(e)}")
        return ""

def create_ai_summary(title, content):
    """Create an AI-style summary of the article"""
    if not content:
        return f"'{title}' - The ancient scrolls speak of developments in this realm, though the full wisdom remains shrouded in mystery."
    
    # Extract key sentences (simple extractive summarization)
    sentences = re.split(r'[.!?]+', content)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 50]
    
    if not sentences:
        return f"'{title}' - The scribes report stirrings in this domain, though specifics elude our current understanding."
    
    # Take first 2-3 most relevant sentences
    summary_sentences = sentences[:3]
    summary = ' '.join(summary_sentences)
    
    # Add Tolkien-style flourishes
    elvish_intro = random.choice([
        "The ancient texts reveal that",
        "From the halls of knowledge comes word that",
        "The wise ones speak of tidings that",
        "In the chronicles of our age, it is written that",
        "The learned scholars report that"
    ])
    
    return f"'{title}' - {elvish_intro} {summary}..."

def gather_news_articles(category, sources, num_articles=4):
    """Gather comprehensive news articles for a category"""
    articles = []
    
    for source_url in sources:
        try:
            feed = feedparser.parse(source_url)
            
            for entry in feed.entries[:num_articles]:
                if len(articles) >= num_articles:
                    break
                
                # Fetch full article content
                article_content = fetch_article_content(entry.link)
                
                # Create AI summary
                summary = create_ai_summary(entry.title, article_content)
                
                articles.append({
                    'title': entry.title,
                    'summary': summary,
                    'link': entry.link,
                    'published': getattr(entry, 'published', 'Recently')
                })
                
                # Add delay to be respectful to servers
                time.sleep(1)
        
        except Exception as e:
            logger.error(f"Error processing source {source_url}: {str(e)}")
            continue
    
    return articles[:num_articles]

def generate_tarot_reading():
    """Generate a mystical 3-card tarot reading"""
    cards = random.sample(list(TAROT_CARDS.items()), 3)
    
    reading = f"""
    <div style="background: linear-gradient(135deg, #2d1b4e 0%, #4a2c5a 100%); 
                border-radius: 15px; padding: 25px; margin: 20px 0; 
                border: 2px solid #d4af37; box-shadow: 0 0 20px rgba(212, 175, 55, 0.3);">
        <h3 style="color: #d4af37; text-align: center; font-size: 24px; margin-bottom: 20px;">
            🔮 The Three Paths Spread 🔮
        </h3>
        
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 15px;">
            <div style="background: rgba(212, 175, 55, 0.1); padding: 15px; border-radius: 10px; 
                        border: 1px solid #d4af37; flex: 1; min-width: 200px;">
                <h4 style="color: #d4af37; text-align: center; margin-bottom: 10px;">🌅 Past</h4>
                <p style="color: #e6d3a3; text-align: center; font-weight: bold;">{cards[0][0]}</p>
                <p style="color: #c7b299; text-align: center; font-size: 14px; font-style: italic;">{cards[0][1]}</p>
            </div>
            
            <div style="background: rgba(212, 175, 55, 0.1); padding: 15px; border-radius: 10px; 
                        border: 1px solid #d4af37; flex: 1; min-width: 200px;">
                <h4 style="color: #d4af37; text-align: center; margin-bottom: 10px;">🌟 Present</h4>
                <p style="color: #e6d3a3; text-align: center; font-weight: bold;">{cards[1][0]}</p>
                <p style="color: #c7b299; text-align: center; font-size: 14px; font-style: italic;">{cards[1][1]}</p>
            </div>
            
            <div style="background: rgba(212, 175, 55, 0.1); padding: 15px; border-radius: 10px; 
                        border: 1px solid #d4af37; flex: 1; min-width: 200px;">
                <h4 style="color: #d4af37; text-align: center; margin-bottom: 10px;">🌙 Future</h4>
                <p style="color: #e6d3a3; text-align: center; font-weight: bold;">{cards[2][0]}</p>
                <p style="color: #c7b299; text-align: center; font-size: 14px; font-style: italic;">{cards[2][1]}</p>
            </div>
        </div>
        
        <p style="color: #c7b299; text-align: center; margin-top: 20px; font-style: italic;">
            "The cards whisper of journeys taken, paths currently walked, and destinies yet to unfold..."
        </p>
    </div>
    """
    
    return reading

def generate_astrology_report():
    """Generate a mystical daily astrology report"""
    moon_phases = ["New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous", 
                   "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"]
    
    elements = ["Fire", "Earth", "Air", "Water"]
    planets = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    
    current_moon = random.choice(moon_phases)
    dominant_element = random.choice(elements)
    influential_planet = random.choice(planets)
    
    astrology_wisdom = random.choice([
        "The cosmic winds carry whispers of transformation",
        "The celestial dance speaks of new opportunities",
        "The stars align to illuminate hidden truths",
        "The ethereal realm stirs with ancient magic",
        "The cosmic tapestry weaves patterns of destiny"
    ])
    
    report = f"""
    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                border-radius: 15px; padding: 25px; margin: 20px 0; 
                border: 2px solid #d4af37; box-shadow: 0 0 20px rgba(212, 175, 55, 0.3);">
        <h3 style="color: #d4af37; text-align: center; font-size: 24px; margin-bottom: 20px;">
            ✨ Celestial Guidance ✨
        </h3>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
            <div style="background: rgba(212, 175, 55, 0.1); padding: 15px; border-radius: 10px; border: 1px solid #d4af37;">
                <h4 style="color: #d4af37; margin-bottom: 10px;">🌙 Lunar Phase</h4>
                <p style="color: #e6d3a3; font-weight: bold;">{current_moon}</p>
                <p style="color: #c7b299; font-size: 14px; font-style: italic;">
                    The moon's energy flows through the realm, bringing forth its mystical influence.
                </p>
            </div>
            
            <div style="background: rgba(212, 175, 55, 0.1); padding: 15px; border-radius: 10px; border: 1px solid #d4af37;">
                <h4 style="color: #d4af37; margin-bottom: 10px;">🔥 Dominant Element</h4>
                <p style="color: #e6d3a3; font-weight: bold;">{dominant_element}</p>
                <p style="color: #c7b299; font-size: 14px; font-style: italic;">
                    The elemental forces surge with particular strength in this cosmic moment.
                </p>
            </div>
            
            <div style="background: rgba(212, 175, 55, 0.1); padding: 15px; border-radius: 10px; border: 1px solid #d4af37;">
                <h4 style="color: #d4af37; margin-bottom: 10px;">⭐ Planetary Influence</h4>
                <p style="color: #e6d3a3; font-weight: bold;">{influential_planet}</p>
                <p style="color: #c7b299; font-size: 14px; font-style: italic;">
                    This celestial body casts its ancient wisdom upon the earthly realm.
                </p>
            </div>
        </div>
        
        <div style="background: rgba(212, 175, 55, 0.05); padding: 20px; border-radius: 10px; 
                    border: 1px solid rgba(212, 175, 55, 0.3); margin-top: 20px;">
            <h4 style="color: #d4af37; text-align: center; margin-bottom: 15px;">Daily Cosmic Wisdom</h4>
            <p style="color: #e6d3a3; text-align: center; font-style: italic; font-size: 16px;">
                "{astrology_wisdom}. Let the ancient knowledge guide your steps through this day of wonder."
            </p>
        </div>
    </div>
    """
    
    return report

def create_elven_email(ai_articles, env_articles, us_articles, global_articles, tarot_reading, astrology_report):
    """Create a beautifully formatted email in Elven tablet style"""
    
    current_date = datetime.now().strftime("%B %d, %Y")
    
    def format_articles(articles, icon, title):
        article_html = f"""
        <div style="background: linear-gradient(135deg, #2c1810 0%, #3d2817 100%); 
                    border-radius: 15px; padding: 25px; margin: 20px 0; 
                    border: 2px solid #d4af37; box-shadow: 0 0 15px rgba(212, 175, 55, 0.2);">
            <h3 style="color: #d4af37; text-align: center; font-size: 24px; margin-bottom: 20px;">
                {icon} {title} {icon}
            </h3>
        """
        
        for i, article in enumerate(articles, 1):
            article_html += f"""
            <div style="background: rgba(212, 175, 55, 0.1); padding: 20px; margin: 15px 0; 
                        border-radius: 10px; border-left: 4px solid #d4af37;">
                <h4 style="color: #e6d3a3; margin-bottom: 10px; font-size: 18px;">
                    Chronicle {i}: {article['title']}
                </h4>
                <p style="color: #c7b299; line-height: 1.6; margin-bottom: 10px;">
                    {article['summary']}
                </p>
                <p style="color: #8b7355; font-size: 12px; font-style: italic;">
                    Published: {article['published']}
                </p>
            </div>
            """
        
        article_html += "</div>"
        return article_html
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>The Elven News Chronicle</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');
            
            body {{
                font-family: 'Crimson Text', serif;
                background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 50%, #0f0f0f 100%);
                color: #e6d3a3;
                margin: 0;
                padding: 20px;
                line-height: 1.6;
            }}
            
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%);
                border: 3px solid #d4af37;
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 0 30px rgba(212, 175, 55, 0.5);
                position: relative;
                overflow: hidden;
            }}
            
            .container::before {{
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(212, 175, 55, 0.1) 0%, transparent 50%);
                animation: shimmer 10s infinite;
                pointer-events: none;
            }}
            
            @keyframes shimmer {{
                0%, 100% {{ transform: rotate(0deg) scale(1); }}
                50% {{ transform: rotate(180deg) scale(1.1); }}
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 30px;
                position: relative;
                z-index: 1;
            }}
            
            .title {{
                font-family: 'Cinzel', serif;
                font-size: 36px;
                font-weight: 700;
                color: #d4af37;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
                margin-bottom: 10px;
            }}
            
            .subtitle {{
                font-size: 18px;
                color: #c7b299;
                font-style: italic;
                margin-bottom: 20px;
            }}
            
            .ornament {{
                font-size: 24px;
                color: #d4af37;
                margin: 20px 0;
            }}
            
            .section {{
                position: relative;
                z-index: 1;
            }}
            
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid #d4af37;
                color: #8b7355;
                font-style: italic;
                position: relative;
                z-index: 1;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 class="title">🧙‍♂️ The Elven News Chronicle 🧙‍♂️</h1>
                <p class="subtitle">A Daily Tapestry of Worldly Wisdom and Mystical Insight</p>
                <div class="ornament">✦ ◆ ✦ ◆ ✦</div>
                <p style="color: #c7b299; font-size: 16px;">
                    {current_date} - In the Common Reckoning
                </p>
            </div>
            
            <div style="background: rgba(212, 175, 55, 0.1); padding: 20px; border-radius: 15px; 
                        border: 2px solid #d4af37; margin: 20px 0; text-align: center;">
                <p style="color: #e6d3a3; font-size: 18px; font-style: italic; margin: 0;">
                    "In the halls of knowledge, where wisdom flows like rivers of starlight, 
                    we gather the tales of this age for those who seek understanding..."
                </p>
            </div>
            
            <div class="section">
                {format_articles(ai_articles, "🤖", "Chronicles of Artificial Minds")}
            </div>
            
            <div class="section">
                {format_articles(env_articles, "🌿", "Tales of the Natural Realm")}
            </div>
            
            <div class="section">
                {format_articles(us_articles, "🏛️", "Tidings from the American Realm")}
            </div>
            
            <div class="section">
                {format_articles(global_articles, "🌍", "Chronicles from Distant Lands")}
            </div>
            
            <div class="section">
                {tarot_reading}
            </div>
            
            <div class="section">
                {astrology_report}
            </div>
            
            <div class="footer">
                <div class="ornament">✦ ◆ ✦ ◆ ✦</div>
                <p>May this chronicle serve as a lantern in the darkness, illuminating the paths of wisdom.</p>
                <p>From the Scribes of the Elven Archives</p>
                <p style="font-size: 12px; color: #6b5d4a;">
                    "All knowledge flows like water through the streams of time..."
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

def send_daily_news():
    """Gather news and send the daily chronicle"""
    try:
        logger.info("🌟 Beginning daily chronicle creation...")
        
        # Gather comprehensive news articles
        logger.info("📰 Gathering chronicles from the realms of knowledge...")
        ai_articles = gather_news_articles('ai', NEWS_SOURCES['ai'])
        env_articles = gather_news_articles('environment', NEWS_SOURCES['environment']) 
        us_articles = gather_news_articles('us_politics', NEWS_SOURCES['us_politics'])
        global_articles = gather_news_articles('global_politics', NEWS_SOURCES['global_politics'])
        
        # Generate mystical content
        logger.info("🔮 Consulting the ancient arts...")
        tarot_reading = generate_tarot_reading()
        astrology_report = generate_astrology_report()
        
        # Create the email
        logger.info("📜 Inscribing the chronicle upon mystical parchment...")
        html_content = create_elven_email(ai_articles, env_articles, us_articles, 
                                        global_articles, tarot_reading, astrology_report)
        
        # Send the email
        logger.info("🦅 Dispatching the chronicle via ethereal messengers...")
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🧙‍♂️ The Elven News Chronicle - {datetime.now().strftime('%B %d, %Y')}"
        msg['From'] = GMAIL_USER
        msg['To'] = RECIPIENT
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Create SSL context and send
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)
        
        logger.info("✨ News chronicle sent successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error sending email: {str(e)}")
        raise

def main():
    """Main function to run the bot"""
    print("🌟 Elven Chronicle Bot initialized!")
    print("📅 Daily chronicles will be delivered at 5:00 AM")
    print("🧙‍♂️ The mystical scribes await the appointed hour...")
    
    # Schedule the daily email
    schedule.every().day.at("05:00").do(send_daily_news)
    
    # Keep the program running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
