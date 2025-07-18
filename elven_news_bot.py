import smtplib
import ssl
import feedparser
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import time
import random

# =============================================================================
# CONFIGURATION - UPDATE THESE VALUES
# =============================================================================
GMAIL_USER = "your_email@gmail.com"  # Your Gmail address
GMAIL_PASSWORD = "your_app_password"  # Your 16-character app password
RECIPIENT = "recipient@gmail.com"    # Where to send the news

# =============================================================================
# NEWS SOURCES - Reliable RSS feeds
# =============================================================================
NEWS_SOURCES = {
    "Technology": [
        "https://feeds.feedburner.com/TechCrunch",
        "https://www.theverge.com/rss/index.xml",
        "https://feeds.arstechnica.com/arstechnica/index"
    ],
    "Science": [
        "https://feeds.feedburner.com/ScienceDaily",
        "https://www.sciencenews.org/feeds/headlines.rss",
        "https://feeds.nature.com/nature/rss/current"
    ],
    "World News": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.reuters.com/rssFeed/worldNews",
        "https://feeds.npr.org/1004/rss.xml"
    ],
    "Politics": [
        "https://feeds.feedburner.com/politico",
        "https://feeds.washingtonpost.com/rss/politics",
        "https://feeds.npr.org/1014/rss.xml"
    ]
}

def fetch_news_articles(sources, max_articles=3):
    """Fetch articles from RSS feeds - simplified and reliable"""
    articles = []
    
    for source_url in sources:
        try:
            print(f"📡 Fetching from {source_url}")
            
            # Add headers to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Fetch with timeout
            response = requests.get(source_url, headers=headers, timeout=10)
            feed = feedparser.parse(response.content)
            
            # Get articles from this feed
            for entry in feed.entries[:max_articles]:
                article = {
                    'title': entry.title,
                    'link': entry.link,
                    'summary': entry.summary if hasattr(entry, 'summary') else entry.title,
                    'published': entry.published if hasattr(entry, 'published') else 'Recent'
                }
                articles.append(article)
                
            print(f"✅ Got {len(feed.entries[:max_articles])} articles")
            time.sleep(1)  # Be respectful to servers
            
        except Exception as e:
            print(f"⚠️ Error fetching from {source_url}: {str(e)}")
            continue
    
    return articles

def create_elven_html_email(all_articles):
    """Create beautiful Elven-themed HTML email"""
    
    current_date = datetime.now().strftime("%B %d, %Y")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Georgia', serif;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                margin: 0;
                padding: 20px;
                color: #e8e8e8;
            }}
            .scroll-container {{
                max-width: 800px;
                margin: 0 auto;
                background: linear-gradient(145deg, #2a2a4a 0%, #1e1e3a 100%);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.5);
                border: 2px solid #4a6fa5;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 2px solid #4a6fa5;
                padding-bottom: 20px;
            }}
            .title {{
                font-size: 36px;
                color: #87ceeb;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                margin: 0;
                font-weight: bold;
            }}
            .subtitle {{
                font-size: 16px;
                color: #b0c4de;
                margin: 10px 0;
                font-style: italic;
            }}
            .section {{
                margin: 30px 0;
                padding: 20px;
                background: rgba(255,255,255,0.05);
                border-radius: 15px;
                border-left: 4px solid #4a6fa5;
            }}
            .section-title {{
                font-size: 24px;
                color: #87ceeb;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
            }}
            .article {{
                margin: 15px 0;
                padding: 15px;
                background: rgba(255,255,255,0.03);
                border-radius: 10px;
                border-left: 2px solid #6495ed;
            }}
            .article-title {{
                font-size: 18px;
                color: #b0c4de;
                margin-bottom: 8px;
                font-weight: bold;
            }}
            .article-summary {{
                font-size: 14px;
                color: #d3d3d3;
                line-height: 1.4;
                margin-bottom: 8px;
            }}
            .article-link {{
                color: #87ceeb;
                text-decoration: none;
                font-size: 12px;
                font-style: italic;
            }}
            .article-link:hover {{
                color: #6495ed;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #4a6fa5;
                color: #b0c4de;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="scroll-container">
            <div class="header">
                <h1 class="title">🧙‍♂️ The Elven Chronicle 🧙‍♂️</h1>
                <p class="subtitle">Daily Wisdom from the Realms of Knowledge</p>
                <p class="subtitle">{current_date}</p>
            </div>
    """
    
    # Section emojis
    section_emojis = {
        "Technology": "💻",
        "Science": "🔬", 
        "World News": "🌍",
        "Politics": "🏛️"
    }
    
    # Add each section
    for category, articles in all_articles.items():
        emoji = section_emojis.get(category, "📰")
        html_content += f"""
            <div class="section">
                <h2 class="section-title">{emoji} {category}</h2>
        """
        
        for article in articles:
            # Clean up summary
            summary = article['summary'][:300] + "..." if len(article['summary']) > 300 else article['summary']
            
            html_content += f"""
                <div class="article">
                    <div class="article-title">{article['title']}</div>
                    <div class="article-summary">{summary}</div>
                    <a href="{article['link']}" class="article-link">Read full article →</a>
                </div>
            """
        
        html_content += "</div>"
    
    html_content += """
            <div class="footer">
                <p>🌟 May these chronicles bring wisdom to your day 🌟</p>
                <p>Generated by the Elven News Bot</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

def send_email(html_content):
    """Send the email with proper error handling"""
    try:
        print("📧 Preparing to send email...")
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🧙‍♂️ Your Daily Elven Chronicle - {datetime.now().strftime('%B %d, %Y')}"
        msg['From'] = GMAIL_USER
        msg['To'] = RECIPIENT
        
        # Add HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)
            
        print("✅ Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        return False

def main():
    """Main function - simplified workflow"""
    print("🌟 Beginning daily chronicle creation...")
    print(f"📅 Date: {datetime.now().strftime('%B %d, %Y')}")
    
    all_articles = {}
    
    # Fetch news from each category
    for category, sources in NEWS_SOURCES.items():
        print(f"\n📰 Gathering {category} chronicles...")
        articles = fetch_news_articles(sources, max_articles=3)
        
        if articles:
            all_articles[category] = articles
            print(f"✅ Found {len(articles)} {category} articles")
        else:
            print(f"⚠️ No articles found for {category}")
    
    # Create and send email
    if all_articles:
        print("\n🎨 Crafting the elven scroll...")
        html_content = create_elven_html_email(all_articles)
        
        print("📧 Sending the chronicle...")
        if send_email(html_content):
            print("🎉 Daily chronicle completed successfully!")
        else:
            print("❌ Failed to send chronicle")
    else:
        print("❌ No articles found from any source")

if __name__ == "__main__":
    main()
