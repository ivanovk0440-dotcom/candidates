import asyncio
import json
import os
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

# ==================== КОНФИГУРАЦИЯ ====================

SUPPORT_BOT_TOKEN = "8551087174:AAEnVZyU9vQl0cT89gPurxs0KtCLbdE3HrY"
ADMIN_ID = 7912200734

storage = MemoryStorage()
bot = Bot(token=SUPPORT_BOT_TOKEN)
dp = Dispatcher(storage=storage)

DIALOGS_FILE = "dialogs.json"
CONFIG_FILE = "config.json"

# ==================== СОСТОЯНИЯ ====================

class AdminReplyState(StatesGroup):
    waiting_for_reply = State()

class AdminSetVideoLinkState(StatesGroup):
    waiting_for_link = State()

# ==================== КОНФИГ ====================

def load_config():
    """Загружает конфиг с ссылкой на video bot"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "video_bot_link": "https://t.me/shadepnbot",
        "pinned_message_id": None
    }

def save_config(config):
    """Сохраняет конфиг"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# ==================== ДИАЛОГИ ====================

def load_dialogs():
    """Загружает диалоги"""
    if os.path.exists(DIALOGS_FILE):
        with open(DIALOGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_dialogs(dialogs):
    """Сохраняет диалоги"""
    with open(DIALOGS_FILE, "w", encoding="utf-8") as f:
        json.dump(dialogs, f, ensure_ascii=False, indent=2)

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def get_video_bot_keyboard():
    """Возвращает клавиатуру с кнопкой на Video Bot"""
    config = load_config()
    video_bot_link = config.get("video_bot_link", "https://t.me/shadepnbot")
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Перейти в 18Video Bot", url=video_bot_link)]
    ])

def get_video_bot_keyboard_with_extra(extra_buttons=None):
    """Возвращает клавиатуру с Video Bot и дополнительными кнопками"""
    config = load_config()
    video_bot_link = config.get("video_bot_link", "https://t.me/shadepnbot")
    
    buttons = []
    
    if extra_buttons:
        buttons.extend(extra_buttons)
    
    buttons.append([InlineKeyboardButton(text="🚀 Перейти в 18Video Bot", url=video_bot_link)])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ==================== ОБНОВЛЕНИЕ ЗАКРЕПЛЕННОГО СООБЩЕНИЯ ====================

async def update_pinned_message():
    """🔄 Обновляет закрепленное сообщение с актуальной ссылкой"""
    config = load_config()
    video_bot_link = config.get("video_bot_link", "https://t.me/shadepnbot")
    
    text = (
        "🎬 <b>18Video Bot</b>\n\n"
        "✨ Создавайте видео из фотографий с помощью AI\n\n"
        "📊 <b>Возможности:</b>\n"
        "✓ Преобразование фото в видео\n"
        "✓ Оплата Telegram Stars или CryptoBot\n"
        "✓ Быстрая генерация\n\n"
        "💬 <b>Поддержка:</b>\n"
        "Нажмите кнопку ниже если у вас есть вопросы"
    )
    
    pinned_msg_id = config.get("pinned_message_id")
    
    try:
        if pinned_msg_id:
            try:
                await bot.edit_message_text(
                    chat_id=ADMIN_ID,
                    message_id=pinned_msg_id,
                    text=text,
                    parse_mode="HTML",
                    reply_markup=get_video_bot_keyboard_with_extra([
                        [InlineKeyboardButton(text="💬 Написать в поддержку", callback_data="write_support")]
                    ])
                )
                print(f"✅ Закрепленное сообщение обновлено (ID: {pinned_msg_id})")
                return
            except Exception as e:
                print(f"⚠️ Ошибка при редактировании: {e}")
                pinned_msg_id = None
        
        # Если сообщения не было - создаем новое
        if not pinned_msg_id:
            msg = await bot.send_message(
                ADMIN_ID,
                text,
                parse_mode="HTML",
                reply_markup=get_video_bot_keyboard_with_extra([
                    [InlineKeyboardButton(text="💬 Написать в поддержку", callback_data="write_support")]
                ])
            )
            
            config["pinned_message_id"] = msg.message_id
            save_config(config)
            
            try:
                await bot.pin_chat_message(ADMIN_ID, msg.message_id)
                print(f"✅ Сообщение закреплено (ID: {msg.message_id})")
            except:
                print("⚠️ Не удалось закрепить сообщение")
    
    except Exception as e:
        print(f"❌ Ошибка при обновлении закрепленного сообщения: {e}")

# ==================== ОСНОВНЫЕ ОБРАБОТЧИКИ ====================

@dp.message(Command("start"))
async def start(message: types.Message):
    """Начало диалога в боте поддержки"""
    config = load_config()
    video_bot_link = config.get("video_bot_link", "https://t.me/shadepnbot")
    
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    
    # Сохраняем диалог
    dialogs = load_dialogs()
    if str(user_id) not in dialogs:
        dialogs[str(user_id)] = {
            "username": username,
            "full_name": full_name,
            "active": True,
            "created_at": datetime.now().isoformat()
        }
        save_dialogs(dialogs)
    else:
        dialogs[str(user_id)]["active"] = True
        save_dialogs(dialogs)
    
    await message.answer(
        "👋 <b>Привет!</b>\n\n"
        "Это бот поддержки 18Video Bot.\n\n"
        "🎬 <b>Хочешь создать видео?</b>\n"
        "Нажми кнопку ниже и перейди в генератор видео.\n\n"
        "📝 <b>Есть вопросы?</b>\n"
        "Напиши сообщение и я отправлю его админу. Он ответит тебе в течение часа.\n\n"
        "⚠️ Чтобы закончить диалог - напиши /stop",
        parse_mode="HTML",
        reply_markup=get_video_bot_keyboard_with_extra([
            [InlineKeyboardButton(text="❓ Часто задаваемые вопросы", callback_data="faq")]
        ])
    )

@dp.callback_query(F.data == "write_support")
async def write_support_button(callback: types.CallbackQuery):
    """Кнопка 'Написать в поддержку' из закрепленного сообщения"""
    user_id = callback.from_user.id
    
    dialogs = load_dialogs()
    if str(user_id) not in dialogs:
        dialogs[str(user_id)] = {
            "username": callback.from_user.username,
            "full_name": callback.from_user.full_name,
            "active": True,
            "created_at": datetime.now().isoformat()
        }
        save_dialogs(dialogs)
    else:
        dialogs[str(user_id)]["active"] = True
        save_dialogs(dialogs)
    
    await callback.message.answer(
        "📝 Напиши свой вопрос или проблему.\n\n"
        "Я отправлю сообщение админу и он ответит тебе.\n\n"
        "⚠️ Чтобы закончить диалог - напиши /stop",
        reply_markup=get_video_bot_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "faq")
async def show_faq(callback: types.CallbackQuery):
    """ЧЗВ"""
    await callback.message.answer(
        "❓ <b>Часто задаваемые вопросы</b>\n\n"
        
        "<b>Как создать видео?</b>\n"
        "1️⃣ Откройте генератор видео\n"
        "2️⃣ Отправьте фотографию\n"
        "3️⃣ Напишите описание движения\n"
        "4️⃣ Выберите способ оплаты\n"
        "5️⃣ Получите видео\n\n"
        
        "<b>Сколько это стоит?</b>\n"
        "💰 49 Telegram Stars или 0.55 USDT\n\n"
        
        "<b>Сколько ждать?</b>\n"
        "⏱️ Примерно 7 минут\n\n"
        
        "<b>Какие форматы видео?</b>\n"
        "🎬 MP4, WebM\n\n"
        
        "<b>Вопрос не решен?</b>\n"
        "Напиши нам в чат ниже 👇",
        parse_mode="HTML",
        reply_markup=get_video_bot_keyboard_with_extra([
            [InlineKeyboardButton(text="💬 Написать в поддержку", callback_data="write_support")]
        ])
    )
    await callback.answer()

# ==================== ОБРАБОТКА СООБЩЕНИЙ ОТ ПОЛЬЗОВАТЕЛЕЙ ====================

@dp.message(lambda message: message.from_user.id != ADMIN_ID)
async def handle_user_message(message: types.Message):
    """Обработка всех сообщений от пользователей"""
    user_id = message.from_user.id
    
    dialogs = load_dialogs()
    if str(user_id) not in dialogs or not dialogs[str(user_id)].get("active", True):
        await message.answer(
            "❌ Диалог закрыт.\n\n"
            "Введи /start чтобы начать новый диалог.",
            reply_markup=get_video_bot_keyboard()
        )
        return
    
    # Формируем сообщение для админа
    admin_text = (
        f"📨 <b>НОВОЕ СООБЩЕНИЕ В ПОДДЕРЖКЕ</b>\n\n"
        f"👤 <b>Имя:</b> {message.from_user.full_name}\n"
        f"🆔 <b>ID:</b> {user_id}\n"
        f"📛 <b>Юзернейм:</b> @{message.from_user.username if message.from_user.username else 'нет'}\n"
        f"🕐 <b>Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
    )
    
    if message.text:
        admin_text += f"💬 <b>Текст:</b>\n{message.text}"
        await bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML")
    
    elif message.photo:
        photo = message.photo[-1]
        admin_text += f"📸 <b>Отправил фото</b>"
        if message.caption:
            admin_text += f"\n📝 <b>Подпись:</b> {message.caption}"
        await bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML")
        await bot.send_photo(ADMIN_ID, photo=photo.file_id)
    
    elif message.document:
        admin_text += f"📎 <b>Отправил файл:</b> {message.document.file_name}"
        await bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML")
        await bot.send_document(ADMIN_ID, document=message.document.file_id)
    
    else:
        admin_text += f"📝 <b>Отправил:</b> {message.content_type}"
        await bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML")
    
    # Кнопка для ответа админу
    await bot.send_message(
        ADMIN_ID,
        f"🔘 Нажми кнопку, чтобы ответить:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✍️ Ответить", callback_data=f"reply_{user_id}")]
        ])
    )
    
    await message.answer(
        "✅ <b>Сообщение отправлено админу.</b>\n\n"
        "⏳ Я ответу тебе в течение часа.",
        parse_mode="HTML",
        reply_markup=get_video_bot_keyboard()
    )

# ==================== АДМИН ОТВЕЧАЕТ ====================

@dp.callback_query(F.data.startswith("reply_"))
async def admin_reply_start(callback: types.CallbackQuery, state: FSMContext):
    """Админ начинает отвечать"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Только для админа!", show_alert=True)
        return
    
    user_id = callback.data.split("_")[1]
    
    await state.update_data(reply_to_user=user_id)
    await state.set_state(AdminReplyState.waiting_for_reply)
    
    await callback.message.answer(
        f"✍️ <b>Ответ пользователю ID: {user_id}</b>\n\n"
        f"Введи текст или отправь фото.\n"
        f"Для отмены нажми /cancel",
        parse_mode="HTML"
    )
    await callback.answer()

@dp.message(StateFilter(AdminReplyState.waiting_for_reply), F.text)
async def admin_send_text_reply(message: types.Message, state: FSMContext):
    """Админ отправляет текстовый ответ"""
    if message.from_user.id != ADMIN_ID:
        return
    
    data = await state.get_data()
    user_id = data.get("reply_to_user")
    
    if not user_id:
        await message.answer("❌ Ошибка: нет пользователя для ответа")
        await state.clear()
        return
    
    try:
        await bot.send_message(
            int(user_id),
            f"📩 <b>Ответ от админа:</b>\n\n{message.text}",
            parse_mode="HTML",
            reply_markup=get_video_bot_keyboard()
        )
        
        await message.answer(f"✅ Ответ отправлен пользователю {user_id}")
        await state.clear()
        
        await bot.send_message(
            int(user_id),
            "✍️ Ты можешь ответить админу, просто написав сообщение сюда.",
            reply_markup=get_video_bot_keyboard()
        )
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@dp.message(StateFilter(AdminReplyState.waiting_for_reply), F.photo)
async def admin_send_photo_reply(message: types.Message, state: FSMContext):
    """Админ отправляет фото в ответ"""
    if message.from_user.id != ADMIN_ID:
        return
    
    data = await state.get_data()
    user_id = data.get("reply_to_user")
    
    if not user_id:
        await message.answer("❌ Ошибка: нет пользователя для ответа")
        await state.clear()
        return
    
    try:
        photo = message.photo[-1]
        caption = "📩 <b>Ответ от админа</b>"
        if message.caption:
            caption = f"📩 <b>Ответ от админа:</b>\n\n{message.caption}"
        
        await bot.send_photo(
            int(user_id),
            photo=photo.file_id,
            caption=caption,
            parse_mode="HTML",
            reply_markup=get_video_bot_keyboard()
        )
        
        await message.answer(f"✅ Фото отправлено пользователю {user_id}")
        await state.clear()
        
        await bot.send_message(
            int(user_id),
            "✍️ Ты можешь ответить админу, просто написав сообщение сюда.",
            reply_markup=get_video_bot_keyboard()
        )
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@dp.message(Command("cancel"))
async def cancel_reply(message: types.Message, state: FSMContext):
    """Отмена ответа"""
    current_state = await state.get_state()
    if current_state == AdminReplyState.waiting_for_reply:
        await state.clear()
        await message.answer("❌ Отправка ответа отменена")

# ==================== КОМАНДЫ ПОЛЬЗОВАТЕЛЯ ====================

@dp.message(Command("stop"))
async def stop_dialog(message: types.Message):
    """Завершение диалога"""
    user_id = message.from_user.id
    
    dialogs = load_dialogs()
    if str(user_id) in dialogs:
        dialogs[str(user_id)]["active"] = False
        save_dialogs(dialogs)
    
    await message.answer(
        "✅ <b>Диалог завершён.</b>\n\n"
        "Введи /start чтобы начать новый диалог.",
        parse_mode="HTML",
        reply_markup=get_video_bot_keyboard()
    )

# ==================== АДМИН-ПАНЕЛЬ ====================

@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    """Админ-панель"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Доступ запрещен")
        return
    
    config = load_config()
    video_bot_link = config.get("video_bot_link", "https://t.me/ai_video_studio_bot")
    
    await message.answer(
        f"⚙️ <b>АДМИН-ПАНЕЛЬ</b>\n\n"
        f"🔗 <b>Текущая ссылка на Video Bot:</b>\n"
        f"<code>{video_bot_link}</code>\n\n"
        f"<b>КОМАНДЫ:</b>\n"
        f"/set_video_link - 🔗 Изменить ссылку на Video Bot\n"
        f"/update_pinned - 🔄 Обновить закрепленное сообщение\n"
        f"/dialogs - 💬 Активные диалоги\n"
        f"/stats - 📊 Статистика",
        parse_mode="HTML"
    )

@dp.message(Command("set_video_link"))
async def set_video_link(message: types.Message, state: FSMContext):
    """✏️ Изменить ссылку на Video Bot"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Доступ запрещен")
        return
    
    await state.set_state(AdminSetVideoLinkState.waiting_for_link)
    await message.answer(
        "🔗 <b>Введи новую ссылку на Video Bot:</b>\n\n"
        "Пример: <code>https://t.me/ai_video_studio_bot</code>\n\n"
        "Для отмены нажми /cancel",
        parse_mode="HTML"
    )

@dp.message(StateFilter(AdminSetVideoLinkState.waiting_for_link))
async def process_video_link(message: types.Message, state: FSMContext):
    """Обработка новой ссылки"""
    if message.from_user.id != ADMIN_ID:
        return
    
    new_link = message.text.strip()
    
    if not new_link.startswith("https://t.me/"):
        await message.answer(
            "❌ Ссылка должна быть в формате:\n"
            "<code>https://t.me/bot_username</code>",
            parse_mode="HTML"
        )
        return
    
    config = load_config()
    config["video_bot_link"] = new_link
    save_config(config)
    
    await message.answer(
        f"✅ <b>Ссылка обновлена!</b>\n\n"
        f"🔗 Новая ссылка:\n"
        f"<code>{new_link}</code>\n\n"
        f"Нажми /update_pinned чтобы обновить закрепленное сообщение",
        parse_mode="HTML"
    )
    
    await state.clear()

@dp.message(Command("update_pinned"))
async def update_pinned(message: types.Message):
    """🔄 Обновить закрепленное сообщение"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Доступ запрещен")
        return
    
    await message.answer("⏳ Обновляю закрепленное сообщение...")
    await update_pinned_message()
    await message.answer("✅ Закрепленное сообщение обновлено!")

@dp.message(Command("dialogs"))
async def show_dialogs(message: types.Message):
    """💬 Активные диалоги"""
    if message.from_user.id != ADMIN_ID:
        return
    
    dialogs = load_dialogs()
    if not dialogs:
        await message.answer("✅ Нет диалогов")
        return
    
    active_count = sum(1 for d in dialogs.values() if d.get("active", True))
    
    text = f"💬 <b>АКТИВНЫЕ ДИАЛОГИ ({active_count}):</b>\n\n"
    for uid, data in dialogs.items():
        if data.get("active", True):
            created = data.get("created_at", "неизвестно")[:10]
            text += (
                f"🆔 {uid}\n"
                f"👤 {data.get('full_name', 'нет')}\n"
                f"📛 @{data.get('username', 'нет')}\n"
                f"📅 {created}\n\n"
            )
    
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("stats"))
async def show_stats(message: types.Message):
    """📊 Статистика"""
    if message.from_user.id != ADMIN_ID:
        return
    
    dialogs = load_dialogs()
    active_dialogs = sum(1 for d in dialogs.values() if d.get("active", True))
    all_dialogs = len(dialogs)
    
    config = load_config()
    video_bot_link = config.get("video_bot_link", "https://t.me/ai_video_studio_bot")
    
    await message.answer(
        f"📊 <b>СТАТИСТИКА</b>\n\n"
        f"💬 Всего диалогов: {all_dialogs}\n"
        f"🟢 Активных диалогов: {active_dialogs}\n"
        f"🔗 Ссылка на Video Bot: {video_bot_link}",
        parse_mode="HTML"
    )

# ==================== ЗАПУСК ====================

async def main():
    print("=" * 70)
    print("💬 Support Bot запущен!")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print("=" * 70)
    
    # Обновляем закрепленное сообщение при старте
    await update_pinned_message()
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
