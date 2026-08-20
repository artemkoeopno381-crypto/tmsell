# -*- coding: utf-8 -*-
# Hikka модуль: TeledoX Pro v11 (с прямыми callback-данными)
# Команды: .dox, .doxm, .doxf, .doxp
# Бот: @aybotrobot

from .. import loader, utils
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
import asyncio
import logging

logger = logging.getLogger(__name__)

@loader.tds
class TeledoXProV11Mod(loader.Module):
    strings = {
        "name": "TeledoXProV11",
        "no_args": "<b>[TeledoX]</b> Укажите аргумент: <code>{}</code>",
        "searching": "<b>[TeledoX]</b> 🔍 Навигация...",
        "no_response": "<b>[TeledoX]</b> ⚠️ Нет ответа.",
        "result": "<b>[TeledoX] 📊 Результат:</b>\n<blockquote>{}</blockquote>",
        "reset_done": "<b>[TeledoX]</b> ✅ Сброшено.",
        "bot_not_found": "<b>[TeledoX]</b> ❌ Бот не найден."
    }

    async def client_ready(self, client, db):
        self._client = client
        self._bot_username = "@aybotrobot"
        self._bot_entity = None
        
        # Точные тексты кнопок (как в интерфейсе)
        self._buttons = {
            "start": ["🔍НАЧАТЬ ПОИСК", "НАЧАТЬ ПОИСК", "Начать поиск"],
            "phone": ["🔍ПОИСК по номеру (2025 НОВАЯ)", "ПОИСК по номеру"],
            "fio": ["👥Поиск по ФИО", "Поиск по ФИО"],
            "passport": ["🪪 Поиск по паспорту", "Поиск по паспорту"],
            "home": ["🔍Поиск по Домашнему номеру Ашхабад", "Поиск по Домашнему номеру Ашхабад"]
        }

    async def _get_bot(self):
        if self._bot_entity:
            return self._bot_entity
        try:
            self._bot_entity = await self._client.get_entity(self._bot_username)
            return self._bot_entity
        except:
            async for d in self._client.iter_dialogs():
                if d.entity and getattr(d.entity, 'username', '').lower() == "aybotrobot":
                    self._bot_entity = d.entity
                    return self._bot_entity
            return None

    async def _click_callback(self, button_texts, timeout=4):
        """Клик по кнопке с точным совпадением текста"""
        bot = await self._get_bot()
        if not bot:
            return False
        
        if isinstance(button_texts, str):
            button_texts = [button_texts]
        
        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < timeout:
            try:
                async for msg in self._client.iter_messages(bot, limit=3):
                    if msg.sender_id == bot.id and msg.reply_markup:
                        for row in msg.reply_markup.rows:
                            for btn in row.buttons:
                                for target in button_texts:
                                    if btn.text == target:
                                        await self._client(GetBotCallbackAnswerRequest(
                                            peer=bot,
                                            msg_id=msg.id,
                                            data=btn.data
                                        ))
                                        await asyncio.sleep(1.5)
                                        return True
            except:
                pass
            await asyncio.sleep(0.5)
        return False

    async def _navigate(self, search_type):
        """Навигация: /start -> start -> выбор типа"""
        bot = await self._get_bot()
        if not bot:
            return False
        
        await self._client.send_message(bot, "/start")
        await asyncio.sleep(2.5)
        
        # Клик по кнопке начала поиска
        if not await self._click_callback(self._buttons["start"]):
            return False
        await asyncio.sleep(2.0)
        
        # Клик по типу поиска
        if search_type:
            if not await self._click_callback(self._buttons[search_type]):
                return False
            await asyncio.sleep(1.5)
        return True

    async def _get_result(self, query, search_type):
        bot = await self._get_bot()
        if not bot:
            return None
        
        if not await self._navigate(search_type):
            return None
        
        await self._client.send_message(bot, query)
        await asyncio.sleep(10.0)
        
        resp = []
        async for msg in self._client.iter_messages(bot, limit=6):
            if msg.sender_id == bot.id:
                text = msg.text or msg.raw_text
                if text and len(text) > 5:
                    resp.append(text.strip())
        return resp if resp else None

    @loader.command()
    async def doxcmd(self, m):
        args = utils.get_args_raw(m)
        if not args:
            await utils.answer(m, self.strings["no_args"].format(".dox +99312345678"))
            return
        q = args.strip()
        if not q.startswith("+") and q.isdigit():
            q = f"+{q}"
        await utils.answer(m, self.strings["searching"])
        r = await self._get_result(q, "phone")
        if r:
            await utils.answer(m, self.strings["result"].format("\n\n".join(r[-2:])))
        else:
            await utils.answer(m, self.strings["no_response"])

    @loader.command()
    async def doxmcmd(self, m):
        args = utils.get_args_raw(m)
        if not args or not args.strip().isdigit() or len(args.strip()) != 6:
            await utils.answer(m, self.strings["no_args"].format(".doxm 123456"))
            return
        await utils.answer(m, self.strings["searching"])
        r = await self._get_result(args.strip(), "home")
        if r:
            await utils.answer(m, self.strings["result"].format("\n\n".join(r[-2:])))
        else:
            await utils.answer(m, self.strings["no_response"])

    @loader.command()
    async def doxfcmd(self, m):
        args = utils.get_args_raw(m)
        if not args:
            await utils.answer(m, self.strings["no_args"].format(".doxf Иванов Иван"))
            return
        await utils.answer(m, self.strings["searching"])
        r = await self._get_result(args.strip(), "fio")
        if r:
            await utils.answer(m, self.strings["result"].format("\n\n".join(r[-2:])))
        else:
            await utils.answer(m, self.strings["no_response"])

    @loader.command()
    async def doxpcmd(self, m):
        args = utils.get_args_raw(m)
        if not args:
            await utils.answer(m, self.strings["no_args"].format(".doxp 654321"))
            return
        await utils.answer(m, self.strings["searching"])
        r = await self._get_result(args.strip().upper(), "passport")
        if r:
            await utils.answer(m, self.strings["result"].format("\n\n".join(r[-2:])))
        else:
            await utils.answer(m, self.strings["no_response"])

    @loader.command()
    async def doxresetcmd(self, m):
        bot = await self._get_bot()
        if not bot:
            await utils.answer(m, self.strings["bot_not_found"])
            return
        await self._client.send_message(bot, "/start")
        await utils.answer(m, self.strings["reset_done"])
