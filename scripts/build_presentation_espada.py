import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PPTX_PATH = OUTPUT_DIR / "Espada_Qala_Astana.pptx"

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.dml.color import RGBColor
except ImportError:
    print("python-pptx not available")
    sys.exit(1)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Color Palette — Espada Cyber Luxury
DARK_BG = RGBColor(9, 14, 28)
CARD_BG = RGBColor(17, 26, 48)
CARD_BORDER = RGBColor(34, 52, 92)
CYAN = RGBColor(0, 234, 255)
BLUE = RGBColor(68, 148, 255)
GREEN = RGBColor(46, 224, 154)
GOLD = RGBColor(255, 196, 54)
PURPLE = RGBColor(186, 104, 255)
WHITE = RGBColor(255, 255, 255)
MUTED = RGBColor(150, 173, 209)
MUTED_DARK = RGBColor(100, 125, 165)

def apply_slide_bg(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = DARK_BG

def add_header(slide, title_text, category_text, slide_num, total_slides=8):
    # Team & Track Badge
    badge_shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.42), Inches(3.2), Inches(0.35))
    badge_shape.fill.solid()
    badge_shape.fill.fore_color.rgb = RGBColor(24, 40, 72)
    badge_shape.line.color.rgb = CYAN
    badge_shape.line.width = Pt(1)
    tf_b = badge_shape.text_frame
    tf_b.word_wrap = False
    p_b = tf_b.paragraphs[0]
    p_b.text = f"TEAM ESPADA · {category_text.upper()}"
    p_b.font.size = Pt(10)
    p_b.font.bold = True
    p_b.font.color.rgb = CYAN
    p_b.alignment = PP_ALIGN.CENTER

    # Title
    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(10.5), Inches(0.8))
    tf = t_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = WHITE

    # Slide Counter
    num_box = slide.shapes.add_textbox(Inches(11.3), Inches(0.42), Inches(1.2), Inches(0.35))
    tf_n = num_box.text_frame
    p_n = tf_n.paragraphs[0]
    p_n.text = f"{slide_num:02d} / {total_slides:02d}"
    p_n.font.size = Pt(12)
    p_n.font.bold = True
    p_n.font.color.rgb = MUTED
    p_n.alignment = PP_ALIGN.RIGHT

# -------------------------------------------------------------
# SLIDE 1: Cover — Team Espada
# -------------------------------------------------------------
s1 = prs.slides.add_slide(prs.slide_layouts[6])
apply_slide_bg(s1)

# Glow bar on top
bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(1.8), Inches(0.08))
bar.fill.solid()
bar.fill.fore_color.rgb = CYAN
bar.line.fill.background()

# Tag
tag_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.0), Inches(11.5), Inches(0.4))
p = tag_box.text_frame.paragraphs[0]
p.text = "BUILD WITH AI · ТРЕК 1: НИЦ SMART CITY & GDG ASTANA"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = CYAN

# Team Espada Brand Name
main_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.5), Inches(2.2))
tf = main_box.text_frame
p = tf.paragraphs[0]
p.text = "QALA ASTANA 2.0"
p.font.size = Pt(56)
p.font.bold = True
p.font.color.rgb = WHITE

p2 = tf.add_paragraph()
p2.text = "Интеллектуальный RAG-гид по прогулкам нового поколения"
p2.font.size = Pt(22)
p2.font.bold = True
p2.font.color.rgb = GREEN

# Description
desc_box = s1.shapes.add_textbox(Inches(0.8), Inches(3.7), Inches(11.5), Inches(1.5))
tf_d = desc_box.text_frame
tf_d.word_wrap = True
p = tf_d.paragraphs[0]
p.text = "Гибридный советчик по городской среде Астаны: соединяет строгий Retrieval по 821 POI OpenStreetMap, алгоритм пешеходной доступности и генерацию мотиваций («Почему») и планов («Что делать») на базе DeepSeek-V3."
p.font.size = Pt(15)
p.font.color.rgb = MUTED

# 4 Key Pillars Cards at bottom
pillars = [
    ("⚡ 821 POI Астаны", "Автоматический сбор и обогащение из OpenStreetMap Overpass", CYAN),
    ("🧠 DeepSeek-V3 + Local", "Двухрежимная RAG генерация с нулевыми галлюцинациями", GREEN),
    ("🎯 5 из 5 Стретч-целей", "Мини-маршруты, KZ/RU/EN, инклюзивность, группы, афиша", GOLD),
    ("🛡️ Zero Retention", "100% конфиденциальность: координаты не сохраняются", PURPLE),
]

card_w = Inches(2.75)
card_h = Inches(1.4)
spacing = Inches(0.18)
start_x = Inches(0.8)
start_y = Inches(5.3)

for i, (title, sub, color) in enumerate(pillars):
    x = start_x + i * (card_w + spacing)
    card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, start_y, card_w, card_h)
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = color
    card.line.width = Pt(1.5)

    tf_c = card.text_frame
    tf_c.word_wrap = True
    p1 = tf_c.paragraphs[0]
    p1.text = title
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = color

    p2 = tf_c.add_paragraph()
    p2.text = sub
    p2.font.size = Pt(10)
    p2.font.color.rgb = MUTED

# Footer team attribution
foot = s1.shapes.add_textbox(Inches(0.8), Inches(6.9), Inches(11.5), Inches(0.4))
p_f = foot.text_frame.paragraphs[0]
p_f.text = "Разработано командой ESPADA · Build with AI 2026"
p_f.font.size = Pt(11)
p_f.font.bold = True
p_f.font.color.rgb = GOLD

# -------------------------------------------------------------
# SLIDE 2: Problem vs Espada Solution
# -------------------------------------------------------------
s2 = prs.slides.add_slide(prs.slide_layouts[6])
apply_slide_bg(s2)
add_header(s2, "Проблема пользователя и решение команды Espada", "Концепция продукта", 2)

# Column 1: Problem (Red tone)
col1 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.9))
col1.fill.solid()
col1.fill.fore_color.rgb = RGBColor(28, 20, 30)
col1.line.color.rgb = RGBColor(220, 53, 69)
col1.line.width = Pt(1.5)

tf1 = col1.text_frame
tf1.word_wrap = True
p = tf1.paragraphs[0]
p.text = "❌ КАК ЕСТЬ СЕЙЧАС (БОЛИ)"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = RGBColor(255, 100, 100)

points_fail = [
    ("Сотни слепых точек на картах", "2GIS и Google Maps вываливают десятки маркеров. Пользователь тратит 15 минут на чтение чужих отзывов вместо прогулки."),
    ("Галлюцинации стандартных LLM", "ChatGPT и базовые боты уверенно придумывают закрытые заведения, путают расстояния и не знают погоду Астаны."),
    ("Ограничение по времени (30–60 мин)", "Ни один навигатор не понимает запрос: «У меня 45 минут между встречами, где выпить кофе с розеткой и успеть вернуться»."),
    ("Слепая уверенность в статусах", "Боты пишут «открыто прямо сейчас», когда место уже на ремонте или имеет санитарный день."),
]

for title, desc in points_fail:
    p_t = tf1.add_paragraph()
    p_t.text = f"• {title}:"
    p_t.font.size = Pt(12)
    p_t.font.bold = True
    p_t.font.color.rgb = WHITE
    p_d = tf1.add_paragraph()
    p_d.text = f"  {desc}"
    p_d.font.size = Pt(11)
    p_d.font.color.rgb = RGBColor(210, 170, 170)

# Column 2: Espada Solution (Green tone)
col2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.8), Inches(5.6), Inches(4.9))
col2.fill.solid()
col2.fill.fore_color.rgb = RGBColor(16, 32, 44)
col2.line.color.rgb = GREEN
col2.line.width = Pt(1.5)

tf2 = col2.text_frame
tf2.word_wrap = True
p = tf2.paragraphs[0]
p.text = "✅ КАК РЕШАЕТ QALA ASTANA (ESPADA)"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = GREEN

points_win = [
    ("Готовый сценарий за 1 секунду", "Выдача 1–3 идеальных мест с обоснованием («Почему») и конкретным планом («Что сделать там»)."),
    ("Строгий двухэтапный RAG", "Retrieval по 821 проверенному POI Астаны + генерация DeepSeek-V3 строго в рамках контекста без вымысла."),
    ("Учёт контекста Астаны (UTC+5)", "Система знает время суток: днем ведет на аллеи и выставки, вечером — к иллюминации Экспо и видовым лаунжам."),
    ("Честная степень уверенности", "Дисклеймер на часах работы, разделение источников («Данные POI» vs «Текст ИИ») и нулевое логирование GPS."),
]

for title, desc in points_win:
    p_t = tf2.add_paragraph()
    p_t.text = f"• {title}:"
    p_t.font.size = Pt(12)
    p_t.font.bold = True
    p_t.font.color.rgb = WHITE
    p_d = tf2.add_paragraph()
    p_d.text = f"  {desc}"
    p_d.font.size = Pt(11)
    p_d.font.color.rgb = RGBColor(170, 225, 200)

# -------------------------------------------------------------
# SLIDE 3: Two-stage RAG Pipeline Architecture
# -------------------------------------------------------------
s3 = prs.slides.add_slide(prs.slide_layouts[6])
apply_slide_bg(s3)
add_header(s3, "Архитектура двухэтапного RAG-пайплайна", "Технологический стек", 3)

steps = [
    ("1. СБОР & ОБОГАЩЕНИЕ", "Автоматизация данных", [
        "OpenStreetMap Overpass API (BBOX Астаны)",
        "Обогащение тегами: розетки, Wi-Fi, пандусы, события",
        "821 валидированная точка интереса в JSON-кэше",
        "In-memory mtime кэширование без задержек",
    ], CYAN),
    ("2. RETRIEVAL (ПОИСК)", "Гибридное ранжирование", [
        "Лексический BM25 + семантический интент",
        "Spatial Decay: затухание веса с дистанцией",
        "Жёсткие фильтры: дети, группы, ночь, коляски",
        "Расчёт пешеходной матрицы и таймингов",
    ], BLUE),
    ("3. GENERATION (ИИ)", "Генерация рекомендаций", [
        "Dual-engine: DeepSeek-V3 (флагман) / Local RAG",
        "Контекст времени Астаны (UTC+5: вечер/день)",
        "Синтез «Почему подходит» (краткая мотивация)",
        "Синтез «Что делать там» (пошаговый план)",
    ], GREEN),
]

col_w = Inches(3.65)
for i, (title, sub, bullets, color) in enumerate(steps):
    x = Inches(0.8) + i * (col_w + Inches(0.35))
    box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), col_w, Inches(4.8))
    box.fill.solid()
    box.fill.fore_color.rgb = CARD_BG
    box.line.color.rgb = color
    box.line.width = Pt(1.5)

    tf_s = box.text_frame
    tf_s.word_wrap = True
    p1 = tf_s.paragraphs[0]
    p1.text = title
    p1.font.size = Pt(15)
    p1.font.bold = True
    p1.font.color.rgb = color

    p2 = tf_s.add_paragraph()
    p2.text = sub
    p2.font.size = Pt(11)
    p2.font.bold = True
    p2.font.color.rgb = MUTED

    tf_s.add_paragraph() # spacer

    for b in bullets:
        pb = tf_s.add_paragraph()
        pb.text = f"✔ {b}"
        pb.font.size = Pt(11)
        pb.font.color.rgb = WHITE

# -------------------------------------------------------------
# SLIDE 4: Validation of Official Hackathon Scenarios
# -------------------------------------------------------------
s4 = prs.slides.add_slide(prs.slide_layouts[6])
apply_slide_bg(s4)
add_header(s4, "Проверка официальных сценариев из ТЗ хакатона", "Тестирование и валидация", 4)

cases_data = [
    ("🛍️ Mega Silk Way (30–60 мин)", "Локация: Expo / Mega Silk Way (51.0891, 71.4073)", "Система выбирает ТРЦ Mega Silk Way (1 мин), Линейный парк Expo (7 мин) и Музей «Нұр Әлем» (9 мин). Точный расчет времени, шагов и калорий.", CYAN),
    ("☕ Кофе и розетка", "Локация: Центр Астаны (51.1352, 71.4241)", "Фильтрация кафе с подтвержденными розетками и тишиной для ноутбука: Кафе «Көктем» (Коктем), Zebra Coffee. Никаких выдуманных удобств.", GREEN),
    ("👶 С ребёнком (площадки / музей)", "Локация: Экспо (51.0898, 71.4147)", "Интерактивный парк Happylon Ocean Park в ТРЦ + 8 этажей науки в сфере «Нұр Әлем». Фильтр kids_friendly гарантирует безопасность.", GOLD),
    ("✈️ Перед вылетом (Аэропорт)", "Краевой случай: 51.0250, 71.4650", "Честное информирование: система НЕ галлюцинирует ложные места у кромки карты, а сообщает о границе данных и советует сдвинуться в зону.", PURPLE),
    ("🌙 Ночная активность (вечер)", "Локация: Hilton Expo (51.0872, 71.4180)", "The Cloud Bar на крыше Hilton до 02:00, ночные пабы и вечерняя подсветка сферы Expo. Привязка к часам работы заведений.", BLUE),
]

row_h = Inches(0.92)
for i, (title, loc, res, col) in enumerate(cases_data):
    y = Inches(1.8) + i * (row_h + Inches(0.1))
    c_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, Inches(11.7), row_h)
    c_box.fill.solid()
    c_box.fill.fore_color.rgb = CARD_BG
    c_box.line.color.rgb = col
    c_box.line.width = Pt(1)

    tf_c = c_box.text_frame
    tf_c.word_wrap = True
    p1 = tf_c.paragraphs[0]
    p1.text = title
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = col

    r = p1.add_run()
    r.text = f"  [{loc}]"
    r.font.size = Pt(10)
    r.font.bold = False
    r.font.color.rgb = MUTED

    p2 = tf_c.add_paragraph()
    p2.text = res
    p2.font.size = Pt(10)
    p2.font.color.rgb = WHITE

# -------------------------------------------------------------
# SLIDE 5: All 5 Stretch Goals (Unfair Advantage)
# -------------------------------------------------------------
s5 = prs.slides.add_slide(prs.slide_layouts[6])
apply_slide_bg(s5)
add_header(s5, "100% Выполнение стретч-целей (Бонусные баллы)", "Креативность и инновации", 5)

stretch_goals = [
    ("🗺️ Мини-маршрут (3 точки)", "Последовательный маршрут: Старт ➔ Кульминация ➔ Финал. Подсчет времени каждого перехода, суммарный километраж, шаги и ккал.", CYAN),
    ("🌐 Мультиязычность (3 языка)", "Полная поддержка Казахского (Қазақша), Русского и Английского языков. Аутентичная генерация DeepSeek на родном языке запроса.", GREEN),
    ("👥 Группы (3–5 человек)", "Алгоритм подбора заведений с вместительными столами, лаунж-зонами и парковыми маршрутами для компании друзей или коллег.", GOLD),
    ("♿ Доступная среда", "Фильтрация объектов с подтвержденными пандусами и безбарьерным входом (wheelchair=yes) для маломобильных граждан и мам с колясками.", PURPLE),
    ("🎭 Городская афиша событий", "Интеграция временных выставок, фестивалей робототехники, ярмарок дизайнеров и вечерней подсветки монументов Астаны.", BLUE),
]

for i, (title, desc, color) in enumerate(stretch_goals):
    col_idx = i % 2
    row_idx = i // 2
    w = Inches(5.65)
    h = Inches(1.4) if i < 4 else Inches(1.4)
    x = Inches(0.8) if col_idx == 0 else Inches(6.85)
    y = Inches(1.8) + row_idx * (Inches(1.55))

    if i == 4:
        w = Inches(11.7)
        x = Inches(0.8)

    card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = color
    card.line.width = Pt(1.5)

    tf = card.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = title
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = color

    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(10.5)
    p2.font.color.rgb = WHITE

# -------------------------------------------------------------
# SLIDE 6: Ethics, Privacy & Responsible AI
# -------------------------------------------------------------
s6 = prs.slides.add_slide(prs.slide_layouts[6])
apply_slide_bg(s6)
add_header(s6, "Этика, Privacy и ответственный искусственный интеллект", "Безопасность и доверие", 6)

ethics = [
    ("🛡️ Zero Retention (Приватность геоданных)", "Координаты пользователя обрабатываются строго в оперативной памяти (RAM) в момент запроса. Никакие координаты НЕ сохраняются в базу данных, НЕ логируются на диск и НЕ передаются третьим лицам.", CYAN),
    ("🏷️ Честное разделение источников", "В каждой карточке пользователь видит четкую маркировку: «Факты: OpenStreetMap & Городской реестр POI» vs «Идея: DeepSeek-V3 / Local RAG». Мы не выдаем фантазии модели за реальные городские факты.", GREEN),
    ("⚠️ Отказ от ложных обещаний («Открыто сейчас»)", "Система избегает категоричных утверждений о доступности заведений при неполных данных. Вместо этого выводится вежливая рекомендация уточнить часы перед посещением.", GOLD),
    ("🔊 Инклюзивный Голосовой Аудиогид (TTS)", "Встроенный синтез речи позволяет людям с нарушениями зрения или тем, кто идет пешком в наушниках, прослушать рекомендацию без необходимости смотреть в экран телефона.", PURPLE),
]

for i, (title, desc, color) in enumerate(ethics):
    y = Inches(1.8) + i * Inches(1.22)
    card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, Inches(11.7), Inches(1.12))
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = color
    card.line.width = Pt(1)

    tf = card.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = title
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = color

    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(10.5)
    p2.font.color.rgb = WHITE

# -------------------------------------------------------------
# SLIDE 7: Business Model & Smart City Impact
# -------------------------------------------------------------
s7 = prs.slides.add_slide(prs.slide_layouts[6])
apply_slide_bg(s7)
add_header(s7, "Ценность для города и бизнес-модель", "Экономика и Smart City", 7)

biz_cols = [
    ("🏛️ ДЛЯ ГОРОДА И АКИМАТА", "Умный туризм и культура", [
        "Разгрузка популярных локаций и распределение турпотока",
        "Популяризация культурного наследия и музеев Астаны",
        "Пешеходная доступность и пропаганда здорового образа жизни",
        "Интеграция с городскими событиями и ярмарками",
    ], CYAN),
    ("💼 ДЛЯ БИЗНЕСА И 2GIS", "Партнерская экосистема", [
        "1-click бесшовный переход в 2GIS, Яндекс Карты и Google",
        "Органический приток пешеходного трафика в локальные кафе",
        "Нативная подсветка спешелти-кофеен с розетками и Wi-Fi",
        "B2B API для отелей (Hilton, Marriott) и туристских инфоцентров",
    ], GREEN),
    ("💰 ЭКОНОМИКА РЕШЕНИЯ", "Низкая стоимость владения", [
        "Микро-затраты на LLM: DeepSeek-V3 стоит $0.14 за 1M токенов",
        "Один запрос обходится городу в < 0.0001 $ (доли тенге)",
        "Автономный fallback на Local RAG при сбоях сети",
        "Масштабируемость до миллионов туристов без роста затрат",
    ], GOLD),
]

for i, (title, sub, bullets, color) in enumerate(biz_cols):
    x = Inches(0.8) + i * (Inches(3.65) + Inches(0.35))
    box = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), Inches(3.65), Inches(4.8))
    box.fill.solid()
    box.fill.fore_color.rgb = CARD_BG
    box.line.color.rgb = color
    box.line.width = Pt(1.5)

    tf_b = box.text_frame
    tf_b.word_wrap = True
    p1 = tf_b.paragraphs[0]
    p1.text = title
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = color

    p2 = tf_b.add_paragraph()
    p2.text = sub
    p2.font.size = Pt(11)
    p2.font.bold = True
    p2.font.color.rgb = MUTED

    tf_b.add_paragraph()

    for b in bullets:
        pb = tf_b.add_paragraph()
        pb.text = f"✔ {b}"
        pb.font.size = Pt(11)
        pb.font.color.rgb = WHITE

# -------------------------------------------------------------
# SLIDE 8: Roadmap & Conclusion — Team Espada
# -------------------------------------------------------------
s8 = prs.slides.add_slide(prs.slide_layouts[6])
apply_slide_bg(s8)
add_header(s8, "План развития (Roadmap) и финал", "Команда Espada", 8)

stages = [
    ("ЭТАП 1: ТЕКУЩИЙ MVP (СДЕЛАНО)", "Хакатон Build with AI", [
        "Рабочий двухэтапный RAG-движок (DeepSeek-V3 + Local)",
        "821 валидированная точка POI Астаны с автосинхронизацией",
        "Все 5 сценариев ТЗ и 5 стретч-целей полностью закрыты",
        "Интерактивная карта Leaflet, мобильная адаптация и GPS",
    ], GREEN),
    ("ЭТАП 2: БЛИЖАЙШИЕ 3 МЕСЯЦА", "Городское внедрение", [
        "Telegram WebApp бот (@QalaAstanaBot) с 1-click маршрутами",
        "Интеграция с CTS (автобусы и линия LRT Астаны)",
        "Расширение базы POI на правый берег и старый город",
        "Подключение афиши городских событий Astana Tourism",
    ], CYAN),
    ("ЭТАП 3: ДОЛГОСРОЧНО (6–12 МЕС)", "Экосистема Smart City", [
        "Интеграция в городское приложение Smart Astana / eGov",
        "Голосовой диалоговый ассистент для умных остановок",
        "Персонализация на основе предпочтений пользователя",
        "Тиражирование на другие города (Алматы, Шымкент)",
    ], PURPLE),
]

for i, (title, sub, bullets, color) in enumerate(stages):
    x = Inches(0.8) + i * (Inches(3.65) + Inches(0.35))
    box = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), Inches(3.65), Inches(4.0))
    box.fill.solid()
    box.fill.fore_color.rgb = CARD_BG
    box.line.color.rgb = color
    box.line.width = Pt(1.5)

    tf_b = box.text_frame
    tf_b.word_wrap = True
    p1 = tf_b.paragraphs[0]
    p1.text = title
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = color

    p2 = tf_b.add_paragraph()
    p2.text = sub
    p2.font.size = Pt(10.5)
    p2.font.bold = True
    p2.font.color.rgb = MUTED

    tf_b.add_paragraph()

    for b in bullets:
        pb = tf_b.add_paragraph()
        pb.text = f"✦ {b}"
        pb.font.size = Pt(10.5)
        pb.font.color.rgb = WHITE

# Final Call-to-action bar
cta = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.0), Inches(11.7), Inches(0.9))
cta.fill.solid()
cta.fill.fore_color.rgb = RGBColor(18, 35, 68)
cta.line.color.rgb = GOLD
cta.line.width = Pt(2)

tf_cta = cta.text_frame
p_cta = tf_cta.paragraphs[0]
p_cta.text = "⚔️ КОМАНДА ESPADA · МЫ ГОТОВЫ К ВОПРОСАМ ЖЮРИ!"
p_cta.font.size = Pt(18)
p_cta.font.bold = True
p_cta.font.color.rgb = GOLD
p_cta.alignment = PP_ALIGN.CENTER

p_cta2 = tf_cta.add_paragraph()
p_cta2.text = "Живое демо: http://127.0.0.1:8765 · Документация API: /api/docs"
p_cta2.font.size = Pt(12)
p_cta2.font.color.rgb = WHITE
p_cta2.alignment = PP_ALIGN.CENTER

prs.save(str(PPTX_PATH))
print(f"Презентация команды Espada сохранена: {PPTX_PATH}")
