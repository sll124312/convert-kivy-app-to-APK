# Standoff 2 Case Simulator - Ban System + Stable
# Все права принадлежат Axelbolt

from kivy.config import Config
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'orientation', 'landscape')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock
import random
import json
import os
import time
from datetime import datetime

SAVE_FILE = "standoff_save.json"

RARITY_COLORS = {
    "Rare": (0.25, 0.55, 1.0, 1),
    "Epic": (0.75, 0.35, 0.95, 1),
    "Legendary": (1.0, 0.65, 0.1, 1),
    "Arcane": (1.0, 0.25, 0.25, 1),
}

RARITY_WEIGHTS = {"Rare": 53, "Epic": 30, "Legendary": 15, "Arcane": 2}

MARKET_PRICES = {
    "Rare": (25, 60),
    "Epic": (90, 180),
    "Legendary": (350, 700),
    "Arcane": (1200, 3500),
}

CASES = {
    "Dynasty Case": {"price": 100, "skins": {
        "Rare": ["Five-Seven Aquamarine", "MAC10 Pixel", "MP5 Iron"],
        "Epic": ["G22 Briar", "P350 Ooze", "AWM Sylvan"],
        "Legendary": ["Deagle Eclipse", "P90 Noir", "M4A1 Overdrive"],
        "Arcane": ["AKR Genesis", "Mantis Citrine", "Mantis Eclipse"],
    }},
    "Chameleon Case": {"price": 100, "skins": {
        "Rare": ["Deagle Violet Flame", "M4A1 Stainless", "VAL Joker"],
        "Epic": ["M4 Flock", "USP Ghosts", "M40 Disguise"],
        "Legendary": ["TEC-9 Disguise", "MP7 Fright", "AKR12 Mimicry"],
        "Arcane": ["VAL Gilded Gale", "AWM Hohei Taisho", "Gloves Mimicry"],
    }},
    "Revenge Case": {"price": 100, "skins": {
        "Rare": ["USP Ignite", "Berettas Soul", "MAC10 Noxious"],
        "Epic": ["Tec-9 Tie Dye", "P90 Clash", "AWM Kings"],
        "Legendary": ["Berettas Damascus", "MAC10 Shogun", "SPAS Taint"],
        "Arcane": ["Deagle Venator", "M16 Shogun", "Stiletto Damascus"],
    }},
    "Gambit Case": {"price": 100, "skins": {
        "Rare": ["TEC-9 Iris", "P90 Oracle", "FN FAL Splash"],
        "Epic": ["AKR12 Shark", "Deagle Gambit"],
        "Legendary": ["AWM Ravage", "M4 Gambit"],
        "Arcane": ["Butterfly Gambit", "Gloves Dread", "Gloves Gambit"],
    }},
    "Origin Case": {"price": 1000, "skins": {
        "Rare": ["USP Genesis", "P350 Forest", "MP5 Origin"],
        "Epic": ["AKR Origin", "M4A1 Origin"],
        "Legendary": ["AWM Origin", "AKR12 Origin"],
        "Arcane": ["M9 Blue Blood", "M9 Scratch"],
    }},
    "Furious Case": {"price": 1000, "skins": {
        "Rare": ["G22 Fury", "MAC10 Fury"],
        "Epic": ["AKR Furious", "M4 Furious"],
        "Legendary": ["AWM Furious", "Deagle Furious"],
        "Arcane": ["Karambit Purple", "Karambit Gold"],
    }},
    "Fable Case": {"price": 1000, "skins": {
        "Rare": ["G22 Starfall", "Deagle Ace"],
        "Epic": ["USP Pisces", "UMP45 Cerberus"],
        "Legendary": ["Tec-9 Fable", "MP7 Lich"],
        "Arcane": ["Butterfly Legacy", "Butterfly Dragon Glass"],
    }},
    "Scorpion Case": {"price": 1000, "skins": {
        "Rare": ["G22 Scorpion", "MAC10 Scorpion"],
        "Epic": ["AKR Scorpion", "M4 Scorpion"],
        "Legendary": ["AWM Scorpion", "Deagle Scorpion"],
        "Arcane": ["Scorpion Venom", "Scorpion Gold"],
    }},
}

AGENTS = ["Reis", "Lincoln", "Phoenix", "Norton", "Victor", "Caesar", "Shadow", "Venom", "Twilight", "Division"]
AVATARS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C"]  # стабильные вместо смайликов

def load_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "market" not in data:
                    data["market"] = []
                if "bans" not in data:
                    data["bans"] = {}
                return data
        except Exception:
            pass
    return {
        "users": {},
        "next_id": 0,
        "promos": {"WELCOME500": 500, "AXELBOLT": 200, "STANDOFF": 100},
        "clans": {},
        "market": [],
        "bans": {}
    }

def save_data(data):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Save error:", e)

def create_user(data):
    uid = f"{data['next_id']:04d}"
    data["next_id"] += 1
    user = {
        "id": uid,
        "nick": f"Player{uid}",
        "avatar": "1",
        "gold": 500,
        "inventory": [],
        "stats": {"cases_opened": 0, "total_drops": 0, "clicks": 0, "first_login": datetime.now().isoformat()},
        "clan": None,
        "used_promos": []
    }
    data["users"][uid] = user
    save_data(data)
    return user

def get_or_create_user(data):
    if data["users"]:
        last_id = sorted(data["users"].keys())[-1]
        return data["users"][last_id]
    return create_user(data)

def is_banned(data, uid):
    ban = data.get("bans", {}).get(uid)
    if not ban:
        return False, None
    if ban.get("until") == "perm":
        return True, ban
    if time.time() < ban.get("until", 0):
        return True, ban
    # бан истёк
    del data["bans"][uid]
    save_data(data)
    return False, None

def get_market_price(rarity):
    low, high = MARKET_PRICES.get(rarity, (50, 100))
    return random.randint(low, high)

class Btn(Button):
    def __init__(self, bg=(0.15, 0.15, 0.22, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_color = (0, 0, 0, 0)
        with self.canvas.before:
            Color(*bg)
            self.rect = RoundedRectangle(radius=[dp(8)])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self.rect.pos = self.pos
        self.rect.size = self.size

def make_bg(widget, color=(0.07, 0.08, 0.11, 1)):
    with widget.canvas.before:
        Color(*color)
        widget._bg = Rectangle()
    def upd(*a):
        widget._bg.pos = widget.pos
        widget._bg.size = widget.size
    widget.bind(pos=upd, size=upd)

class Splash(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        make_bg(layout)

        title = Label(text="STANDOFF 2\nCASE SIMULATOR", font_size="28sp", bold=True,
                      halign="center", color=(1, 0.72, 0.15, 1),
                      pos_hint={"center_x": 0.5, "center_y": 0.62})
        title.bind(size=title.setter("text_size"))

        disc = Label(text="Все права принадлежат Axelbolt", font_size="14sp",
                     color=(0.55, 0.55, 0.6, 1), pos_hint={"center_x": 0.5, "center_y": 0.45})

        btn = Btn(text="ВОЙТИ", size_hint=(0.3, 0.1),
                  pos_hint={"center_x": 0.5, "center_y": 0.28},
                  bg=(0.95, 0.5, 0.1, 1), font_size="17sp", bold=True)
        btn.bind(on_release=self.enter)

        layout.add_widget(title)
        layout.add_widget(disc)
        layout.add_widget(btn)
        self.add_widget(layout)

    def enter(self, *a):
        app = App.get_running_app()
        app.data = load_data()
        app.user = get_or_create_user(app.data)

        banned, ban_info = is_banned(app.data, app.user["id"])
        if banned:
            self.manager.current = "banned"
            self.manager.get_screen("banned").show_ban(ban_info)
            return

        Clock.schedule_interval(app.check_market_bots, 3.0)
        self.manager.current = "main"

class Banned(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=dp(30), spacing=dp(15))
        make_bg(root, (0.15, 0.05, 0.05, 1))
        self.title = Label(text="ВЫ ЗАБАНЕНЫ", font_size="26sp", bold=True, color=(1, 0.3, 0.3, 1), size_hint_y=0.2)
        self.reason = Label(text="", font_size="16sp", color=(0.9, 0.9, 0.9, 1), size_hint_y=0.3, halign="center")
        self.reason.bind(size=self.reason.setter("text_size"))
        self.time_lbl = Label(text="", font_size="15sp", color=(0.8, 0.7, 0.7, 1), size_hint_y=0.2)
        root.add_widget(self.title)
        root.add_widget(self.reason)
        root.add_widget(self.time_lbl)
        self.add_widget(root)

    def show_ban(self, ban_info):
        self.reason.text = f"Причина: {ban_info.get('reason', 'не указана')}"
        until = ban_info.get("until")
        if until == "perm":
            self.time_lbl.text = "Срок: НАВСЕГДА"
        else:
            left = max(0, int((until - time.time()) / 60))
            self.time_lbl.text = f"Осталось минут: {left}"

class Main(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="horizontal")
        make_bg(root)

        left = BoxLayout(orientation="vertical", size_hint_x=0.1, padding=dp(5), spacing=dp(6))
        make_bg(left, (0.11, 0.12, 0.16, 1))

        menu = [
            ("H", "main"),
            ("C", "cases"),
            ("I", "inv"),
            ("M", "market"),
            ("A", "agents"),
            ("$", "click"),
            ("K", "clans"),
            ("S", "promo"),
        ]
        for icon, scr in menu:
            b = Button(text=icon, font_size="18sp", background_normal="", background_color=(0.16, 0.17, 0.23, 1))
            b.bind(on_release=lambda inst, s=scr: setattr(self.manager, "current", s))
            left.add_widget(b)

        self.admin_btn = Button(text="ADM", font_size="14sp", background_normal="", background_color=(0.4, 0.12, 0.12, 1))
        self.admin_btn.bind(on_release=lambda x: setattr(self.manager, "current", "admin"))
        left.add_widget(self.admin_btn)
        root.add_widget(left)

        center = BoxLayout(orientation="vertical", size_hint_x=0.6, padding=dp(10), spacing=dp(8))

        top = BoxLayout(size_hint_y=0.13, spacing=dp(8))
        self.avatar_lbl = Label(text="1", font_size="22sp", size_hint_x=0.12)
        self.nick_lbl = Label(text="", font_size="15sp", bold=True, color=(1, 0.85, 0.3, 1),
                              halign="left", valign="middle", size_hint_x=0.55)
        self.nick_lbl.bind(size=self.nick_lbl.setter("text_size"))
        self.gold_lbl = Label(text="", font_size="16sp", bold=True, color=(1, 0.9, 0.25, 1), size_hint_x=0.33)
        top.add_widget(self.avatar_lbl)
        top.add_widget(self.nick_lbl)
        top.add_widget(self.gold_lbl)
        center.add_widget(top)

        agent_box = BoxLayout(orientation="vertical", size_hint_y=0.75, padding=dp(15))
        make_bg(agent_box, (0.12, 0.14, 0.19, 1))
        self.agent_lbl = Label(text="Agent\nне выбран", font_size="24sp",
                               color=(0.85, 0.85, 0.9, 1), halign="center")
        self.agent_lbl.bind(size=self.agent_lbl.setter("text_size"))
        agent_box.add_widget(self.agent_lbl)
        center.add_widget(agent_box)
        root.add_widget(center)

        right = BoxLayout(orientation="vertical", size_hint_x=0.3, padding=dp(10), spacing=dp(8))
        make_bg(right, (0.10, 0.11, 0.15, 1))
        right.add_widget(Label(text="БЫСТРЫЕ ДЕЙСТВИЯ", font_size="12sp", color=(0.7, 0.7, 0.75, 1), size_hint_y=0.08))

        for text, scr, col in [
            ("ОТКРЫТЬ КЕЙСЫ", "cases", (0.18, 0.35, 0.55, 1)),
            ("ИНВЕНТАРЬ", "inv", (0.15, 0.4, 0.3, 1)),
            ("РЫНОК", "market", (0.15, 0.42, 0.38, 1)),
            ("КЛИКЕР", "click", (0.55, 0.4, 0.1, 1)),
        ]:
            b = Btn(text=text, bg=col, font_size="13sp", size_hint_y=0.13)
            b.bind(on_release=lambda inst, s=scr: setattr(self.manager, "current", s))
            right.add_widget(b)

        root.add_widget(right)
        self.add_widget(root)

    def on_enter(self, *a):
        app = App.get_running_app()
        if not getattr(app, "user", None):
            return

        banned, _ = is_banned(app.data, app.user["id"])
        if banned:
            self.manager.current = "banned"
            return

        u = app.user
        self.avatar_lbl.text = u.get("avatar", "1")
        clan = f"  [{u['clan']}]" if u.get("clan") else ""
        self.nick_lbl.text = f"{u.get('nick', 'Player')}{clan}\nID: {u['id']}"
        gold = u.get("gold", 0)
        self.gold_lbl.text = f"G {gold}" if gold > 0 else ""

        agents = [i for i in u.get("inventory", []) if str(i.get("name", "")).startswith("Agent")]
        if agents:
            self.agent_lbl.text = f"Agent\n{agents[-1]['name']}"
        else:
            self.agent_lbl.text = "Agent\nне выбран"

        is_admin = u["id"] == "0000"
        self.admin_btn.opacity = 1 if is_admin else 0
        self.admin_btn.disabled = not is_admin

class Cases(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="horizontal")
        make_bg(root)

        left = BoxLayout(orientation="vertical", size_hint_x=0.1, padding=dp(4), spacing=dp(5))
        make_bg(left, (0.11, 0.12, 0.16, 1))
        for icon, scr in [("H", "main"), ("C", "cases"), ("I", "inv"), ("M", "market"), ("S", "promo")]:
            b = Button(text=icon, font_size="16sp", background_normal="", background_color=(0.16, 0.17, 0.23, 1))
            b.bind(on_release=lambda inst, s=scr: setattr(self.manager, "current", s))
            left.add_widget(b)
        root.add_widget(left)

        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(6))
        content.add_widget(Label(text="КЕЙСЫ", font_size="20sp", bold=True, color=(1, 0.7, 0.15, 1), size_hint_y=0.1))
        scroll = ScrollView()
        self.grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, padding=dp(5))
        self.grid.bind(minimum_height=self.grid.setter("height"))
        scroll.add_widget(self.grid)
        content.add_widget(scroll)
        root.add_widget(content)
        self.add_widget(root)

    def on_enter(self, *a):
        self.grid.clear_widgets()
        for name, info in CASES.items():
            price = info["price"]
            col = (0.18, 0.4, 0.25, 1) if price == 100 else (0.45, 0.22, 0.15, 1)
            b = Btn(text=f"{name}\n{price}G", size_hint_y=None, height=dp(65), bg=col, font_size="13sp")
            b.bind(on_release=lambda inst, n=name: self.open_case(n))
            self.grid.add_widget(b)

    def open_case(self, name):
        app = App.get_running_app()
        u = app.user
        price = CASES[name]["price"]
        if u["gold"] < price:
            self.show_popup("Недостаточно голды!")
            return

        content = BoxLayout(orientation="vertical", padding=dp(15))
        anim_lbl = Label(text="Открываем кейс...", font_size="18sp", color=(1, 0.85, 0.3, 1))
        content.add_widget(anim_lbl)
        pop = Popup(title="", content=content, size_hint=(0.45, 0.35), auto_dismiss=False)
        pop.open()

        def step1(dt):
            anim_lbl.text = "Крутим..."
            anim_lbl.color = (0.4, 0.7, 1, 1)

        def step2(dt):
            anim_lbl.text = "Почти..."
            anim_lbl.color = (0.8, 0.4, 1, 1)

        def finish(dt):
            u["gold"] -= price
            skins = CASES[name]["skins"]
            rarity = random.choices(list(RARITY_WEIGHTS.keys()), weights=list(RARITY_WEIGHTS.values()), k=1)[0]
            if rarity not in skins:
                rarity = random.choice(list(skins.keys()))
            skin = random.choice(skins[rarity])
            u["inventory"].append({"name": skin, "rarity": rarity})
            u["stats"]["cases_opened"] += 1
            u["stats"]["total_drops"] += 1
            save_data(app.data)

            col = RARITY_COLORS.get(rarity, (1, 1, 1, 1))
            anim_lbl.text = f"{skin}\n[{rarity}]"
            anim_lbl.color = col

            def close(dt2):
                pop.dismiss()
                self.manager.get_screen("main").on_enter()
            Clock.schedule_once(close, 1.6)

        Clock.schedule_once(step1, 0.5)
        Clock.schedule_once(step2, 1.1)
        Clock.schedule_once(finish, 1.8)

    def show_popup(self, text):
        content = BoxLayout(orientation="vertical", padding=dp(12))
        content.add_widget(Label(text=text, font_size="15sp"))
        btn = Btn(text="OK", size_hint_y=0.4, bg=(0.3, 0.5, 0.3, 1))
        pop = Popup(title="", content=content, size_hint=(0.4, 0.3), auto_dismiss=True)
        btn.bind(on_release=pop.dismiss)
        content.add_widget(btn)
        pop.open()

class Agents(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(10))
        make_bg(root)
        root.add_widget(Label(text="АГЕНТЫ", font_size="20sp", bold=True, color=(1, 0.7, 0.15, 1), size_hint_y=0.12))
        self.info = Label(text="Цена: 300G", font_size="16sp", size_hint_y=0.2)
        root.add_widget(self.info)
        buy = Btn(text="КУПИТЬ АГЕНТА", size_hint_y=0.15, bg=(0.45, 0.2, 0.55, 1), font_size="15sp")
        buy.bind(on_release=self.buy)
        root.add_widget(buy)
        back = Btn(text="НАЗАД", size_hint_y=0.12, bg=(0.2, 0.2, 0.25, 1))
        back.bind(on_release=lambda x: setattr(self.manager, "current", "main"))
        root.add_widget(back)
        self.add_widget(root)

    def buy(self, *a):
        app = App.get_running_app()
        u = app.user
        if u["gold"] < 300:
            self.info.text = "Недостаточно голды"
            return
        u["gold"] -= 300
        agent = random.choice(AGENTS)
        u["inventory"].append({"name": "Agent " + agent, "rarity": "Arcane"})
        u["stats"]["total_drops"] += 1
        save_data(app.data)
        self.info.text = f"Получен: Agent {agent}"
        self.manager.get_screen("main").on_enter()

class Inv(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="horizontal")
        make_bg(root)

        left = BoxLayout(orientation="vertical", size_hint_x=0.1, padding=dp(4), spacing=dp(5))
        make_bg(left, (0.11, 0.12, 0.16, 1))
        for icon, scr in [("H", "main"), ("C", "cases"), ("I", "inv"), ("M", "market"), ("S", "promo")]:
            b = Button(text=icon, font_size="16sp", background_normal="", background_color=(0.16, 0.17, 0.23, 1))
            b.bind(on_release=lambda inst, s=scr: setattr(self.manager, "current", s))
            left.add_widget(b)
        root.add_widget(left)

        content = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(4))
        content.add_widget(Label(text="ИНВЕНТАРЬ", font_size="18sp", bold=True, color=(1, 0.7, 0.15, 1), size_hint_y=0.08))
        scroll = ScrollView()
        self.list_layout = GridLayout(cols=4, spacing=dp(6), size_hint_y=None, padding=dp(4))
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        scroll.add_widget(self.list_layout)
        content.add_widget(scroll)
        root.add_widget(content)
        self.add_widget(root)

    def on_enter(self, *a):
        self.list_layout.clear_widgets()
        inv = App.get_running_app().user.get("inventory", [])
        if not inv:
            self.list_layout.add_widget(Label(text="Пусто", size_hint_y=None, height=dp(40), color=(0.5, 0.5, 0.55, 1)))
            return

        for idx, item in enumerate(reversed(inv)):
            rarity = item.get("rarity", "Rare")
            col = RARITY_COLORS.get(rarity, (0.5, 0.5, 0.5, 1))
            real_idx = len(inv) - 1 - idx

            card = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(95), padding=dp(3))
            make_bg(card, (col[0]*0.2, col[1]*0.2, col[2]*0.2, 1))

            icon = Label(text="[]", font_size="22sp", color=col, size_hint_y=0.4)
            name = Label(text=item["name"][:16], font_size="10sp", color=(0.95, 0.95, 1, 1), size_hint_y=0.3, halign="center")
            name.bind(size=name.setter("text_size"))
            sell = Btn(text="Продать", size_hint_y=0.3, bg=(0.25, 0.45, 0.28, 1), font_size="10sp")
            sell.bind(on_release=lambda inst, i=real_idx: self.sell_item(i))

            card.add_widget(icon)
            card.add_widget(name)
            card.add_widget(sell)
            self.list_layout.add_widget(card)

    def sell_item(self, idx):
        app = App.get_running_app()
        inv = app.user["inventory"]
        if idx < 0 or idx >= len(inv):
            return
        item = inv[idx]

        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(6))
        content.add_widget(Label(text=f"Выставить:\n{item['name']}", font_size="13sp", halign="center"))
        price_input = TextInput(hint_text="Цена", input_filter="int", multiline=False, size_hint_y=0.3)
        content.add_widget(price_input)
        btns = BoxLayout(size_hint_y=0.3, spacing=dp(6))
        ok = Btn(text="Выставить", bg=(0.25, 0.55, 0.3, 1))
        cancel = Btn(text="Отмена", bg=(0.4, 0.2, 0.2, 1))
        btns.add_widget(ok)
        btns.add_widget(cancel)
        content.add_widget(btns)
        pop = Popup(title="Рынок", content=content, size_hint=(0.4, 0.45), auto_dismiss=False)

        def do_list(*a):
            try:
                price = int(price_input.text)
                if price < 1:
                    return
            except Exception:
                return
            listed = inv.pop(idx)
            market_price = get_market_price(listed.get("rarity", "Rare"))
            overpriced = price > market_price * 1.35
            entry = {
                "seller_id": app.user["id"],
                "item": listed,
                "price": price,
                "listed_at": time.time(),
                "market_value": market_price,
                "overpriced_until": time.time() + 600 if overpriced else 0
            }
            app.data.setdefault("market", []).append(entry)
            save_data(app.data)
            pop.dismiss()
            self.on_enter()
            self.manager.get_screen("main").on_enter()

        ok.bind(on_release=do_list)
        cancel.bind(on_release=pop.dismiss)
        pop.open()

class Market(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="horizontal")
        make_bg(root)

        left = BoxLayout(orientation="vertical", size_hint_x=0.1, padding=dp(4), spacing=dp(5))
        make_bg(left, (0.11, 0.12, 0.16, 1))
        for icon, scr in [("H", "main"), ("C", "cases"), ("I", "inv"), ("M", "market"), ("S", "promo")]:
            b = Button(text=icon, font_size="16sp", background_normal="", background_color=(0.16, 0.17, 0.23, 1))
            b.bind(on_release=lambda inst, s=scr: setattr(self.manager, "current", s))
            left.add_widget(b)
        root.add_widget(left)

        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(5))
        content.add_widget(Label(text="РЫНОК", font_size="18sp", bold=True, color=(1, 0.7, 0.15, 1), size_hint_y=0.08))
        scroll = ScrollView()
        self.list_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None, padding=dp(4))
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        scroll.add_widget(self.list_layout)
        content.add_widget(scroll)
        root.add_widget(content)
        self.add_widget(root)

    def on_enter(self, *a):
        self.refresh()

    def refresh(self):
        self.list_layout.clear_widgets()
        market = App.get_running_app().data.get("market", [])
        if not market:
            self.list_layout.add_widget(Label(text="Рынок пуст", size_hint_y=None, height=dp(40), color=(0.5, 0.5, 0.55, 1)))
            return
        now = time.time()
        for entry in reversed(market):
            item = entry["item"]
            col = RARITY_COLORS.get(item.get("rarity"), (1, 1, 1, 1))
            status = ""
            if entry.get("overpriced_until", 0) > now:
                left = int((entry["overpriced_until"] - now) / 60)
                status = f"  ({left}м)"
            text = f"{item['name']} [{item.get('rarity')}]  {entry['price']}G{status}"
            lbl = Label(text=text, font_size="12sp", color=col, size_hint_y=None, height=dp(38), halign="left", bold=True)
            lbl.bind(size=lbl.setter("text_size"))
            self.list_layout.add_widget(lbl)

class Click(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_click = 0.0
        self.click_times = []
        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(10))
        make_bg(root)
        root.add_widget(Label(text="КЛИКЕР", font_size="22sp", bold=True, color=(1, 0.75, 0.2, 1), size_hint_y=0.12))
        self.info = Label(text="1 клик = 1G\nАнтиавтокликер", font_size="15sp", size_hint_y=0.2, halign="center")
        self.info.bind(size=self.info.setter("text_size"))
        root.add_widget(self.info)
        btn = Btn(text="КЛИКАТЬ", size_hint_y=0.22, bg=(0.7, 0.5, 0.1, 1), font_size="20sp", bold=True)
        btn.bind(on_release=self.do_click)
        root.add_widget(btn)
        back = Btn(text="НАЗАД", size_hint_y=0.12, bg=(0.2, 0.2, 0.25, 1))
        back.bind(on_release=lambda x: setattr(self.manager, "current", "main"))
        root.add_widget(back)
        self.add_widget(root)

    def do_click(self, *a):
        now = time.time()
        if now - self.last_click < 0.13:
            self.info.text = "Слишком быстро!"
            return
        self.click_times = [t for t in self.click_times if now - t < 1.0]
        if len(self.click_times) >= 7:
            self.info.text = "Автокликер!\nПодожди"
            return
        self.last_click = now
        self.click_times.append(now)
        app = App.get_running_app()
        app.user["gold"] += 1
        app.user["stats"]["clicks"] += 1
        save_data(app.data)
        self.info.text = f"+1G\nКликов: {app.user['stats']['clicks']}"
        self.manager.get_screen("main").on_enter()

class Profile(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(8))
        make_bg(root)
        root.add_widget(Label(text="ПРОФИЛЬ", font_size="18sp", bold=True, color=(1, 0.7, 0.15, 1), size_hint_y=0.1))
        self.nick_input = TextInput(hint_text="Ник", multiline=False, size_hint_y=0.12, font_size="14sp")
        root.add_widget(self.nick_input)
        root.add_widget(Label(text="Аватар (1-9, A-C):", font_size="12sp", size_hint_y=0.06))
        avs = GridLayout(cols=6, spacing=dp(4), size_hint_y=0.2)
        self.selected = "1"
        for av in AVATARS:
            b = Button(text=av, font_size="16sp", background_normal="", background_color=(0.18, 0.18, 0.22, 1))
            b.bind(on_release=lambda inst, a=av: self.set_avatar(a))
            avs.add_widget(b)
        root.add_widget(avs)
        self.status = Label(text="", font_size="12sp", size_hint_y=0.08)
        root.add_widget(self.status)
        save = Btn(text="СОХРАНИТЬ", size_hint_y=0.12, bg=(0.2, 0.5, 0.3, 1))
        save.bind(on_release=self.save)
        root.add_widget(save)
        back = Btn(text="НАЗАД", size_hint_y=0.12, bg=(0.2, 0.2, 0.25, 1))
        back.bind(on_release=lambda x: setattr(self.manager, "current", "main"))
        root.add_widget(back)
        self.add_widget(root)

    def on_enter(self, *a):
        u = App.get_running_app().user
        self.nick_input.text = u.get("nick", "Player")
        self.selected = u.get("avatar", "1")

    def set_avatar(self, av):
        self.selected = av
        self.status.text = f"Выбран: {av}"

    def save(self, *a):
        app = App.get_running_app()
        nick = self.nick_input.text.strip()[:12]
        if nick:
            app.user["nick"] = nick
        app.user["avatar"] = self.selected
        save_data(app.data)
        self.status.text = "Сохранено!"
        self.manager.get_screen("main").on_enter()

class Stats(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(8))
        make_bg(root)
        root.add_widget(Label(text="СТАТИСТИКА", font_size="18sp", bold=True, color=(1, 0.7, 0.15, 1), size_hint_y=0.1))
        self.lbl = Label(text="", font_size="14sp", halign="left", valign="top")
        self.lbl.bind(size=self.lbl.setter("text_size"))
        root.add_widget(self.lbl)
        back = Btn(text="НАЗАД", size_hint_y=0.12, bg=(0.2, 0.2, 0.25, 1))
        back.bind(on_release=lambda x: setattr(self.manager, "current", "main"))
        root.add_widget(back)
        self.add_widget(root)

    def on_enter(self, *a):
        u = App.get_running_app().user
        s = u.get("stats", {})
        self.lbl.text = (
            f"ID: {u['id']}\nНик: {u.get('nick')}\nГолда: {u.get('gold', 0)}\n"
            f"Кейсов: {s.get('cases_opened', 0)}\nДропов: {s.get('total_drops', 0)}\n"
            f"Кликов: {s.get('clicks', 0)}\nВ инвентаре: {len(u.get('inventory', []))}\n"
            f"Клан: {u.get('clan') or 'нет'}"
        )

class Promo(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(8))
        make_bg(root)
        root.add_widget(Label(text="НАСТРОЙКИ / ПРОМО", font_size="17sp", bold=True, color=(1, 0.7, 0.15, 1), size_hint_y=0.1))
        self.inp = TextInput(hint_text="Промокод", multiline=False, size_hint_y=0.12, font_size="15sp")
        root.add_widget(self.inp)
        self.msg = Label(text="", font_size="14sp", size_hint_y=0.1)
        root.add_widget(self.msg)
        act = Btn(text="АКТИВИРОВАТЬ", size_hint_y=0.12, bg=(0.3, 0.5, 0.25, 1))
        act.bind(on_release=self.activate)
        root.add_widget(act)
        stats_btn = Btn(text="СТАТИСТИКА", size_hint_y=0.12, bg=(0.25, 0.35, 0.5, 1))
        stats_btn.bind(on_release=lambda x: setattr(self.manager, "current", "stats"))
        root.add_widget(stats_btn)
        prof_btn = Btn(text="ПРОФИЛЬ", size_hint_y=0.12, bg=(0.3, 0.3, 0.4, 1))
        prof_btn.bind(on_release=lambda x: setattr(self.manager, "current", "profile"))
        root.add_widget(prof_btn)
        back = Btn(text="НАЗАД", size_hint_y=0.12, bg=(0.2, 0.2, 0.25, 1))
        back.bind(on_release=lambda x: setattr(self.manager, "current", "main"))
        root.add_widget(back)
        self.add_widget(root)

    def activate(self, *a):
        app = App.get_running_app()
        code = self.inp.text.strip().upper()
        promos = app.data.get("promos", {})
        used = app.user.get("used_promos", [])
        if code in used:
            self.msg.text = "Уже использован"
            return
        if code in promos:
            gold = promos[code]
            app.user["gold"] += gold
            app.user.setdefault("used_promos", []).append(code)
            save_data(app.data)
            self.msg.text = f"+{gold}G!"
            self.manager.get_screen("main").on_enter()
        else:
            self.msg.text = "Неверный код"

class Clans(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(8))
        make_bg(root)
        root.add_widget(Label(text="КЛАНЫ", font_size="18sp", bold=True, color=(1, 0.7, 0.15, 1), size_hint_y=0.1))
        self.info = Label(text="", font_size="14sp", size_hint_y=0.15, halign="center")
        self.info.bind(size=self.info.setter("text_size"))
        root.add_widget(self.info)
        self.tag_input = TextInput(hint_text="Тег (до 4)", multiline=False, size_hint_y=0.12)
        self.name_input = TextInput(hint_text="Название (до 10)", multiline=False, size_hint_y=0.12)
        root.add_widget(self.tag_input)
        root.add_widget(self.name_input)
        create = Btn(text="СОЗДАТЬ (500G)", size_hint_y=0.13, bg=(0.35, 0.25, 0.5, 1))
        create.bind(on_release=self.create_clan)
        root.add_widget(create)
        back = Btn(text="НАЗАД", size_hint_y=0.12, bg=(0.2, 0.2, 0.25, 1))
        back.bind(on_release=lambda x: setattr(self.manager, "current", "main"))
        root.add_widget(back)
        self.add_widget(root)

    def on_enter(self, *a):
        u = App.get_running_app().user
        self.info.text = f"Клан: [{u['clan']}]" if u.get("clan") else "Нет клана\nСоздание = 500G"

    def create_clan(self, *a):
        app = App.get_running_app()
        u = app.user
        if u.get("clan"):
            self.info.text = "Уже есть клан"
            return
        if u["gold"] < 500:
            self.info.text = "Мало голды"
            return
        tag = self.tag_input.text.strip().upper()[:4]
        name = self.name_input.text.strip()[:10]
        if not tag or not name:
            self.info.text = "Заполни поля"
            return
        u["gold"] -= 500
        u["clan"] = tag
        app.data.setdefault("clans", {})[tag] = {"name": name, "owner": u["id"]}
        save_data(app.data)
        self.info.text = f"Клан [{tag}] создан!"
        self.manager.get_screen("main").on_enter()

class Admin(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(6))
        make_bg(root, (0.10, 0.05, 0.05, 1))
        root.add_widget(Label(text="АДМИНКА 0000", font_size="16sp", bold=True, color=(1, 0.4, 0.3, 1), size_hint_y=0.08))

        # Промо
        self.pcode = TextInput(hint_text="Новый промокод", multiline=False, size_hint_y=0.08)
        self.pgold = TextInput(hint_text="Сумма", multiline=False, input_filter="int", size_hint_y=0.08)
        root.add_widget(self.pcode)
        root.add_widget(self.pgold)
        add = Btn(text="СОЗДАТЬ ПРОМО", size_hint_y=0.09, bg=(0.5, 0.3, 0.1, 1))
        add.bind(on_release=self.add_promo)
        root.add_widget(add)

        # Выдача голды
        self.gid = TextInput(hint_text="ID игрока", multiline=False, size_hint_y=0.08)
        self.gamt = TextInput(hint_text="Сколько голды", multiline=False, input_filter="int", size_hint_y=0.08)
        root.add_widget(self.gid)
        root.add_widget(self.gamt)
        give = Btn(text="ВЫДАТЬ ГОЛДУ", size_hint_y=0.09, bg=(0.3, 0.5, 0.2, 1))
        give.bind(on_release=self.give_gold)
        root.add_widget(give)

        # Бан
        self.bid = TextInput(hint_text="ID для бана", multiline=False, size_hint_y=0.08)
        self.breason = TextInput(hint_text="Причина", multiline=False, size_hint_y=0.08)
        self.btime = TextInput(hint_text="Минуты или perm", multiline=False, size_hint_y=0.08)
        root.add_widget(self.bid)
        root.add_widget(self.breason)
        root.add_widget(self.btime)
        ban_btn = Btn(text="ЗАБАНИТЬ", size_hint_y=0.09, bg=(0.6, 0.15, 0.15, 1))
        ban_btn.bind(on_release=self.ban_user)
        root.add_widget(ban_btn)

        unban_btn = Btn(text="РАЗБАНИТЬ", size_hint_y=0.09, bg=(0.2, 0.45, 0.25, 1))
        unban_btn.bind(on_release=self.unban_user)
        root.add_widget(unban_btn)

        self.msg = Label(text="", font_size="12sp", size_hint_y=0.08)
        root.add_widget(self.msg)

        back = Btn(text="НАЗАД", size_hint_y=0.09, bg=(0.25, 0.2, 0.2, 1))
        back.bind(on_release=lambda x: setattr(self.manager, "current", "main"))
        root.add_widget(back)
        self.add_widget(root)

    def add_promo(self, *a):
        app = App.get_running_app()
        if app.user["id"] != "0000":
            return
        code = self.pcode.text.strip().upper()
        try:
            gold = int(self.pgold.text)
        except Exception:
            self.msg.text = "Неверная сумма"
            return
        if code:
            app.data.setdefault("promos", {})[code] = gold
            save_data(app.data)
            self.msg.text = f"{code} = {gold}G"

    def give_gold(self, *a):
        app = App.get_running_app()
        if app.user["id"] != "0000":
            return
        uid = self.gid.text.strip()
        try:
            amount = int(self.gamt.text)
        except Exception:
            self.msg.text = "Неверная сумма"
            return
        if uid in app.data["users"]:
            app.data["users"][uid]["gold"] += amount
            save_data(app.data)
            self.msg.text = f"+{amount}G -> {uid}"
        else:
            self.msg.text = "Игрок не найден"

    def ban_user(self, *a):
        app = App.get_running_app()
        if app.user["id"] != "0000":
            return
        uid = self.bid.text.strip()
        reason = self.breason.text.strip() or "без причины"
        t = self.btime.text.strip().lower()
        if not uid:
            self.msg.text = "Укажи ID"
            return
        if t == "perm":
            until = "perm"
        else:
            try:
                minutes = int(t)
                until = time.time() + minutes * 60
            except Exception:
                self.msg.text = "Время: число или perm"
                return
        app.data.setdefault("bans", {})[uid] = {"reason": reason, "until": until}
        save_data(app.data)
        self.msg.text = f"Забанен {uid}"

    def unban_user(self, *a):
        app = App.get_running_app()
        if app.user["id"] != "0000":
            return
        uid = self.bid.text.strip()
        if uid in app.data.get("bans", {}):
            del app.data["bans"][uid]
            save_data(app.data)
            self.msg.text = f"Разбанен {uid}"
        else:
            self.msg.text = "Бан не найден"

class StandoffApp(App):
    def build(self):
        Window.clearcolor = (0.07, 0.08, 0.11, 1)
        try:
            Window.orientation = "landscape"
        except Exception:
            pass
        self.user = None
        self.data = {}
        sm = ScreenManager(transition=FadeTransition(duration=0.15))
        sm.add_widget(Splash(name="splash"))
        sm.add_widget(Banned(name="banned"))
        sm.add_widget(Main(name="main"))
        sm.add_widget(Cases(name="cases"))
        sm.add_widget(Agents(name="agents"))
        sm.add_widget(Inv(name="inv"))
        sm.add_widget(Market(name="market"))
        sm.add_widget(Click(name="click"))
        sm.add_widget(Profile(name="profile"))
        sm.add_widget(Stats(name="stats"))
        sm.add_widget(Promo(name="promo"))
        sm.add_widget(Clans(name="clans"))
        sm.add_widget(Admin(name="admin"))
        return sm

    def check_market_bots(self, dt):
        if not hasattr(self, "data") or not self.data:
            return
        market = self.data.get("market", [])
        if not market:
            return
        now = time.time()
        to_remove = []
        for i, entry in enumerate(market):
            if entry.get("overpriced_until", 0) > now:
                continue
            if now - entry["listed_at"] < random.uniform(10, 15):
                continue
            seller_id = entry["seller_id"]
            price = entry["price"]
            if seller_id in self.data["users"]:
                self.data["users"][seller_id]["gold"] += price
            to_remove.append(i)
            if self.user and self.user["id"] == seller_id:
                self.user["gold"] += price
        for i in sorted(to_remove, reverse=True):
            market.pop(i)
        if to_remove:
            save_data(self.data)
            try:
                if self.root.current == "market":
                    self.root.get_screen("market").refresh()
                if self.root.current == "main":
                    self.root.get_screen("main").on_enter()
            except Exception:
                pass

if __name__ == "__main__":
    try:
        StandoffApp().run()
    except Exception as e:
        print("ОШИБКА:", e)
        import traceback
        traceback.print_exc()