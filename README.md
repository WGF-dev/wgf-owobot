# OwO Bot Hunter

Discord OwO botunda **hunt**, **kutu açma**, **silah kutusu**, **savaş** ve **pet takımı** gibi tüm aktiviteleri rate limit’e uygun çalıştıran betik.

## Ne yapar?

| Aktivite | Açıklama | Varsayılan komut / süre |
|----------|----------|--------------------------|
| **Hunt** | Hayvan avlama | `wh` — 15 saniyede bir |
| **Lootbox** | Kutu açma (gem için) | `owo lb all` — 5 dakikada bir |
| **Weapon crate** | Silah kutusu açma | `owo wc` — 10 dakikada bir |
| **Battle** | Başka biriyle savaş (petlerle) | `owo battle @kullanıcı 0` — 3 dakikada bir |
| **Setteam** | Takım 1’i seç (petleri gücüne göre kullan) | `owo setteam 1` — 1 saatte bir |
| **Daily** | Günlük ödül | `owo daily` — 24 saatte bir |
| **Quest** | Günlük görev | `owo quest` — 24 saatte bir |

Bot, hangi aktivitenin sırası geldiyse onu çalıştırır (en uzun süredir yapılmayan önce). Rate limit ve captcha’ya göre bekleyip tekrar dener.

## Petleri gücüne göre ayarlama

OwO’da otomatik “en güçlü petleri seç” yok; takım numarasıyla seçim yapılıyor. Yapman gereken:

1. OwO’da **en güçlü 3 petini** **Takım 1**’e koy (`owo team` ile bak, takımı OwO’nun kendi komutlarıyla ayarla).
2. Config’de `setteam_enabled = True` ve `setteam_command = "owo setteam 1"` kalsın.
3. Bot periyodik olarak `owo setteam 1` atarak bu takımı seçili tutar.

Yani “güce göre ayarlama” = sen takım 1’i güçlü petlerle dolduruyorsun, bot sadece o takımı seçiyor.

## Kurulum

1. **Python yüklü değilse:** [python.org/downloads](https://www.python.org/downloads/) adresinden Python 3.10+ indir. Kurulumda **"Add Python to PATH"** kutusunu işaretle.

2. **Yapılandırma:** `config.example.py` dosyasını `config.py` olarak kopyala, ardından `config.py` içinde `token` ve `channel_id` değerlerini doldur.
   - Windows: `copy config.example.py config.py`
   - Linux/Mac: `cp config.example.py config.py`

3. Bağımlılıkları yükle (PowerShell veya CMD’de):

```bash
cd wgf-owobot
pip install -r requirements.txt
```

`pip` tanınmıyorsa şunu dene:

```bash
python -m pip install -r requirements.txt
```

Windows’ta bazen Python launcher ile:

```bash
py -m pip install -r requirements.txt
```

## Ayarlar (`config.py`)

Önce `config.example.py` dosyasını `config.py` olarak kopyalayıp düzenle (Kurulum adım 2). **Asla** token veya API anahtarını içeren `config.py` dosyasını GitHub'a yükleme.

**Zorunlu:** `token`, `channel_id`

**Aktiviteler (hepsi açıkken bot hepsini yapar):**

| Değişken | Açıklama |
|----------|----------|
| `hunt_enabled` | Hunt açık/kapalı |
| `hunt_command` | Örn. `wh`, `owo h` |
| `hunt_interval_seconds` | Kaç saniyede bir (örn. 15) |
| `lootbox_enabled` | Kutu açma açık/kapalı |
| `lootbox_command` | Örn. `owo lb all` veya `owo lb 50` (max 100) |
| `lootbox_interval_seconds` | Örn. 300 (5 dk) |
| `weapon_crate_enabled` | Silah kutusu açık/kapalı |
| `weapon_crate_command` | Örn. `owo wc` |
| `weapon_crate_interval_seconds` | Örn. 600 (10 dk) |
| `battle_enabled` | Savaş açık/kapalı |
| `battle_target` | Savaşılacak kullanıcı: `<@USER_ID>` veya sadece `USER_ID` |
| `battle_command_template` | Örn. `owo battle {target} 0` (bahis 0) |
| `battle_interval_seconds` | Örn. 180 (3 dk) |
| `setteam_enabled` | Takım seçimi açık/kapalı |
| `setteam_command` | Örn. `owo setteam 1` (güçlü takımın 1 ise) |
| `setteam_interval_seconds` | Örn. 3600 (1 saat) |
| `daily_enabled` / `quest_enabled` | Günlük ve quest (24 saatte bir mantığı) |

**Rate limit:** `base_delay_seconds` (12+ önerilir), `randomize_delay`, `min/max_random_delay_seconds`, `max_delay_seconds`, `exit_on_captcha`, `max_consecutive_failures`.

**Yapay zeka (opsiyonel):** Kanal mesajları LLM ile analiz edilir; captcha, rate limit ve hata daha akıllı tespit edilir.

| Değişken | Açıklama |
|----------|----------|
| `ai_enabled` | `True` = AI analizi açık |
| `ai_api_key` | OpenAI API key (veya Together vb.). Ollama için `ollama` yazabilirsin. |
| `ai_base_url` | Boş = OpenAI. Ollama için `http://localhost:11434`. Together vb. için kendi URL. |
| `ai_model` | Örn. `gpt-4o-mini` (OpenAI), `llama3.2` (Ollama), `mistral` (Ollama). |

AI kapalıyken sadece anahtar kelime ile captcha tespiti yapılır; AI açıkken hem anahtar kelime hem LLM sonucu kullanılır.

**Yapay zeka çalışıyor mu nasıl anlarım?**  
Botu çalıştırdığında konsolda şunları görürsün:
- Açılışta: `Yapay zeka analizi açık (model: gpt-4o-mini)` (veya kullandığın model)
- İlk analizde: `Yapay zeka bağlantısı hazır (...)`
- Her komut sonrası: `Yapay zeka mesajları analiz ediyor...` ardından `Yapay zeka sonucu: status=ok, reason=-, bekleme=0`  
Bu satırları görüyorsan yapay zeka çalışıyordur. Görmüyorsan `ai_enabled = True` ve `ai_api_key` dolu mu kontrol et; API erişilemiyorsa `Yapay zeka yanıt alamadı, anahtar kelime kontrolü kullanılıyor` uyarısı çıkar.

## Çalıştırma

```bash
python main.py
```

- 429 alınırsa `Retry-After` kadar beklenir.
- Captcha tespit edilirse (config’e göre) program durur veya 60 sn bekleyip devam eder.

## Uyarı

- Discord **kullanıcı token’ı** kullanımı Discord ToS’a aykırı olabilir; kendi riskinle kullan.
- Rate limit için `base_delay_seconds` değerini düşürme (en az 12–15 saniye önerilir).
- **Savaş** için `battle_target` doldurman gerekir; boşsa battle atlanır.
