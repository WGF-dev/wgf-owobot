"""
OwO görev tanımları ve sıra mantığı.
Hangisi sırada: en uzun süredir yapılmayan aktivite seçilir (interval'a göre).
"""
import time
import logging

logger = logging.getLogger(__name__)


def _get_activities(config):
    """Config'den açık aktiviteleri (isim, komut, interval) listesi olarak al."""
    out = []
    if getattr(config, "hunt_enabled", True):
        out.append(("hunt", getattr(config, "hunt_command", "wh"), getattr(config, "hunt_interval_seconds", 15)))
    if getattr(config, "lootbox_enabled", False):
        out.append(("lootbox", getattr(config, "lootbox_command", "owo lb all"), getattr(config, "lootbox_interval_seconds", 300)))
    if getattr(config, "weapon_crate_enabled", False):
        out.append(("weapon_crate", getattr(config, "weapon_crate_command", "owo wc"), getattr(config, "weapon_crate_interval_seconds", 600)))
    if getattr(config, "battle_enabled", False):
        target = getattr(config, "battle_target", "").strip()
        if target:
            if not target.startswith("<@"):
                target = f"<@{target}>"
            cmd = getattr(config, "battle_command_template", "owo battle {target} 0").format(target=target)
            out.append(("battle", cmd, getattr(config, "battle_interval_seconds", 180)))
        else:
            logger.debug("battle açık ama battle_target boş, atlanıyor.")
    if getattr(config, "setteam_enabled", False):
        out.append(("setteam", getattr(config, "setteam_command", "owo setteam 1"), getattr(config, "setteam_interval_seconds", 3600)))
    if getattr(config, "daily_enabled", False):
        out.append(("daily", getattr(config, "daily_command", "owo daily"), getattr(config, "daily_interval_seconds", 86400)))
    if getattr(config, "quest_enabled", False):
        out.append(("quest", getattr(config, "quest_command", "owo quest"), getattr(config, "quest_interval_seconds", 86400)))
    if getattr(config, "sell_enabled", False):
        out.append(("sell", getattr(config, "sell_command", "owo sell all"), getattr(config, "sell_interval_seconds", 1800)))
    return out


class Scheduler:
    """
    Her aktivite için son yapılma zamanını tutar.
    next() ile sıradaki (en uzun süredir yapılmayan) aktiviteyi verir.
    """
    def __init__(self, config):
        self.config = config
        self.last_done = {}  # activity_name -> timestamp
        self.activities = _get_activities(config)

    def next(self):
        """Returns (activity_name, command_string, wait_seconds). wait_seconds > 0 ise önce bu kadar bekle."""
        if not self.activities:
            return None, None, 0
        now = time.time()
        overdue = []
        for name, cmd, interval in self.activities:
            last = self.last_done.get(name, 0)
            waited = now - last
            if waited >= interval:
                overdue.append((name, cmd, waited))
        if overdue:
            overdue.sort(key=lambda x: -x[2])
            return overdue[0][0], overdue[0][1], 0
        next_wait = []
        for name, cmd, interval in self.activities:
            last = self.last_done.get(name, 0)
            remaining = interval - (now - last)
            next_wait.append((name, cmd, max(0, remaining)))
        next_wait.sort(key=lambda x: x[2])
        name, cmd, remaining = next_wait[0]
        return name, cmd, remaining

    def mark_done(self, activity_name):
        self.last_done[activity_name] = time.time()
