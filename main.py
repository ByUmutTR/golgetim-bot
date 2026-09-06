import os
from flask import Flask, request
import telebot
from telebot import types

TOKEN = "8259142838:AAES_yZxA_IFl2Uqg3YD2f252iYvFVdTq2U"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Kullanıcıların işlem adımlarını tutmak için geçici sözlükler
user_states = {}


# --- WEBHOOK ENDPOINT ---
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
  json_string = request.get_data().decode("utf-8")
  update = telebot.types.Update.de_json(json_string)
  bot.process_new_updates([update])
  return "!", 200


@app.route("/")
def index():
  return "Gölge Timi Güvenlik Sistemi Aktif!", 200


# --- BOT KOMUTLARI VE AKIŞI ---


@bot.message_handler(commands=["start"])
def send_welcome(message):
  markup = types.InlineKeyboardMarkup(row_width=1)
  btn_ihbar = types.InlineKeyboardButton(
      "🚨 Dolandırıcılık/Şüpheli İhbar Et", callback_data="islem_ihbar"
  )
  btn_basvuru = types.InlineKeyboardButton(
      "🛡️ Gölge Timi'ne Katıl (Başvuru)", callback_data="islem_basvuru"
  )
  btn_bilgi = types.InlineKeyboardButton(
      "ℹ️ Gölge Timi Nedir?", callback_data="islem_bilgi"
  )
  markup.add(btn_ihbar, btn_basvuru, btn_bilgi)

  welcome_text = (
      f"Selam {message.from_user.first_name}.\n\n"
      "**Gölge Timi** merkezi güvenlik ve farkındalık sistemine hoş geldin.\n"
      "Aşağıdaki menüden işlem seçebilirsin."
  )
  bot.send_message(
      message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup
  )


# --- BUTON YÖNETİMLERİ ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
  chat_id = call.message.chat.id

  if call.data == "islem_ihbar":
    user_states[chat_id] = "waiting_for_ihbar"
    bot.send_message(
        chat_id,
        "🚨 **İhbar Modülü Aktif**\n\nLütfen şüpheli bağlantıyı, sosyal medya hesabını veya dolandırıcılık olayını detaylıca yazıp gönder. (Kanıt/Ekran görüntüsü de ekleyebilirsin)",
        parse_mode="Markdown",
    )

  elif call.data == "islem_basvuru":
    user_states[chat_id] = "waiting_for_basvuru"
    bot.send_message(
        chat_id,
        "🛡️ **Ekip Başvuru Modülü**\n\nNeden Gölge Timi'ne katılmak istiyorsun ve hangi alanda (Tasarım, Araştırma, Sosyal Medya) yeteneklisin? Kendinden kısaca bahset.",
        parse_mode="Markdown",
    )

  elif call.data == "islem_bilgi":
    bot.send_message(
        chat_id,
        "ℹ️ **Gölge Timi Nedir?**\n\nİnternetteki dolandırıcılıklara, sahte hesaplara ve tehditlere karşı insanları bilinçlendiren, dijital güvenliği savunan bağımsız bir topluluk projesidir.",
        parse_mode="Markdown",
    )


# --- MESAJ YÖNETİCİSİ (İHBAR VE BAŞVURU ALMA) ---
@bot.message_handler(
    func=lambda message: True, content_types=["text", "photo"]
)
def handle_user_messages(message):
  chat_id = message.chat.id
  state = user_states.get(chat_id)

  if state == "waiting_for_ihbar":
    # Burada normalde bu ihbarı yönetim kanalına / veritabanına atarsın
    bot.send_message(
        chat_id,
        "✅ **İhbarınız Alındı!**\n\nAraştırma ekibimiz verileri inceleyecektir. Hassasiyetiniz için teşekkürler.",
        parse_mode="Markdown",
    )
    user_states[chat_id] = None  # Durumu sıfırla

  elif state == "waiting_for_basvuru":
    bot.send_message(
        chat_id,
        "✅ **Başvurunuz Alındı!**\n\nYönetim ekibimiz başvurunuzu inceleyip sizinle iletişime geçecektir.",
        parse_mode="Markdown",
    )
    user_states[chat_id] = None  # Durumu sıfırla


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))

  # Webhook'u Telegram'a Tanımlama Komutu
  WEBHOOK_URL = f"https://golge.onrender.com/{TOKEN}"
  bot.remove_webhook()
  bot.set_webhook(url=WEBHOOK_URL)

  app.run(host="0.0.0.0", port=port)
