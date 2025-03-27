import os
import random
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from sheets import write_order

BOT_TOKEN = os.getenv("8009333235:AAGw-i0xJUhosC-Dci_DmmzVoCLKtCIwgOE")
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("Biz haqimizda"))
main_menu.add(KeyboardButton("Xizmatlar"))
main_menu.add(KeyboardButton("Buyurtma berish"))
main_menu.add(KeyboardButton("Aloqa"))

motivatsiya = [
    "Harakat – natijaning kaliti.",
    "Har kuni yangi imkoniyat!",
    "Orzularingizga ishoning – ular sizni chaqiryapti.",
    "Qilmagan xatolaringizdan qo‘rqmang – ular yo‘l ko‘rsatadi.",
]

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(
        f"Assalomu alaykum, {message.from_user.first_name}!\n"
        "Men — Ruya Vision Assistent botiman. Quyidagilardan birini tanlang:",
        reply_markup=main_menu
    )

@dp.message_handler(lambda message: message.text == "Biz haqimizda")
async def about_us(message: types.Message):
    photo = InputFile("logo.jpeg")
    await bot.send_photo(chat_id=message.chat.id, photo=photo,
        caption="**RUYA VISION** — bu zamonaviy kontent yaratish, mobilografiya, dizayn va reklama sohalarida xizmat ko‘rsatadigan ijodiy jamoa.\n"
                "🎯 Maqsadimiz – mijozlarimizga sifatli vizual kontent va marketing yechimlarini taqdim etish.",
        parse_mode='Markdown'
    )

@dp.message_handler(lambda message: message.text == "Xizmatlar")
async def services(message: types.Message):
    await message.answer(
        "Bizning xizmatlar quyidagilarni o‘z ichiga oladi (birgalikda):"
        "- Mobilografiya"
        "- Content meykerlik"
        "- Grafik dizayn"
        "- Targeting va Instagram boshqaruvi"
    )

@dp.message_handler(lambda message: message.text == "Aloqa")
async def contact(message: types.Message):
    contact_markup = InlineKeyboardMarkup()
    contact_markup.add(
        InlineKeyboardButton("Instagram", url="https://www.instagram.com/ruyavisionuz?igsh=MTF4MXp4ZDNiMHhi"),
        InlineKeyboardButton("Telegram", url="https://t.me/ruyavisionadmin")
    )
    await message.answer("Quyidagi tugmalar orqali biz bilan bog‘lanishingiz mumkin:", reply_markup=contact_markup)

class OrderStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_comment = State()

@dp.message_handler(lambda message: message.text == "Buyurtma berish")
async def order(message: types.Message):
    await message.answer("Buyurtma berish uchun ismingizni yozing:")
    await OrderStates.waiting_for_name.set()

@dp.message_handler(state=OrderStates.waiting_for_name, content_types=types.ContentTypes.TEXT)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Telefon raqamingizni kiriting:")
    await OrderStates.waiting_for_phone.set()

@dp.message_handler(state=OrderStates.waiting_for_phone, content_types=types.ContentTypes.TEXT)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Qo‘shimcha izoh yoki xizmat bo‘yicha izoh qoldiring:")
    await OrderStates.waiting_for_comment.set()

@dp.message_handler(state=OrderStates.waiting_for_comment, content_types=types.ContentTypes.TEXT)
async def finish_order(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data['name']
    phone = user_data['phone']
    comment = message.text

    write_order(name, phone, comment)

    order_text = f"Yangi buyurtma:"
    Ismi: {name}
    Tel: {phone}
    Izoh: {comment}
    await message.answer(order_text)

    quote = random.choice(motivatsiya)
    await message.answer(f"Rahmat! Tez orada siz bilan bog‘lanamiz.")
    Motivatsiya: {quote}

    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
