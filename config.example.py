# OwO Bot Hunter - Yapılandırma Şablonu
# Kurulum: Bu dosyayı config.py olarak kopyala ve aşağıdaki değerleri doldur.
#   Windows: copy config.example.py config.py
#   Linux/Mac: cp config.example.py config.py
#
# Kendi token ve channel_id değerlerini gir (Discord kullanıcı token'ı)

# Discord kullanıcı token'ı (gerekli)
# Uyarı: User token kullanımı Discord ToS'a aykırı olabilir, kendi riskinle kullan.
token = ""

# OwO komutlarının çalıştığı kanal ID'si
channel_id = "1"

# ========== AKTİVİTELER (şu an: sadece para odaklı, biraz hızlı) ==========

# --- Hunt (hayvan avlama → sat = para) ---
hunt_enabled = True
hunt_command = "wh"
hunt_interval_seconds = 12  # biraz hızlı (rate limit'e dikkat)

# --- Lootbox (gem = hunt bonus, dolaylı para) ---
lootbox_enabled = True
lootbox_command = "owo lb all"
lootbox_interval_seconds = 300  # 5 dk

# --- Silah kutusu / savaş / takım: para odaklı değil, kapalı ---
weapon_crate_enabled = False
weapon_crate_command = "owo wc"
weapon_crate_interval_seconds = 600

battle_enabled = False
battle_target = ""
battle_command_template = "owo battle {target} 0"
battle_interval_seconds = 180

setteam_enabled = False
setteam_command = "owo setteam 1"
setteam_interval_seconds = 3600

# --- Günlük / quest (direkt cowoncy) ---
daily_enabled = True
daily_command = "owo daily"
daily_interval_seconds = 86400  # 24 saat
quest_enabled = True
quest_command = "owo quest"
quest_interval_seconds = 86400

# --- Satış (hayvanları paraya çevir) ---
sell_enabled = True
sell_command = "owo sell all"
sell_interval_seconds = 1800  # 30 dakikada bir

# ========== GENEL RATE LİMİT (biraz hızlandırıldı) ==========
base_delay_seconds = 12  # 15 → 12
randomize_delay = True
min_random_delay_seconds = 0
max_random_delay_seconds = 3  # 1-5 → 0-3
rate_limit_backoff_multiplier = 1.5
max_delay_seconds = 120

# Captcha / hata
exit_on_captcha = True
check_captcha_after_send = True
max_consecutive_failures = 5
log_level = "INFO"

# ========== YAPAY ZEKA (opsiyonel) ==========
# Açıksa, kanal mesajları LLM ile analiz edilir; captcha/rate_limit/hata daha akıllı tespit edilir.
ai_enabled = False
# OpenAI API key (OpenAI, Together, vb. için). Ollama için api_key "ollama" veya herhangi bir değer olabilir.
ai_api_key = ""
# Boş = OpenAI resmi. Ollama için: http://localhost:11434. Together vb. için kendi base URL'in.
ai_base_url = ""
# Model: OpenAI "gpt-4o-mini", Ollama "llama3.2", "mistral" vb.
ai_model = "gpt-4o-mini"
