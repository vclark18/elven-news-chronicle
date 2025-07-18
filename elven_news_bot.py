import smtplib
import schedule
import time
import requests
from bs4 import BeautifulSoup
import feedparser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import random
import re
from urllib.parse import urljoin, urlparse
import json

class ElvenNewsChronicle:
    def __init__(self):
        self.ai_sources = [
            "https://feeds.feedburner.com/venturebeat/SZYF",  # VentureBeat AI
            "https://techcrunch.com/category/artificial-intelligence/feed/",  # TechCrunch AI
            "https://www.artificialintelligence-news.com/feed/",  # AI News
            "https://feeds.feedburner.com/oreilly/radar/atom",  # O'Reilly Radar
            "https://blog.openai.com/rss/",  # OpenAI Blog
            "https://deepmind.com/blog/feed/basic/",  # DeepMind
            "https://ai.googleblog.com/feeds/posts/default",  # Google AI Blog
        ]
        
        self.environmental_sources = [
            "https://feeds.feedburner.com/EnvironmentalNewsNetwork",
            "https://www.theguardian.com/environment/rss",
            "https://www.reuters.com/arcio/rss/category/environment/",
            "https://feeds.feedburner.com/climatecentral/djOO",
            "https://www.eenews.net/rss/latest_news",
            "https://www.nationalgeographic.com/environment/rss/",
            "https://e360.yale.edu/feed",
        ]
        
        self.us_politics_sources = [
            "https://feeds.feedburner.com/politico/politics",
            "https://www.politico.com/rss/politics08.xml",
            "https://feeds.washingtonpost.com/rss/politics",
            "https://rss.cnn.com/rss/politics.rss",
            "https://feeds.npr.org/1014/rss.xml",
            "https://feeds.feedburner.com/TheHill",
            "https://www.reuters.com/arcio/rss/category/us-politics/",
        ]
        
        self.global_politics_sources = [
            "https://feeds.feedburner.com/reuters/topNews",
            "https://feeds.bbci.co.uk/news/world/rss.xml",
            "https://www.aljazeera.com/xml/rss/all.xml",
            "https://feeds.feedburner.com/time/topstories",
            "https://www.foreignaffairs.com/rss.xml",
            "https://feeds.feedburner.com/ForeignPolicy",
            "https://www.reuters.com/arcio/rss/category/world/",
        ]
        
        self.tarot_cards = [
            "The Fool", "The Magician", "The High Priestess", "The Empress", 
            "The Emperor", "The Hierophant", "The Lovers", "The Chariot",
            "Strength", "The Hermit", "Wheel of Fortune", "Justice",
            "The Hanged Man", "Death", "Temperance", "The Devil",
            "The Tower", "The Star", "The Moon", "The Sun",
            "Judgement", "The World"
        ]
        
        self.card_meanings = {
            "The Fool": "New beginnings, spontaneity, and trusting the journey ahead",
            "The Magician": "Manifestation, resourcefulness, and power to create",
            "The High Priestess": "Intuition, sacred knowledge, and divine feminine",
            "The Empress": "Fertility, femininity, and abundance in all forms",
            "The Emperor": "Authority, structure, and masculine energy",
            "The Hierophant": "Tradition, conformity, and spiritual guidance",
            "The Lovers": "Love, harmony, and important relationships",
            "The Chariot": "Control, willpower, and determination",
            "Strength": "Inner strength, courage, and gentle power",
            "The Hermit": "Soul searching, introspection, and inner guidance",
            "Wheel of Fortune": "Change, cycles, and inevitable fate",
            "Justice": "Justice, fairness, and truth",
            "The Hanged Man": "Suspension, restriction, and letting go",
            "Death": "Endings, beginnings, and transformation",
            "Temperance": "Balance, moderation, and patience",
            "The Devil": "Bondage, addiction, and materialism",
            "The Tower": "Sudden change, upheaval, and chaos",
            "The Star": "Hope, faith, and spiritual guidance",
            "The Moon": "Illusion, fear, and anxiety",
            "The Sun": "Joy, success, and positivity",
            "Judgement": "Judgement, rebirth, and inner calling",
            "The World": "Completion, accomplishment, and travel"
        }

    def fetch_article_content(self, url):
        """Fetch the full text content of an article"""
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
            
            # Try to find the main content area
            content_selectors = [
                'article', '[role="main"]', '.entry-content', '.post-content',
                '.article-body', '.story-body', '.content', '.post-body',
                '.article-content', '.main-content', '#content', '.text'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements:
                        # Get text and clean it up
                        text = element.get_text(separator=' ', strip=True)
                        if len(text) > 100:  # Only consider substantial text blocks
                            content += text + "\n\n"
                    break
            
            # If no content found with selectors, try getting all paragraphs
            if not content:
                paragraphs = soup.find_all('p')
                content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
            
            # Clean up the content
            content = re.sub(r'\s+', ' ', content)
            content = re.sub(r'\n+', '\n\n', content)
            
            return content[:3000]  # Limit content length
            
        except Exception as e:
            print(f"Error fetching article content: {e}")
            return ""

    def summarize_content(self, content, topic_area):
        """Create an AI-style summary of the content"""
        if not content:
            return ""
        
        # Simple extractive summarization - find most important sentences
        sentences = content.split('. ')
        sentences = [s.strip() + '.' for s in sentences if len(s.strip()) > 20]
        
        # Score sentences based on key terms for each topic
        key_terms = {
            'AI': ['artificial intelligence', 'machine learning', 'neural network', 'algorithm', 'AI', 'automation', 'robot', 'deep learning', 'computer vision', 'natural language'],
            'Environment': ['climate', 'environment', 'carbon', 'emission', 'renewable', 'solar', 'wind', 'green', 'sustainability', 'pollution', 'conservation'],
            'US Politics': ['congress', 'senate', 'house', 'president', 'biden', 'trump', 'republican', 'democrat', 'election', 'vote', 'policy', 'law'],
            'Global Politics': ['international', 'country', 'nation', 'war', 'peace', 'treaty', 'diplomacy', 'sanctions', 'trade', 'global', 'world']
        }
        
        terms = key_terms.get(topic_area, [])
        
        scored_sentences = []
        for sentence in sentences:
            score = 0
            lower_sentence = sentence.lower()
            for term in terms:
                if term in lower_sentence:
                    score += 1
            
            # Boost sentences with numbers, quotes, or important words
            if any(word in lower_sentence for word in ['said', 'announced', 'reported', 'according', 'study', 'research']):
                score += 1
            if re.search(r'\d+%|\$\d+|\d+\s*(million|billion|trillion)', lower_sentence):
                score += 1
            
            scored_sentences.append((sentence, score))
        
        # Sort by score and take top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [s[0] for s in scored_sentences[:5]]
        
        return ' '.join(top_sentences)

    def get_enhanced_news(self, sources, topic_area, num_articles=5):
        """Get enhanced news with full article summaries"""
        print(f"📰 Gathering {topic_area} news from the ancient scrolls...")
        
        all_articles = []
        
        for source in sources:
            try:
                print(f"   📜 Consulting source: {source}")
                feed = feedparser.parse(source)
                
                for entry in feed.entries[:3]:  # Get more entries per source
                    article_content = self.fetch_article_content(entry.link)
                    summary = self.summarize_content(article_content, topic_area)
                    
                    if summary:  # Only include articles with good summaries
                        all_articles.append({
                            'title': entry.title,
                            'summary': summary,
                            'link': entry.link,
                            'published': getattr(entry, 'published', 'Recently')
                        })
                
            except Exception as e:
                print(f"   ❌ Error with source {source}: {e}")
                continue
        
        # Sort by content quality (length of summary as proxy)
        all_articles.sort(key=lambda x: len(x['summary']), reverse=True)
        
        return all_articles[:num_articles]

    def generate_tarot_spread(self):
        """Generate a mystical 3-card tarot spread"""
        cards = random.sample(self.tarot_cards, 3)
        spread = {
            'past': {'card': cards[0], 'meaning': self.card_meanings[cards[0]]},
            'present': {'card': cards[1], 'meaning': self.card_meanings[cards[1]]},
            'future': {'card': cards[2], 'meaning': self.card_meanings[cards[2]]}
        }
        return spread

    def generate_astrology_report(self):
        """Generate a mystical astrology report"""
        moon_phases = ["New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous", 
                      "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"]
        
        elements = ["Fire", "Earth", "Air", "Water"]
        planets = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
        
        current_moon = random.choice(moon_phases)
        dominant_element = random.choice(elements)
        influential_planet = random.choice(planets)
        
        return {
            'moon_phase': current_moon,
            'element': dominant_element,
            'planet': influential_planet
        }

    def create_enhanced_email_content(self, ai_news, env_news, us_news, global_news, tarot, astrology):
        """Create beautiful HTML email content with enhanced summaries"""
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>The Elven News Chronicle</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');
                
                body {{
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
                    font-family: 'Crimson Text', serif;
                    color: #d4af37;
                    line-height: 1.6;
                }}
                
                .chronicle-container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: linear-gradient(145deg, #1a1a1a 0%, #2d2d2d 100%);
                    border: 3px solid #d4af37;
                    border-radius: 15px;
                    box-shadow: 0 0 30px rgba(212, 175, 55, 0.3);
                    overflow: hidden;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #d4af37 0%, #ffd700 100%);
                    color: #1a1a1a;
                    padding: 30px;
                    text-align: center;
                    position: relative;
                }}
                
                .header::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="2" fill="rgba(255,255,255,0.1)"/></svg>');
                    animation: shimmer 3s infinite;
                }}
                
                @keyframes shimmer {{
                    0%, 100% {{ opacity: 0.3; }}
                    50% {{ opacity: 0.7; }}
                }}
                
                .title {{
                    font-family: 'Cinzel', serif;
                    font-size: 2.5em;
                    font-weight: 700;
                    margin: 0;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                    position: relative;
                    z-index: 1;
                }}
                
                .subtitle {{
                    font-family: 'Cinzel', serif;
                    font-size: 1.2em;
                    margin-top: 10px;
                    font-weight: 400;
                    position: relative;
                    z-index: 1;
                }}
                
                .content {{
                    padding: 40px;
                }}
                
                .section {{
                    margin-bottom: 40px;
                    padding: 25px;
                    background: linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(212, 175, 55, 0.05) 100%);
                    border-radius: 10px;
                    border-left: 4px solid #d4af37;
                }}
                
                .section-title {{
                    font-family: 'Cinzel', serif;
                    font-size: 1.8em;
                    font-weight: 600;
                    color: #ffd700;
                    margin-bottom: 20px;
                    text-align: center;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
                }}
                
                .article {{
                    margin-bottom: 25px;
                    padding: 20px;
                    background: rgba(0,0,0,0.3);
                    border-radius: 8px;
                    border: 1px solid rgba(212, 175, 55, 0.3);
                }}
                
                .article-title {{
                    font-family: 'Cinzel', serif;
                    font-size: 1.3em;
                    font-weight: 600;
                    color: #ffd700;
                    margin-bottom: 10px;
                    line-height: 1.4;
                }}
                
                .article-summary {{
                    font-size: 1.05em;
                    color: #e8e8e8;
                    margin-bottom: 10px;
                    line-height: 1.7;
                    text-align: justify;
                }}
                
                .article-link {{
                    color: #d4af37;
                    text-decoration: none;
                    font-weight: 600;
                    font-size: 0.9em;
                    transition: color 0.3s ease;
                }}
                
                .article-link:hover {{
                    color: #ffd700;
                }}
                
                .mystical-section {{
                    background: linear-gradient(135deg, #2d1810 0%, #3d2818 100%);
                    border: 2px solid #8b4513;
                    border-radius: 15px;
                    padding: 30px;
                    margin-bottom: 30px;
                }}
                
                .mystical-title {{
                    font-family: 'Cinzel', serif;
                    font-size: 1.6em;
                    color: #daa520;
                    text-align: center;
                    margin-bottom: 20px;
                }}
                
                .tarot-card {{
                    background: linear-gradient(135deg, #4a4a4a 0%, #2a2a2a 100%);
                    border: 1px solid #d4af37;
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 15px;
                    text-align: center;
                }}
                
                .card-name {{
                    font-family: 'Cinzel', serif;
                    font-size: 1.2em;
                    color: #ffd700;
                    font-weight: 600;
                    margin-bottom: 8px;
                }}
                
                .card-meaning {{
                    font-style: italic;
                    color: #cccccc;
                    font-size: 0.95em;
                }}
                
                .astro-info {{
                    display: flex;
                    justify-content: space-around;
                    flex-wrap: wrap;
                    margin-top: 20px;
                }}
                
                .astro-item {{
                    text-align: center;
                    margin: 10px;
                    padding: 15px;
                    background: rgba(212, 175, 55, 0.1);
                    border-radius: 8px;
                    border: 1px solid rgba(212, 175, 55, 0.3);
                }}
                
                .astro-label {{
                    font-family: 'Cinzel', serif;
                    font-size: 0.9em;
                    color: #d4af37;
                    font-weight: 600;
                }}
                
                .astro-value {{
                    font-size: 1.1em;
                    color: #ffd700;
                    font-weight: 600;
                    margin-top: 5px;
                }}
                
                .footer {{
                    text-align: center;
                    padding: 20px;
                    background: linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%);
                    color: #888;
                    font-size: 0.9em;
                    font-style: italic;
                }}
                
                .reading-time {{
                    text-align: center;
                    color: #d4af37;
                    font-style: italic;
                    margin-bottom: 20px;
                    font-size: 0.95em;
                }}
            </style>
        </head>
        <body>
            <div class="chronicle-container">
                <div class="header">
                    <h1 class="title">🧙‍♂️ The Elven News Chronicle</h1>
                    <p class="subtitle">~ Ancient Wisdom for Modern Times ~</p>
                    <p class="subtitle">{current_date}</p>
                </div>
                
                <div class="content">
                    <div class="reading-time">
                        ⏱️ Estimated reading time: 12-15 minutes
                    </div>
        """
        
        # AI News Section
        if ai_news:
            html_content += f"""
            <div class="section">
                <h2 class="section-title">🤖 Realm of Artificial Minds</h2>
                <p style="text-align: center; font-style: italic; color: #cccccc; margin-bottom: 25px;">
                    "The great machines of thought awaken, and their wisdom grows ever deeper..."
                </p>
            """
            for article in ai_news:
                html_content += f"""
                <div class="article">
                    <h3 class="article-title">{article['title']}</h3>
                    <p class="article-summary">{article['summary']}</p>
                    <a href="{article['link']}" class="article-link">📜 Read the full scroll</a>
                </div>
                """
            html_content += "</div>"
        
        # Environmental News Section
        if env_news:
            html_content += f"""
            <div class="section">
                <h2 class="section-title">🌿 Chronicles of Middle-earth</h2>
                <p style="text-align: center; font-style: italic; color: #cccccc; margin-bottom: 25px;">
                    "The very stones of the earth cry out, and the trees whisper of changing times..."
                </p>
            """
            for article in env_news:
                html_content += f"""
                <div class="article">
                    <h3 class="article-title">{article['title']}</h3>
                    <p class="article-summary">{article['summary']}</p>
                    <a href="{article['link']}" class="article-link">🌱 Read the full chronicle</a>
                </div>
                """
            html_content += "</div>"
        
        # US Politics Section
        if us_news:
            html_content += f"""
            <div class="section">
                <h2 class="section-title">🏛️ Tales from the White Tower</h2>
                <p style="text-align: center; font-style: italic; color: #cccccc; margin-bottom: 25px;">
                    "In the halls of power, great councils convene and the fate of the realm is decided..."
                </p>
            """
            for article in us_news:
                html_content += f"""
                <div class="article">
                    <h3 class="article-title">{article['title']}</h3>
                    <p class="article-summary">{article['summary']}</p>
                    <a href="{article['link']}" class="article-link">⚖️ Read the full decree</a>
                </div>
                """
            html_content += "</div>"
        
        # Global Politics Section
        if global_news:
            html_content += f"""
            <div class="section">
                <h2 class="section-title">🌍 Tidings from Distant Kingdoms</h2>
                <p style="text-align: center; font-style: italic; color: #cccccc; margin-bottom: 25px;">
                    "Across the wide world, kingdoms rise and fall, and the great wheel of history turns..."
                </p>
            """
            for article in global_news:
                html_content += f"""
                <div class="article">
                    <h3 class="article-title">{article['title']}</h3>
                    <p class="article-summary">{article['summary']}</p>
                    <a href="{article['link']}" class="article-link">🌐 Read the full tale</a>
                </div>
                """
            html_content += "</div>"
        
        # Tarot Section
        html_content += f"""
        <div class="mystical-section">
            <h2 class="mystical-title">🔮 The Ancient Tarot Speaks</h2>
            <p style="text-align: center; font-style: italic; color: #cccccc; margin-bottom: 25px;">
                "The cards have been drawn, and the threads of fate reveal themselves..."
            </p>
            
            <div class="tarot-card">
                <div class="card-name">Past: {tarot['past']['card']}</div>
                <div class="card-meaning">{tarot['past']['meaning']}</div>
            </div>
            
            <div class="tarot-card">
                <div class="card-name">Present: {tarot['present']['card']}</div>
                <div class="card-meaning">{tarot['present']['meaning']}</div>
            </div>
            
            <div class="tarot-card">
                <div class="card-name">Future: {tarot['future']['card']}</div>
                <div class="card-meaning">{tarot['future']['meaning']}</div>
            </div>
        </div>
        
        <div class="mystical-section">
            <h2 class="mystical-title">⭐ Celestial Guidance</h2>
            <p style="text-align: center; font-style: italic; color: #cccccc; margin-bottom: 25px;">
                "The stars align in ancient patterns, whispering secrets of the cosmos..."
            </p>
            
            <div class="astro-info">
                <div class="astro-item">
                    <div class="astro-label">Moon Phase</div>
                    <div class="astro-value">{astrology['moon_phase']}</div>
                </div>
                <div class="astro-item">
                    <div class="astro-label">Dominant Element</div>
                    <div class="astro-value">{astrology['element']}</div>
                </div>
                <div class="astro-item">
                    <div class="astro-label">Influential Planet</div>
                    <div class="astro-value">{astrology['planet']}</div>
                </div>
            </div>
        </div>
        """
        
        html_content += """
                </div>
                
                <div class="footer">
                    <p>~ May wisdom guide your path through the day ahead ~</p>
                    <p>The Elven News Chronicle • Delivered by ancient magic and modern technology</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content

def send_daily_news():
    """Send the enhanced daily news chronicle"""
    print("🌟 Beginning the gathering of news from across the realms...")
    
    chronicle = ElvenNewsChronicle()
    
    # Gather comprehensive news with full summaries
    ai_news = chronicle.get_enhanced_news(chronicle.ai_sources, 'AI', 4)
    env_news = chronicle.get_enhanced_news(chronicle.environmental_sources, 'Environment', 4)
    us_news = chronicle.get_enhanced_news(chronicle.us_politics_sources, 'US Politics', 4)
    global_news = chronicle.get_enhanced_news(chronicle.global_politics_sources, 'Global Politics', 4)
    
    # Generate mystical content
    tarot_spread = chronicle.generate_tarot_spread()
    astrology_report = chronicle.generate_astrology_report()
    
    # Create enhanced email content
    email_content = chronicle.create_enhanced_email_content(
        ai_news, env_news, us_news, global_news, tarot_spread, astrology_report
    )
    
    # Send email
    try:
        print("📧 Sending the chronicle via magical post...")
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🧙‍♂️ The Elven News Chronicle - {datetime.now().strftime('%B %d, %Y')}"
        msg['From'] = GMAIL_USER
        msg['To'] = RECIPIENT
        
        html_part = MIMEText(email_content, 'html')
        msg.attach(html_part)
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        
        server.send_message(msg)
        server.quit()
        
        print("✅ Enhanced news chronicle sent successfully!")
        print(f"📊 Delivered: {len(ai_news)} AI articles, {len(env_news)} environmental articles, {len(us_news)} US politics articles, {len(global_news)} global politics articles")
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")

def main():
    print("🌟 Enhanced Elven Chronicle Bot initialized!")
    print("📅 Daily chronicles will be delivered at 5:00 AM")
    print("📰 Now gathering FULL article summaries for comprehensive coverage")
    print("⏰ Waiting for the appointed hour...")
    
    # Schedule the daily news
    schedule.every().day.at("05:00").do(send_daily_news)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # Email configuration
    GMAIL_USER = "vanessa.lee.clark@gmail.com"
    GMAIL_PASSWORD = "liwr ddik qjpk rykm"
    RECIPIENT = "vanessa.lee.clark@gmail.com"
    
    main()
