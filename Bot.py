import os
import re
import time
import json
import requests
import logging
import concurrent.futures
from urllib.parse import urlparse, parse_qs

import telebot
from telebot import types
from flask import Flask, request

from dotenv import load_dotenv

# === تحميل المتغيرات ===
load_dotenv()

TELEGRAM_TOKEN_BOT = os.getenv('TELEGRAM_BOT_TOKEN')
ALIEXPRESS_API_PUBLIC = os.getenv('ALIEXPRESS_API_PUBLIC')
ALIEXPRESS_API_SECRET = os.getenv('ALIEXPRESS_API_SECRET')
ALIEXPRESS_TRACKING_ID = os.getenv('ALIEXPRESS_TRACKING_ID')
RUN_MODE = os.getenv('RUN_MODE', 'polling')  # polling (default) أو webhook
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

if not TELEGRAM_TOKEN_BOT or not ALIEXPRESS_API_PUBLIC or not ALIEXPRESS_API_SECRET or not ALIEXPRESS_TRACKING_ID:
    print("❌ Missing environment variables! Please check .env")
    exit(1)

# === Logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === AliExpress API init (افتراضي كما كنت تستخدم) ===
try:
    from aliexpress_api import AliexpressApi, models
    aliexpress = AliexpressApi(
        ALIEXPRESS_API_PUBLIC,
        ALIEXPRESS_API_SECRET,
        models.Language.AR,
        models.Currency.USD,
        ALIEXPRESS_TRACKING_ID
    )
except Exception as e:
    # إذا لم تتوفر المكتبة أو فشل الإنشاء، نتابع لكن وظائف API قد تفشل لاحقاً
    logger.exception("Failed to initialize AliexpressApi. Make sure library is installed and keys are correct.")
    aliexpress = None

bot = telebot.TeleBot(TELEGRAM_TOKEN_BOT)

# === Constants / Buttons ===
ALIEXPRESS_BUNDLE_PAGE = "https://www.aliexpress.com/ssr/300000512/BundleDeals2?spm=a1z65.home.3fornn&businessCode=guide&pha_manifest=ssr&_immersiveMode=true&disableNav=YES&wh_pid=300000512/BundleDeals2&wh_ttid=adc"

keyboardStart = types.InlineKeyboardMarkup(row_width=1)
keyboardStart.add(
    types.InlineKeyboardButton("⭐️ صفحة مراجعة وجمع النقاط يوميا ⭐️", url="https://s.click.aliexpress.com/e/_DdwUZVd"),
    types.InlineKeyboardButton("📦 رابط الحزمة", url=ALIEXPRESS_BUNDLE_PAGE),
    types.InlineKeyboardButton("❤️ اشترك في القناة للمزيد من العروض ❤️", url="https://t.me/hmida92"),
    types.InlineKeyboardButton("🎬 شاهد كيفية عمل البوت 🎬", url="https://t.me/ShopAliExpressMaroc/9")
)

keyboard = types.InlineKeyboardMarkup(row_width=1)
keyboard.add(
    types.InlineKeyboardButton("⭐️ صفحة مراجعة وجمع النقاط يوميا ⭐️", url="https://s.click.aliexpress.com/e/_DdwUZVd"),
    types.InlineKeyboardButton("📦 رابط الحزمة", url=ALIEXPRESS_BUNDLE_PAGE),
    types.InlineKeyboardButton("❤️ اشترك في القناة للمزيد من العروض ❤️", url="https://t.me/hmida92"),
    types.InlineKeyboardButton("🔗 شارك هذا العرض", switch_inline_query="")
)

# === Session / Executor ===
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (compatible; CoinsBot/1.0)'})
executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

# === Helpers ===
def resolve_full_redirect_chain(link, timeout=10):
    try:
        r = session.get(link, allow_redirects=True, timeout=timeout)
        final_url = r.url
        parsed_url = urlparse(final_url)
        params = parse_qs(parsed_url.query)
        if 'redirectUrl' in params:
            return params['redirectUrl'][0]
        return final_url
    except Exception as e:
        logger.warning(f"resolve_full_redirect_chain failed for {link}: {e}")
        return link

def extract_product_id(link):
    resolved_link = resolve_full_redirect_chain(link)
    # محاولات متعددة لأن روابط AliExpress قد تختلف
    match = re.search(r'/item/(\d+)\.html', resolved_link)
    if match:
        return match.group(1)
    match_alt = re.search(r'productIds=(\d+)', resolved_link)
    if match_alt:
        return match_alt.group(1)
    match_long = re.search(r'(\d{13,})', resolved_link)
    if match_long:
        return match_long.group(1)
    return None

def safe_api_call(func, *args, retries=2, backoff=1, **kwargs):
    last_exc = None
    for i in range(retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exc = e
            sleep = backoff * (2 ** i)
            logger.warning(f"API call failed (attempt {i+1}/{retries+1}): {e}. Sleeping {sleep}s before retry.")
            time.sleep(sleep)
    logger.exception("API call failed after retries.")
    raise last_exc

def generate_coin_affiliate_link(aliex, product_id):
    if not aliex:
        return None
    try:
        url = f"https://m.aliexpress.com/p/coin-index/index.html?_immersiveMode=true&from=syicon&productIds={product_id}"
        links = safe_api_call(aliex.get_affiliate_links, url, retries=2)
        if links and len(links) > 0:
            time.sleep(0.8)
            return links[0].promotion_link
    except Exception as e:
        logger.warning(f"generate_coin_affiliate_link error: {e}")
    return None

def generate_bundle_affiliate_link(aliex, product_id, original_link):
    if not aliex:
        return None
    try:
        url = f'https://star.aliexpress.com/share/share.htm?platform=AE&businessType=ProductDetail&redirectUrl={original_link}?sourceType=560&aff_fcid='
        links = safe_api_call(aliex.get_affiliate_links, url, retries=2)
        if links and len(links) > 0:
            time.sleep(0.8)
            return links[0].promotion_link
    except Exception as e:
        logger.warning(f"generate_bundle_affiliate_link error: {e}")
    return None

def extract_link(text):
    match = re.findall(r'https?://\S+', text)
    return match[0] if match else None

def fetch_product_details(aliex, product_id):
    if not aliex:
        raise RuntimeError("AliExpress API client not initialized.")
    # نطلب الحقول الأساسية، نحاول قراءة حقول التقييمات إن وجدت
    fields = ["target_sale_price", "product_title", "product_main_image_url", "seller_id", "store_name", "seller_positive_rate"]
    details = safe_api_call(aliex.get_products_details, [product_id], fields=fields, retries=2)
    if details and len(details) > 0:
        return details[0]
    raise RuntimeError("No product details returned.")

def format_price(price_field):
    try:
        return float(price_field)
    except:
        try:
            return float(str(price_field).replace(',', '').strip())
        except:
            return None

# === Bot handlers ===
@bot.message_handler(commands=['start'])
def welcome_user(message):
    text = (
        "👋 أهلاً ومرحباً بك في *بوت النقاط (Coins Bot)*\n\n"
        "🎯 مهمته زيادة نسبة التخفيض بالنقاط *(العملات)* حتى 55٪!\n\n"
        "📦 أرسل رابط المنتج من AliExpress وسأجهز لك روابط التخفيض والعروض 👇"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=keyboardStart)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    link = extract_link(message.text or "")
    if link and "aliexpress.com" in link:
        sent = bot.send_message(message.chat.id, '⏳ جاري تجهيز العروض... الرجاء الانتظار قليلاً')
        # نستخدم Executor بدل threading.Thread لتسهيل التحكم
        executor.submit(process_link, message.chat.id, sent.message_id, link)
    else:
        bot.send_message(message.chat.id, "❌ يرجى إرسال رابط منتج من AliExpress.")

def process_link(chat_id, status_message_id, link):
    try:
        product_id = extract_product_id(link)
        if not product_id:
            bot.send_message(chat_id, '❌ لم أتمكن من استخراج معرّف المنتج (Product ID). تأكد من أن الرابط صحيح.')
            bot.delete_message(chat_id, status_message_id)
            return

        # توليد الروابط (محاولات آمنة)
        coin_link = generate_coin_affiliate_link(aliexpress, product_id)
        bundle_link = generate_bundle_affiliate_link(aliexpress, product_id, link)

        # روابط سوبر/محدود (محاولة امنة)
        try:
            super_links = safe_api_call(aliexpress.get_affiliate_links, f'{link}?sourceType=562&aff_fcid=', retries=2)
            super_link = super_links[0].promotion_link if super_links else None
            time.sleep(0.6)
        except Exception:
            super_link = None

        try:
            limit_links = safe_api_call(aliexpress.get_affiliate_links, f'{link}?sourceType=561&aff_fcid=', retries=2)
            limit_link = limit_links[0].promotion_link if limit_links else None
            time.sleep(0.6)
        except Exception:
            limit_link = None

        # تفاصيل المنتج
        details = fetch_product_details(aliexpress, product_id)
        price_usd = format_price(getattr(details, "target_sale_price", 0) or 0) or 0.0
        title = getattr(details, "product_title", "اسم المنتج غير متوفر")
        image = getattr(details, "product_main_image_url", None)

        # محاولة جلب اسم المتجر وتقييمه (fallback)
        store_name = getattr(details, "store_name", None) or getattr(details, "shopName", None) or "غير متوفر"
        # قد يسمّى الحقل seller_positive_rate أو seller_rating أو similar
        seller_rating = None
        for candidate in ["seller_positive_rate", "seller_rating", "shopPositiveRate", "store_score"]:
            seller_rating = getattr(details, candidate, None)
            if seller_rating:
                break
        if not seller_rating:
            # أحياناً تكون داخل dict
            try:
                seller_rating = details.get("seller_positive_rate") if isinstance(details, dict) else None
            except:
                seller_rating = None
        seller_rating = seller_rating or "غير متوفر"

        # === رسالة مُنسَّقة مع فراغات كما طلبت ===
        msg_lines = []
        msg_lines.append(f"📦 {title}")
        msg_lines.append(f"⭐️ المتجر: {store_name}  —  تقييم المتجر: {seller_rating}")
        msg_lines.append(f"💰 السعر: {price_usd:.2f}$")
        msg_lines.append("")  # سطر فارغ

        # الأقسام المطلوبة مع فراغات بين كل قسم
        msg_lines.append("تخفيضات ✨")
        msg_lines.append("")  # فراغ
        msg_lines.append("نسبة تخفيض النقاط الجديدة :")
        msg_lines.append("")  # فراغ
        msg_lines.append("✈️ ثمن الشحن: مجان")
        msg_lines.append("")  # فراغ

        msg_lines.append("تخفيض النقاط")
        if coin_link:
            msg_lines.append("")
            msg_lines.append(f"💰 رابط النقاط: {coin_link}")

        msg_lines.append("")  # فراغ لعرض الباندلز
        msg_lines.append("تخفيض عروض باندلز")
        if bundle_link:
            msg_lines.append("")
            msg_lines.append(f"📦 رابط الحزمة: {bundle_link}")

        msg_lines.append("")  # فراغ لعرض سوبر/محدود
        msg_lines.append("رابط تخفيض الســوبر")
        if super_link:
            msg_lines.append("")
            msg_lines.append(f"💎 سوبر: {super_link}")

        msg_lines.append("")  # فراغ
        msg_lines.append("رابط التخفيض المحدود")
        if limit_link:
            msg_lines.append("")
            msg_lines.append(f"🔥 محدود: {limit_link}")

        msg_lines.append("")  # فراغ أخير
        msg_lines.append("❤️ اشترك في القناة للمزيد من العروض: https://t.me/hmida92")

        final_msg = "\n".join(msg_lines)

        # حذف رسالة الحالة وإرسال الصورة + التوضيحات
        try:
            bot.delete_message(chat_id, status_message_id)
        except Exception:
            pass

        if image:
            bot.send_photo(chat_id, image, caption=final_msg, reply_markup=keyboard)
        else:
            bot.send_message(chat_id, final_msg, reply_markup=keyboard)

    except Exception as e:
        logger.exception(f"Error in process_link: {e}")
        try:
            bot.delete_message(chat_id, status_message_id)
        except:
            pass
        bot.send_message(chat_id, "❌ حدث خطأ أثناء معالجة الرابط. حاول مرة أخرى لاحقاً.")

# === Webhook support for Replit (إن أردت) ===
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = telebot.types.Update.de_json(request.get_data().decode('UTF-8'))
        bot.process_new_updates([update])
        return 'OK', 200
    except Exception as e:
        logger.exception("Webhook processing error")
        return 'ERR', 500

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

# === Entrypoint ===
if __name__ == '__main__':
    if RUN_MODE.lower() == 'webhook' and WEBHOOK_URL:
        logger.info("Starting in webhook mode")
        # تشغيل Flask في خيط منفصل
        from threading import Thread
        thread = Thread(target=run_flask)
        thread.daemon = True
        thread.start()

        try:
            bot.remove_webhook()
        except Exception:
            pass
        time.sleep(0.5)
        bot.set_webhook(url=WEBHOOK_URL)
        # منع انتهاء العملية
        while True:
            time.sleep(60)

    else:
        logger.info("Starting in polling mode")
        try:
            bot.remove_webhook()
        except:
            pass
        bot.infinity_polling(none_stop=True, timeout=20)
