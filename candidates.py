import asyncio
import json
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

TOKEN = "8551087174:AAEnVZyU9vQl0cT89gPurxs0KtCLbdE3HrY"
ADMIN_ID = 890146872

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)

PARTICIPANTS_FILE = "premium_candidates.txt"
DIALOGS_FILE = "dialogs.json"

class AdminReplyState(StatesGroup):
    waiting_for_reply = State()

def load_dialogs():
    if os.path.exists(DIALOGS_FILE):
        with open(DIALOGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_dialogs(dialogs):
    with open(DIALOGS_FILE, "w", encoding="utf-8") as f:
        json.dump(dialogs, f, ensure_ascii=False, indent=2)

def save_user_id(user_id, username, full_name):
    try:
        if os.path.exists(PARTICIPANTS_FILE):
            with open(PARTICIPANTS_FILE, "r", encoding="utf-8") as f:
                existing = [line.split("|")[0].strip() for line in f.readlines() if line.strip()]
        else:
            existing = []
    except:
        existing = []
    
    if str(user_id) not in existing:
        with open(PARTICIPANTS_FILE, "a", encoding="utf-8") as f:
            username_str = f"@{username}" if username else "без юзернейма"
            f.write(f"{user_id} | {username_str} | {full_name}\n")
        return True
    return False

def get_participants_count():
    try:
        if os.path.exists(PARTICIPANTS_FILE):
            with open(PARTICIPANTS_FILE, "r", encoding="utf-8") as f:
                return len(f.readlines())
        return 0
    except:
        return 0

def get_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Узнать про бесплатный премиум", callback_data="info_premium")],
        [InlineKeyboardButton(text="Написать админу", callback_data="write_to_admin")],
        [InlineKeyboardButton(text="Закрыть", callback_data="close")]
    ])

def get_agree_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, я согласен участвовать", callback_data="agree_premium")],
        [InlineKeyboardButton(text="Нет, не интересно", callback_data="decline_premium")]
    ])

def get_admin_reply_keyboard(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ответить пользователю", callback_data=f"reply_{user_id}")]
    ])

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привет! Я бот для набора авторов контента.\n\n"
        "Хочешь получить бесплатный премиум в боте с кружками?\n"
        "Нажми на кнопку, чтобы узнать подробности.",
        reply_markup=get_main_keyboard()
    )

@dp.callback_query(F.data == "info_premium")
async def show_info(callback: types.CallbackQuery):
    info_text = """
ЧТО ТАКОЕ БЕСПЛАТНЫЙ ПРЕМИУМ?

Обычно премиум стоит денег, но ты можешь получить его бесплатно!

ЧТО ДАЁТ ПРЕМИУМ:

Главная фишка: Привязка ссылки на ТВОЙ Telegram-канал к видеокружку
Под каждым твоим кружком будет кнопка
Люди нажимают -> переходят на твой канал
Пассивный трафик 24/7

Кроме того:
10 кружков вместо 5
Приоритет в ленте

ЧТО НУЖНО ОТ ТЕБЯ:

Загружать интересные видеокружки
Создавать живой контент для бота

КАК ЭТО РАБОТАЕТ:

1. Ты загружаешь кружок
2. Прикрепляешь ссылку на свой канал
3. Люди смотрят и нажимают на кнопку
4. Ты получаешь переходы -> рост подписчиков

Чем больше твоих кружков смотрят - тем больше переходов на твой канал!

ГОТОВ УЧАСТВОВАТЬ?
Нажми Согласен - я добавлю тебя в список и выдам премиум!
"""
    
    await callback.message.answer(
        info_text,
        reply_markup=get_agree_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "agree_premium")
async def agree(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    full_name = callback.from_user.full_name
    
    saved = save_user_id(user_id, username, full_name)
    
    if saved:
        await callback.message.answer(
            f"Ты в списке!\n\n"
            f"Твой ID: {user_id} сохранён.\n\n"
            f"Что дальше?\n"
            f"Я передал твою заявку. В ближайшее время тебе выдадут премиум-доступ в боте.\n\n"
            f"А пока можешь начинать готовить кружки для загрузки!"
        )
        
        await bot.send_message(
            ADMIN_ID,
            f"НОВЫЙ УЧАСТНИК!\n\n"
            f"Имя: {full_name}\n"
            f"ID: {user_id}\n"
            f"Юзернейм: @{username if username else 'нет'}\n\n"
            f"Всего в списке: {get_participants_count()}"
        )
    else:
        await callback.message.answer(
            "Ты уже в списке! Премиум будет выдан в ближайшее время."
        )
    
    await callback.answer()

@dp.callback_query(F.data == "decline_premium")
async def decline(callback: types.CallbackQuery):
    await callback.message.answer(
        "Жаль! Если передумаешь - напиши /start и нажми Узнать про бесплатный премиум."
    )
    await callback.answer()

@dp.callback_query(F.data == "write_to_admin")
async def write_to_admin(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    full_name = callback.from_user.full_name
    
    dialogs = load_dialogs()
    if str(user_id) not in dialogs:
        dialogs[str(user_id)] = {
            "username": username,
            "full_name": full_name,
            "active": True
        }
        save_dialogs(dialogs)
    else:
        dialogs[str(user_id)]["active"] = True
        save_dialogs(dialogs)
    
    await callback.message.answer(
        "Напиши своё сообщение админу. Можно отправить текст или фото.\n\n"
        "Админ ответит тебе сюда. Чтобы закончить диалог - напиши /stop"
    )
    await callback.answer()

# Обработка ВСЕХ сообщений от пользователей (НЕ админа)
@dp.message(lambda message: message.from_user.id != ADMIN_ID)
async def handle_all_user_messages(message: types.Message):
    user_id = message.from_user.id
    
    print(f"Получено сообщение от пользователя {user_id}")
    
    dialogs = load_dialogs()
    if str(user_id) not in dialogs or not dialogs[str(user_id)].get("active", True):
        await message.answer("Сначала нажми 'Написать админу' в меню /start")
        return
    
    admin_text = f"📨 СООБЩЕНИЕ ОТ ПОЛЬЗОВАТЕЛЯ\n\n"
    admin_text += f"👤 Имя: {message.from_user.full_name}\n"
    admin_text += f"🆔 ID: {user_id}\n"
    admin_text += f"📛 Юзернейм: @{message.from_user.username if message.from_user.username else 'нет'}\n\n"
    
    if message.text:
        admin_text += f"💬 Текст: {message.text}"
        await bot.send_message(ADMIN_ID, admin_text)
    
    elif message.photo:
        photo = message.photo[-1]
        admin_text += f"📸 Отправил фото"
        if message.caption:
            admin_text += f"\n📝 Подпись: {message.caption}"
        await bot.send_message(ADMIN_ID, admin_text)
        await bot.send_photo(ADMIN_ID, photo=photo.file_id)
    
    elif message.document:
        admin_text += f"📎 Отправил файл: {message.document.file_name}"
        await bot.send_message(ADMIN_ID, admin_text)
        await bot.send_document(ADMIN_ID, document=message.document.file_id)
    
    else:
        admin_text += f"📝 Отправил: {message.content_type}"
        await bot.send_message(ADMIN_ID, admin_text)
    
    await bot.send_message(
        ADMIN_ID,
        f"🔘 Нажми кнопку, чтобы ответить:",
        reply_markup=get_admin_reply_keyboard(user_id)
    )
    
    await message.answer("✅ Сообщение отправлено админу. Ожидай ответа.")

# Админ нажимает кнопку "Ответить"
@dp.callback_query(F.data.startswith("reply_"))
async def admin_reply_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Только для админа!", show_alert=True)
        return
    
    user_id = callback.data.split("_")[1]
    
    await state.update_data(reply_to_user=user_id)
    await state.set_state(AdminReplyState.waiting_for_reply)
    
    await callback.message.answer(
        f"✍️ Введи ответ для пользователя (ID: {user_id})\n"
        f"Можно отправить текст или фото.\n"
        f"Для отмены нажми /cancel"
    )
    await callback.answer()

# Админ отправляет ТЕКСТОВЫЙ ответ (исправленный фильтр)
@dp.message(StateFilter(AdminReplyState.waiting_for_reply), F.text)
async def admin_send_text_reply(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    data = await state.get_data()
    user_id = data.get("reply_to_user")
    
    if not user_id:
        await message.answer("Ошибка: нет пользователя для ответа")
        await state.clear()
        return
    
    try:
        await bot.send_message(
            int(user_id),
            f"📩 Ответ от админа:\n\n{message.text}"
        )
        
        await message.answer(f"✅ Ответ отправлен пользователю {user_id}")
        await state.clear()
        
        await bot.send_message(
            int(user_id),
            "✍️ Ты можешь ответить админу, просто написав сообщение сюда."
        )
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
        print(f"Ошибка: {e}")

# Админ отправляет ФОТО в ответ (исправленный фильтр)
@dp.message(StateFilter(AdminReplyState.waiting_for_reply), F.photo)
async def admin_send_photo_reply(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    data = await state.get_data()
    user_id = data.get("reply_to_user")
    
    if not user_id:
        await message.answer("Ошибка: нет пользователя для ответа")
        await state.clear()
        return
    
    try:
        photo = message.photo[-1]
        caption = f"📩 Ответ от админа"
        if message.caption:
            caption = f"📩 Ответ от админа:\n\n{message.caption}"
        
        await bot.send_photo(
            int(user_id),
            photo=photo.file_id,
            caption=caption
        )
        
        await message.answer(f"✅ Фото отправлено пользователю {user_id}")
        await state.clear()
        
        await bot.send_message(
            int(user_id),
            "✍️ Ты можешь ответить админу, просто написав сообщение сюда."
        )
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
        print(f"Ошибка: {e}")

@dp.message(Command("cancel"))
async def cancel_reply(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == AdminReplyState.waiting_for_reply:
        await state.clear()
        await message.answer("❌ Отправка ответа отменена")

@dp.callback_query(F.data == "close")
async def close(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()

@dp.message(Command("stop"))
async def stop_dialog(message: types.Message):
    user_id = message.from_user.id
    
    dialogs = load_dialogs()
    if str(user_id) in dialogs:
        dialogs[str(user_id)]["active"] = False
        save_dialogs(dialogs)
    
    await message.answer("Диалог завершён. Чтобы начать новый - напиши /start")

@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Доступ запрещён")
        return
    
    await message.answer(
        "⚙️ Админ-панель:\n\n"
        "/list - список участников премиума\n"
        "/dialogs - список активных диалогов\n"
        "/clear_list - очистить список\n"
        "/stats - статистика"
    )

@dp.message(Command("list"))
async def send_list(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        if os.path.exists(PARTICIPANTS_FILE):
            with open(PARTICIPANTS_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            if not lines:
                await message.answer("Список пуст")
                return
            
            await message.answer_document(
                FSInputFile(PARTICIPANTS_FILE),
                caption=f"📋 Участников премиума: {len(lines)}"
            )
        else:
            await message.answer("Список пуст")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

@dp.message(Command("dialogs"))
async def show_dialogs(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    dialogs = load_dialogs()
    if not dialogs:
        await message.answer("Нет активных диалогов")
        return
    
    text = "💬 Активные диалоги:\n\n"
    for uid, data in dialogs.items():
        if data.get("active", True):
            text += f"🆔 ID: {uid} | {data.get('full_name', 'нет имени')} | @{data.get('username', 'нет')}\n"
    
    await message.answer(text)

@dp.message(Command("clear_list"))
async def clear_list(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    with open(PARTICIPANTS_FILE, "w", encoding="utf-8") as f:
        f.write("")
    
    await message.answer("✅ Список очищен")

@dp.message(Command("stats"))
async def stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    count = get_participants_count()
    dialogs = load_dialogs()
    active_dialogs = sum(1 for d in dialogs.values() if d.get("active", True))
    
    await message.answer(
        f"📊 Статистика:\n\n"
        f"Участников премиума: {count}\n"
        f"Активных диалогов: {active_dialogs}"
    )

async def main():
    print("🤖 Бот запущен!")
    print(f"👑 ID админа: {ADMIN_ID}")
    print(f"📁 Файл участников: {PARTICIPANTS_FILE}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())