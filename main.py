import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


# test
# ================ DATABASE ================
def create_db():
    conn = sqlite3.connect('ilm_ummoni.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS survey_results
                 (user_id INTEGER PRIMARY KEY,
                  phone TEXT,
                  q1 TEXT, q2 TEXT, q3 TEXT, q4 TEXT,
                  q5 TEXT, q6 TEXT, q7 TEXT)''')
    conn.commit()
    conn.close()


def save_to_db(user_id, phone, answers):
    conn = sqlite3.connect('ilm_ummoni.db')
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO survey_results 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (user_id, phone, *answers))
    conn.commit()
    conn.close()


def get_all_results():
    conn = sqlite3.connect('ilm_ummoni.db')
    c = conn.cursor()
    c.execute("SELECT * FROM survey_results")
    results = c.fetchall()
    conn.close()
    return results


# ================ BOT SETUP ================
API_TOKEN = '7656155940:AAFe-DztsObR885heYs4lJUFJiKuLt4VX0w'  # <-- O'z tokenizingizni qo'ying
BOSS_CHAT_ID =  1409901886  # <-- Admin ID

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# ================ STATES ================
class SurveyStates(StatesGroup):
    phone = State()
    q1 = State()
    q2 = State()
    q3 = State()
    q3_detail = State()
    q4 = State()
    q4_detail = State()
    q5 = State()
    q6 = State()
    q7 = State()


# ================ PHONE NUMBER HANDLERS ================
@dp.message_handler(commands=['start'])
async def start_survey(message: types.Message):
    if message.from_user.id == BOSS_CHAT_ID:
        await show_admin_panel(message)
    else:
        await message.answer("""🌟 <b>Ilm Ummoni - Ota-onalar So'rovnomasi</b> 🌟

📝 <i>7 ta savolga javob bering, 5 daqiqadan kam vaqt oladi!</i>""", parse_mode='HTML')
        await SurveyStates.phone.set()
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton("📱Siz bilan bog'lanishimiz uchun Telefon raqamingizni qoldiring!", request_contact=True))
        await message.answer("""📱Siz bilan bog'lanishimiz uchun Telefon raqamingizni qoldiring!""",
                             reply_markup=markup,
                             parse_mode='HTML')


@dp.message_handler(content_types=types.ContentType.CONTACT, state=SurveyStates.phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone_number = message.contact.phone_number

    if phone_number.startswith('+'):
        phone_number = phone_number[1:]

    phone_number = ''.join(c for c in phone_number if c.isdigit())

    if len(phone_number) < 9:
        await message.answer("""❌ Telefon raqam noto'g'ri formatda!
👉 Iltimos, qayta urunib ko'ring:""",
                             reply_markup=ReplyKeyboardMarkup(
                                 resize_keyboard=True,
                                 one_time_keyboard=True
                             ).add(KeyboardButton("📱Siz bilan bog'lanishimiz uchun Telefon raqamingizni qoldiring!", request_contact=True)),
                             parse_mode='HTML')
        return

    await state.update_data(phone=phone_number)
    await SurveyStates.q1.set()
    await ask_question1(message)


@dp.message_handler(content_types=types.ContentType.ANY, state=SurveyStates.phone)
async def handle_invalid_phone_input(message: types.Message):
    await message.answer("""❌ <b>Telefon raqam faqat kontakt orqali yuborilishi kerak!</b>

👉 Iltimos, quyidagi tugma orqali yuboring:""",
                         reply_markup=ReplyKeyboardMarkup(
                             resize_keyboard=True,
                             one_time_keyboard=True
                         ).add(KeyboardButton("📱Siz bilan bog'lanishimiz uchun Telefon raqamingizni qoldiring!", request_contact=True)),
                         parse_mode='HTML')
# Phone handler
@dp.message_handler(content_types=types.ContentType.CONTACT, state=SurveyStates.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await SurveyStates.q1.set()
    await ask_question1(message)


# Savol 1
async def ask_question1(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row("✨ Bilim darajasi oshdi")
    markup.row("🔥 Darsga qiziqish oshdi")
    markup.row("💪 Mustaqillik yaxshilandi")
    markup.row("💯 O'ziga ishonch oshdi")
    markup.row("🔄 Hali sezilarli o'zgarish yo'q")

    await message.answer("""📌 <b>1. Farzandingiz qanday natijalarga erishdi?</b>

<i>Bir yoki bir nechta variant tanlang</i>""", reply_markup=markup, parse_mode='HTML')


@dp.message_handler(state=SurveyStates.q1)
async def process_q1(message: types.Message, state: FSMContext):
    await state.update_data(q1=message.text)
    await SurveyStates.q2.set()
    await ask_question2(message)


# Savol 2
async def ask_question2(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row("👩‍🏫 Ajoyib ustozlar")
    markup.row("📚 Zo'r dars uslubi")
    markup.row("🏆 Kafolatlangan natijalar")
    markup.row("🎯 Individual yondashuv")
    markup.row("🏫 Qulay sharoitlar")

    await message.answer("""📌 <b>2. Qaysi jihatlar sizga yoqadi?</b>

<i>Bir nechta variant tanlash mumkin</i>""", reply_markup=markup, parse_mode='HTML')


@dp.message_handler(state=SurveyStates.q2)
async def process_q2(message: types.Message, state: FSMContext):
    await state.update_data(q2=message.text)
    await SurveyStates.q3.set()
    await ask_question3(message)


# Savol 3
async def ask_question3(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row("❌ Yo'q, hammasi yaxshi")
    markup.row("⚠️ Ha, bor - tushuntiraman")

    await message.answer("""📌 <b>3. Qoniqtirmagan jihatlar bormi?</b>""", reply_markup=markup, parse_mode='HTML')


@dp.message_handler(state=SurveyStates.q3)
async def process_q3(message: types.Message, state: FSMContext):
    if "⚠️" in message.text:
        await message.answer("✍️ <b>Iltimos, qoniqtirmagan jihatlaringizni yozing:</b>", parse_mode='HTML')
        await SurveyStates.q3_detail.set()
    else:
        await state.update_data(q3="Yo'q, hammasi yaxshi")
        await SurveyStates.q4.set()
        await ask_question4(message)


@dp.message_handler(state=SurveyStates.q3_detail)
async def process_q3_detail(message: types.Message, state: FSMContext):
    await state.update_data(q3=f"Kamchilik: {message.text}")
    await SurveyStates.q4.set()
    await ask_question4(message)


# Savol 4
async def ask_question4(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row("🟢 Sifat nazorati bor va yoqadi")
    markup.row("🟡 Ma'lumotim yo'q")
    markup.row("🟠 Yaxshi, lekin takomillashtirish kerak")
    markup.row("🔴 Shikoyatlar bor")

    await message.answer("""📌 <b>4. Sifat nazorati haqida fikringiz:</b>

🎯 <i>Ochiq javob muhim!</i>""", reply_markup=markup, parse_mode='HTML')


@dp.message_handler(state=SurveyStates.q4)
async def process_q4(message: types.Message, state: FSMContext):
    if "🔴" in message.text:
        await message.answer("✍️ <b>Iltimos, shikoyatlaringizni yozing:</b>",  parse_mode='HTML')
        await SurveyStates.q4_detail.set()
    else:
        await state.update_data(q4=message.text)
        await SurveyStates.q5.set()
        await ask_question5(message)


@dp.message_handler(state=SurveyStates.q4_detail)
async def process_q4_detail(message: types.Message, state: FSMContext):
    await state.update_data(q4=f"Shikoyat: {message.text}")
    await SurveyStates.q5.set()
    await ask_question5(message)


# Savol 5
async def ask_question5(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row("🆕 Yangi kurslar")
    markup.row("💻 Innovatsion texnologiyalar")
    markup.row("📊 Hisobotlarni ko'paytirish")
    markup.row("🔝 Sifat nazoratini kuchaytirish")
    markup.row("👨‍🏫 Ustozlar treningi")
    markup.row("🗣️ Ota-ona uchrashuvlari")
    markup.row("🏆 Tanlov va musobaqalar")
    markup.row("🛠️ Jihozlar yangilanishi")

    await message.answer("""📌 <b>5. Qanday takliflaringiz bor?</b>

💡 <i>Bir nechta variant tanlash mumkin</i>""", reply_markup=markup, parse_mode='HTML')


@dp.message_handler(state=SurveyStates.q5)
async def process_q5(message: types.Message, state: FSMContext):
    await state.update_data(q5=message.text)
    await SurveyStates.q6.set()
    await ask_question6(message)


# Savol 6
async def ask_question6(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row("🏆 Ishonchli markaz")
    markup.row("✅ Qoniqarli darajada")
    markup.row("📈 Ishonchim o'sib bormoqda")

    await message.answer("""📌 <b>6. Ilm Ummoni sizda qanday ishonch uyg'otadi?</b>""", reply_markup=markup,
                         parse_mode='HTML')


@dp.message_handler(state=SurveyStates.q6)
async def process_q6(message: types.Message, state: FSMContext):
    await state.update_data(q6=message.text)
    await SurveyStates.q7.set()
    await ask_question7(message)


# Savol 7
async def ask_question7(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row("👍 Albatta tavsiya qilaman!")
    markup.row("🤔 O'ylab ko'raman")
    markup.row("👎 Afsuski tavsiya qilolmayman")

    await message.answer("""📌 <b>7. Do'stlaringizga tavsiya qilasizmi?</b>""", reply_markup=markup, parse_mode='HTML')


@dp.message_handler(state=SurveyStates.q7)
async def process_q7(message: types.Message, state: FSMContext):
    await state.update_data(q7=message.text)
    user_data = await state.get_data()

    # Save to database
    answers = [
        user_data.get('q1', ''),
        user_data.get('q2', ''),
        user_data.get('q3', ''),
        user_data.get('q4', ''),
        user_data.get('q5', ''),
        user_data.get('q6', ''),
        user_data.get('q7', '')
    ]
    save_to_db(message.from_user.id, user_data.get('phone'), answers)

    # Final message
    await message.answer("""🎉 <b>So'rovnoma yakunlandi!</b>

📚 <i>Ilm Ummoni jamoasi nomidan katta rahmat!</i>

✨ <b>Farzandingiz uchun yanada sifatli ta'lim berish uchun ishlaymiz!</b>""",
                         reply_markup=types.ReplyKeyboardRemove(), parse_mode='HTML')
    await state.finish()


def calculate_statistics():
    results = get_all_results()
    stats = {
        'q1': {}, 'q2': {}, 'q3': {}, 'q4': {},
        'q5': {}, 'q6': {}, 'q7': {}
    }

    emoji_list = ["✨", "🔥", "💪", "💯", "🔄", "👩‍🏫", "📚", "🏆", "🎯", "🏫",
                  "❌", "⚠️", "🟢", "🟡", "🟠", "🔴", "🆕", "💻", "📊", "🔝",
                  "👨‍🏫", "🗣️", "🏅", "🛠️", "✅", "📈", "👍", "🤔", "👎"]

    for user in results:
        for i in range(1, 8):
            answer = user[i + 1]  # q1=2, q2=3, etc.
            if answer:
                key = f'q{i}'
                # Extract emoji from answer
                emoji = answer.split()[0] if answer.split() and answer.split()[0] in emoji_list else ""
                clean_answer = answer.replace(emoji, "").strip()

                if clean_answer not in stats[key]:
                    stats[key][clean_answer] = {'count': 0, 'emoji': emoji}
                stats[key][clean_answer]['count'] += 1
    return stats


# ================ ADMIN PANEL ================
async def show_admin_panel(message: types.Message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📊 Umumiy statistika", callback_data="show_stats"),
        InlineKeyboardButton("📋 Barcha javoblar", callback_data="all_responses")
    )
    await message.answer("👨‍💻 <b>Admin paneli:</b>", reply_markup=markup, parse_mode='HTML')


@dp.callback_query_handler(lambda c: c.data == "all_responses")
async def show_all_responses(callback: types.CallbackQuery):
    results = get_all_results()

    if not results:
        await bot.answer_callback_query(callback.id, "Hozircha javoblar mavjud emas")
        return

    response = "📋 <b>Barcha javoblar:</b>\n\n"
    for user in results:
        response += f"👤 <b>Foydalanuvchi ID:</b> {user[0]}\n"
        response += f"📱 <b>Tel:</b> +{user[1]}\n\n"
        response += f"1️⃣ {user[2]}\n\n"
        response += f"2️⃣ {user[3]}\n\n"
        response += f"3️⃣ {user[4]}\n\n"
        response += f"4️⃣ {user[5]}\n\n"
        response += f"5️⃣ {user[6]}\n\n"
        response += f"6️⃣ {user[7]}\n\n"
        response += f"7️⃣ {user[8]}\n\n"
        response += "─────────────────\n\n"

    # Split long messages
    if len(response) > 4000:
        parts = [response[i:i + 4000] for i in range(0, len(response), 4000)]
        for part in parts:
            await bot.send_message(callback.from_user.id, part, parse_mode='HTML')
    else:
        await bot.send_message(callback.from_user.id, response, parse_mode='HTML')

    await bot.answer_callback_query(callback.id)


@dp.callback_query_handler(lambda c: c.data == "show_stats")
async def show_statistics(callback: types.CallbackQuery):
    stats = calculate_statistics()

    response = "📈 <b>Umumiy statistika:</b>\n\n"

    for q_num in range(1, 8):
        q_key = f'q{q_num}'
        response += f"<b>{q_num}-savol:</b>\n"

        if not stats[q_key]:
            response += "❌ Javoblar mavjud emas\n"
        else:
            for answer, data in stats[q_key].items():
                response += f"{data['emoji']} <i>{answer}</i>: <b>{data['count']} ta</b>\n"

        response += "\n"

    await bot.send_message(callback.from_user.id, response, parse_mode='HTML')
    await bot.answer_callback_query(callback.id)
# ================ RUN BOT ================
if __name__ == '__main__':
    create_db()  # Create database
    executor.start_polling(dp, skip_updates=True)