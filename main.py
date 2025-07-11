import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_TOKEN = "7645408828:AAFiC7MI7lbZV0qDoUlv58vRNlRf2Y_LMVw"
ADMIN_IDS = [7105959922, 6476871794]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

user_language = {}

def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")]
    ])

# /start komandasi
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Tilni tanlang / Выберите язык:", reply_markup=language_keyboard())

# Til tanlanganda
@dp.callback_query(F.data.startswith("lang_"))
async def language_chosen(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = callback.data.split("_")[1]
    user_language[user_id] = lang
    
    if lang == "uz":
        text = (
            "Assalomu alaykum, bu Eltuz portalining murojaat boti.\n\n"
            "Ariza va shikoyatingiz yoki fosh etuvchi ma'lumotingiz bo'lsa, "
            "mazmunini qisqacha tushuntirib yozing. Hujjatlar, foto, audio va "
            "videolar bo'lsa ilova qilib yo'llang. Aloqa uchun telegram manzilingizni yozib yuboring."
        )
    else:
        text = (
            "Здравствуйте. Это бот для обращений портала Eltuz.\n\n"
            "Если у вас есть жалоба или разоблачающая информация, кратко опишите суть. "
            "Прикрепите документы, фото, аудио или видео, если имеются. "
            "Укажите ваш Telegram для связи."
        )
    
    await callback.message.answer(text)
    await callback.answer()

@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    lang = user_language.get(user_id, "uz")
    
    if lang == "uz":
        response_text = "✅ Murojaatingiz qabul qilindi. Adminlar ko'rib chiqadi."
    else:
        response_text = "✅ Ваше обращение принято. Администраторы рассмотрят его."
    
    await message.answer(response_text)
    
    # Foydalanuvchi ma'lumotlarini tayyorlash
    user = message.from_user
    
    # Foydalanuvchi tanlagan tilni aniqlash
    user_selected_lang = user_language.get(user_id, "uz")
    lang_display = "🇺🇿 O'zbekcha" if user_selected_lang == "uz" else "🇷🇺 Русский"
    
    user_info = f"""
📋 YANGI MUROJAAT

👤 Foydalanuvchi ma'lumotlari:
• ID: {user.id}
• Username: @{user.username if user.username else 'Yo\'q'}
• Ism: {user.first_name if user.first_name else 'Yo\'q'}
• Familiya: {user.last_name if user.last_name else 'Yo\'q'}
• Tanlagan til: {lang_display}

💬 Xabar turi: {message.content_type}
📅 Sana: {message.date.strftime('%Y-%m-%d %H:%M:%S')}

📝 Xabar matni:
"""
    
    # Adminlarga xabar yuborish
    for admin_id in ADMIN_IDS:
        try:
            # Avval foydalanuvchi ma'lumotlarini yuborish
            await bot.send_message(chat_id=admin_id, text=user_info)
            
            # Keyin asl xabarni forward qilish
            await bot.forward_message(
                chat_id=admin_id, 
                from_chat_id=message.chat.id, 
                message_id=message.message_id
            )
        except Exception as e:
            logging.error(f"Xabarni admin {admin_id} ga yuborishda xato: {e}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
