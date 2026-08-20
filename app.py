import streamlit as st
import re
from collections import Counter


# ============================================================
# БЕТТІ БАПТАУ
# ============================================================

st.set_page_config(
    page_title="Қазақ тіліндегі эссені бағалау",
    page_icon="📝",
    layout="centered"
)


# ============================================================
# ҚОСЫМША СТИЛЬ
# ============================================================

st.markdown("""
<style>
.main-title {
    text-align: center;
    font-size: 34px;
    font-weight: bold;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: gray;
    margin-bottom: 30px;
}

.result-box {
    padding: 20px;
    border-radius: 10px;
    background-color: #f5f5f5;
    margin-top: 20px;
}

.big-score {
    font-size: 35px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# МӘТІНДЕГІ СӨЗДЕР
# ============================================================

def get_words(text):
    return re.findall(
        r"[А-Яа-яӘәҒғҚқҢңӨөҰұҮүҺһІіЁёA-Za-z'-]+",
        text
    )


# ============================================================
# СӨЙЛЕМДЕР
# ============================================================

def get_sentences(text):
    sentences = re.split(r"[.!?]+", text)

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


# ============================================================
# АБЗАЦТАР
# ============================================================

def get_paragraphs(text):
    paragraphs = re.split(r"\n+", text)

    return [
        paragraph.strip()
        for paragraph in paragraphs
        if paragraph.strip()
    ]


# ============================================================
# СӨЗДІ ҚАЛЫПҚА КЕЛТІРУ
# ============================================================

def normalize(word):
    return word.lower().strip(
        ".,!?;:()[]{}\"'«»"
    )


# ============================================================
# 1. ТАҚЫРЫПҚА СӘЙКЕСТІК — 20 БАЛЛ
# ============================================================

def check_topic(title, essay):

    title_words = [
        normalize(word)
        for word in get_words(title)
        if len(word) >= 4
    ]

    essay_lower = essay.lower()

    if not title_words:
        return 10, "⚠ Тақырыпты нақтырақ енгізу қажет."

    found = 0

    for word in title_words:
        if word in essay_lower:
            found += 1

    ratio = found / len(title_words)

    if ratio >= 0.75:
        return 20, "✓ Эссенің негізгі ойы тақырыпқа толық сәйкес."

    elif ratio >= 0.50:
        return 18, "✓ Эссенің негізгі ойы тақырыпқа сәйкес."

    elif ratio >= 0.30:
        return 14, "⚠ Тақырып жартылай ашылған."

    else:
        return 9, "⚠ Эссе тақырыбын толығырақ ашу қажет."


# ============================================================
# 2. ҚҰРЫЛЫМЫ — 20 БАЛЛ
# ============================================================

def check_structure(essay):

    paragraphs = get_paragraphs(essay)
    sentences = get_sentences(essay)

    score = 0

    # Абзац саны
    if len(paragraphs) >= 3:
        score += 10
    elif len(paragraphs) == 2:
        score += 7
    else:
        score += 4

    # Сөйлем саны
    if len(sentences) >= 10:
        score += 5
    elif len(sentences) >= 6:
        score += 4
    else:
        score += 2

    # Қорытынды сөздер
    conclusion_words = [
        "қорыта",
        "қорытындылай",
        "қорытынды",
        "осылайша",
        "сонымен",
        "демек",
        "түйіндей"
    ]

    essay_lower = essay.lower()

    has_conclusion = any(
        word in essay_lower
        for word in conclusion_words
    )

    if has_conclusion:
        score += 5
    else:
        score += 3

    score = min(score, 20)

    if score >= 17:
        comment = "✓ Кіріспе және қорытынды бөлімдері анықталған."
    elif score >= 13:
        comment = "⚠ Эссе құрылымы жақсы, бірақ бөлімдерді нақтылауға болады."
    else:
        comment = "⚠ Эссені кіріспе, негізгі бөлім және қорытындыға бөліңіз."

    return score, comment


# ============================================================
# 3. СӨЗДІК ҚОРЫ — 15 БАЛЛ
# ============================================================

def check_vocabulary(essay):

    words = [
        normalize(word)
        for word in get_words(essay)
    ]

    if not words:
        return 0, "⚠ Сөздер анықталмады."

    unique_words = set(words)

    diversity = len(unique_words) / len(words)

    if diversity >= 0.65:
        return 15, "✓ Сөздік қоры өте бай."

    elif diversity >= 0.55:
        return 13, "✓ Сөздік қоры жақсы."

    elif diversity >= 0.45:
        return 12, "✓ Сөздік қоры жеткілікті."

    elif diversity >= 0.35:
        return 9, "⚠ Кейбір сөздер жиі қайталанады."

    else:
        return 6, "⚠ Сөздік қорды байыту қажет."


# ============================================================
# 4. ГРАММАТИКА — 20 БАЛЛ
# ============================================================

def check_grammar(essay):

    score = 20
    problems = []

    sentences = get_sentences(essay)

    # Сөйлем кіші әріптен бастала ма?
    lowercase_sentences = 0

    for sentence in sentences:

        if (
            sentence
            and sentence[0].isalpha()
            and sentence[0].islower()
        ):
            lowercase_sentences += 1

    if lowercase_sentences > 0:
        score -= min(3, lowercase_sentences)
        problems.append(
            "кейбір сөйлемдер кіші әріптен басталған"
        )

    # Артық бос орын
    if "  " in essay:
        score -= 1
        problems.append("артық бос орындар бар")

    # Тыныс белгісінің алдындағы бос орын
    if re.search(r"\s+[,.!?;:]", essay):
        score -= 2
        problems.append(
            "тыныс белгілерінің алдында артық бос орын бар"
        )

    # Өте көп тыныс белгісі
    if re.search(r"[!?.,]{3,}", essay):
        score -= 2
        problems.append(
            "тыныс белгілері шамадан тыс қолданылған"
        )

    # Тым ұзын сөйлемдер
    long_sentences = 0

    for sentence in sentences:

        sentence_words = get_words(sentence)

        if len(sentence_words) > 30:
            long_sentences += 1

    if long_sentences > 0:
        score -= min(4, long_sentences)

        problems.append(
            "кейбір сөйлемдер тым ұзақ"
        )

    score = max(score, 0)

    if not problems:
        comment = "✓ Негізгі грамматикалық талаптар сақталған."
    else:
        comment = "⚠ " + "; ".join(problems).capitalize() + "."

    return score, comment


# ============================================================
# 5. БАЙЛАНЫСТЫЛЫҚ — 15 БАЛЛ
# ============================================================

def check_coherence(essay):

    linking_words = [
        "біріншіден",
        "екіншіден",
        "үшіншіден",
        "сонымен қатар",
        "алайда",
        "дегенмен",
        "өйткені",
        "себебі",
        "сондықтан",
        "демек",
        "мысалы",
        "осылайша",
        "сонымен",
        "қорыта"
    ]

    essay_lower = essay.lower()

    found = []

    for word in linking_words:
        if word in essay_lower:
            found.append(word)

    count = len(found)

    if count >= 5:
        return 15, "✓ Ойлар бір-бірімен өте жақсы байланысқан."

    elif count >= 3:
        return 13, "✓ Ойлар арасында жақсы байланыс бар."

    elif count >= 1:
        return 10, "⚠ Байланыстырушы сөздерді көбірек қолдануға болады."

    else:
        return 6, (
            "⚠ «Біріншіден», «алайда», «сондықтан», "
            "«қорыта айтқанда» сияқты сөздерді қолданыңыз."
        )


# ============================================================
# 6. КӨЛЕМІ — 10 БАЛЛ
# ============================================================

def check_length(essay):

    word_count = len(get_words(essay))

    if 200 <= word_count <= 350:
        return 10, "✓ Эссе көлемі талапқа сай."

    elif 150 <= word_count < 200:
        return 8, "⚠ Эссені сәл толықтыруға болады."

    elif 100 <= word_count < 150:
        return 6, "⚠ Эссенің көлемін арттыру қажет."

    elif word_count > 350:
        return 8, "⚠ Эссе ұсынылған көлемнен ұзын."

    else:
        return 4, "⚠ Эссе тым қысқа."


# ============================================================
# ҚАЙТАЛАНАТЫН СӨЗДЕР
# ============================================================

def find_repeated_words(essay):

    stop_words = {
        "және", "мен", "бұл", "үшін",
        "деген", "болып", "оның", "олар",
        "бірақ", "ғана", "тағы", "өте",
        "бар", "жоқ", "еді", "екен"
    }

    words = [
        normalize(word)
        for word in get_words(essay)
    ]

    useful_words = [
        word
        for word in words
        if len(word) >= 4
        and word not in stop_words
    ]

    counter = Counter(useful_words)

    return [
        (word, count)
        for word, count in counter.most_common(5)
        if count >= 3
    ]


# ============================================================
# ИНТЕРФЕЙС
# ============================================================

st.markdown(
    '<div class="main-title">📝 Қазақ тіліндегі эссені бағалау жүйесі</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Эссені критерийлер бойынша автоматты бағалау</div>',
    unsafe_allow_html=True
)


# Эссе тақырыбы
title = st.text_input(
    "Эссе тақырыбы",
    placeholder="Мысалы: Жасанды интеллекттің білім берудегі маңызы"
)


# Эссе мәтіні
essay = st.text_area(
    "Эссе мәтіні",
    height=350,
    placeholder="Эссеңізді осы жерге жазыңыз..."
)


# ============================================================
# СӨЗ САНЫ
# ============================================================

word_count = len(get_words(essay))

st.write(f"**Сөз саны: {word_count}**")


# ============================================================
# БАҒАЛАУ БАТЫРМАСЫ
# ============================================================

if st.button(
    "Эссені бағалау",
    type="primary",
    use_container_width=True
):

    if not title.strip():

        st.warning(
            "Эссе тақырыбын енгізіңіз."
        )

    elif not essay.strip():

        st.warning(
            "Эссе мәтінін енгізіңіз."
        )

    elif word_count < 30:

        st.error(
            "Бағалау үшін кемінде 30 сөз жазу қажет."
        )

    else:

        # --------------------------------------------
        # БАҒАЛАРДЫ ЕСЕПТЕУ
        # --------------------------------------------

        topic_score, topic_comment = check_topic(
            title,
            essay
        )

        structure_score, structure_comment = check_structure(
            essay
        )

        vocabulary_score, vocabulary_comment = check_vocabulary(
            essay
        )

        grammar_score, grammar_comment = check_grammar(
            essay
        )

        coherence_score, coherence_comment = check_coherence(
            essay
        )

        length_score, length_comment = check_length(
            essay
        )


        # Жалпы балл
        total = (
            topic_score
            + structure_score
            + vocabulary_score
            + grammar_score
            + coherence_score
            + length_score
        )


        # ====================================================
        # НӘТИЖЕ
        # ====================================================

        st.divider()

        st.subheader("📊 Бағалау нәтижесі")

        st.markdown(
            f'<div class="big-score">Нәтиже: {total} / 100</div>',
            unsafe_allow_html=True
        )

        st.progress(total / 100)


        # ====================================================
        # КРИТЕРИЙЛЕР
        # ====================================================

        st.subheader("Критерийлер")

        st.write(
            f"**Тақырыпқа сәйкестік:** "
            f"{topic_score} / 20"
        )

        st.write(
            f"**Құрылымы:** "
            f"{structure_score} / 20"
        )

        st.write(
            f"**Сөздік қоры:** "
            f"{vocabulary_score} / 15"
        )

        st.write(
            f"**Грамматика:** "
            f"{grammar_score} / 20"
        )

        st.write(
            f"**Байланыстылық:** "
            f"{coherence_score} / 15"
        )

        st.write(
            f"**Көлемі:** "
            f"{length_score} / 10"
        )


        # ====================================================
        # КЕРІ БАЙЛАНЫС
        # ====================================================

        st.subheader("💬 Кері байланыс")

        st.write(topic_comment)

        st.write(structure_comment)

        st.write(vocabulary_comment)

        st.write(grammar_comment)

        st.write(coherence_comment)

        st.write(length_comment)


        # ====================================================
        # ҚАЙТАЛАНАТЫН СӨЗДЕР
        # ====================================================

        repeated = find_repeated_words(essay)

        if repeated:

            st.write(
                "⚠ **Қайталанатын сөздерді азайтқан дұрыс:**"
            )

            for word, count in repeated:

                st.write(
                    f"• {word} — {count} рет"
                )


        # ====================================================
        # ҚОРЫТЫНДЫ БАҒА
        # ====================================================

        st.subheader("🎓 Қорытынды")

        if total >= 90:

            st.success(
                f"Өте жақсы! Жалпы нәтиже: {total}/100"
            )

        elif total >= 75:

            st.success(
                f"Жақсы нәтиже! Жалпы балл: {total}/100"
            )

        elif total >= 60:

            st.warning(
                f"Қанағаттанарлық. Жалпы балл: {total}/100"
            )

        else:

            st.error(
                f"Эссені жетілдіру қажет. Жалпы балл: {total}/100"
            )


        st.caption(
            "Ескерту: жүйе мәтінді автоматты алгоритм арқылы "
            "бағалайды. Ол мұғалімнің кәсіби бағасын толық алмастырмайды."
        )
