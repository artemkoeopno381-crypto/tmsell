# -*- coding: utf-8 -*-
# Hikka модуль: TeledoX Pro v9 (чистый клик по инлайн-кнопкам)
# Команды: .dox (номер), .doxm (домашний), .doxf (ФИО), .doxp (паспорт)
# Бот: @aybotrobot
# Автор: palofsc

from .. import loader, utils
import asyncio
import logging

logger = logging.getLogger(__name__)

@loader.tds
class TeledoXProV9Mod(loader.Module):
    """Мульти-запрос с кликами по инлайн-кнопкам"""
    
    strings = {
        "name": "TeledoXProV9",
        "no_args": "<b>[TeledoX]</b> Укажите аргумент: <code>{}</code>",
        "searching": "<b>[TeledoX]</b> 🔍 Навигация по меню...",
        "no_response": "<b>[TeledoX]</b> ⚠️ Ответ не получен.",
        "result": "<b>[TeledoX] 📊 Результат:</b>\n<blockquote>{}</blockquote>",
        "reset_done": "<b>[TeledoX]</b> ✅ Диалог сброшен.",
        "bot_not_found": "<b>[TeledoX]</b> ❌ Бот не найден."
    }

    async def client_ready(self, client, db):
        self._client = client
        self._bot_username = "@aybotrobot"
        self._bot_entity = None

    async def _get_bot_entity(self):
        if self._bot_entity:
            return self._bot_entity
        try:
            self._bot_entity = await self._client.get_entity(self._bot_username)
            return self._bot_entity
        except:
            async for dialog in self._client.iter_dialogs():
                if dialog.entity and hasattr(dialog.entity, 'username'):
                    if dialog.entity.username and dialog.entity.username.lower() == "aybotrobot":
                        self._bot_entity = dialog.entity
                        return self._bot_entity
            return None

    async def _click_inline_button(self, button_text, timeout=5):
        """Клик по инлайн-кнопке через message.click()"""
        entity = await self._get_bot_entity()
        if not entity:
            return False
        
        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < timeout:
            try:
                async for msg in self._client.iter_messages(entity, limit=3):
                    if msg.sender_id == entity.id and msg.reply_markup:
                        try:
                            await msg.click(text=button_text)
                            await asyncio.sleep(1.5)
                            return True
                        except Exception:
                            continue
            except:
                pass
            await asyncio.sleep(0.5)
        return False

    async def _full_navigation(self, search_type):
        """Полная навигация: /start -> НАЧАТЬ ПОИСК -> выбор типа"""
        entity = await self._get_bot_entity()
        if not entity:
            return False
        
        # 1. /start
        await self._client.send_message(entity, "/start")
        await asyncio.sleep(2.5)
        
        # 2. Клик по "НАЧАТЬ ПОИСК"
        start_buttons = ["НАЧАТЬ ПОИСК", "Начать поиск", "GÖZLEME BAŞLA"]
        clicked = False
        for btn in start_buttons:
            if await self._click_inline_button(btn, timeout=3):
                clicked = True
                break
        if not clicked:
            return False
        await asyncio.sleep(2.0)
        
        # 3. Клик по типу поиска
        if search_type:
            await self._click_inline_button(search_type, timeout=3)
            await asyncio.sleep(1.5)
        
        return True

    async def _get_response(self, query, search_type):
        """Отправка запроса и получение ответа"""
        entity = await self._get_bot_entity()
        if not entity:
            return None
        
        # Навигация
        if not await self._full_navigation(search_type):
            return None
        
        # Отправка запроса
        await self._client.send_message(entity, query)
        await asyncio.sleep(8.0)
        
        # Сбор ответов
        responses = []
        async for msg in self._client.iter_messages(entity, limit=5):
            if msg.sender_id == entity.id:
                text = msg.text or msg.raw_text
                if text and len(text) > 5:
                    responses.append(text.strip())
        return responses if responses else None

    @loader.command()
    async def doxcmd(self, message):
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_args"].format(".dox +99312345678"))
            return
        query = args.strip()
        if not query.startswith("+") and query.isdigit():
            query = f"+{query}"
        await utils.answer(message, self.strings["searching"])
        resp = await self._get_response(query, "ПОИСК по номеру")
        if resp:
            await utils.answer(message, self.strings["result"].format("\n\n".join(resp[-2:])))
        else:
            await utils.answer(message, self.strings["no_response"])

    @loader.command()
    async def doxmcmd(self, message):
        args = utils.get_args_raw(message)
        if not args or not args.strip().isdigit() or len(args.strip()) != 6:
            await utils.answer(message, self.strings["no_args"].format(".doxm 123456"))
            return
        query = args.strip()
        await utils.answer(message, self.strings["searching"])
        resp = await self._get_response(query, "Поиск по Домашнему номеру Ашхабад")
        if resp:
            await utils.answer(message, self.strings["result"].format("\n\n".join(resp[-2:])))
        else:
            await utils.answer(message, self.strings["no_response"])

    @loader.command()
    async def doxfcmd(self, message):
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_args"].format(".doxf Иванов Иван"))
            return
        query = args.strip()
        await utils.answer(message, self.strings["searching"])
        resp = await self._get_response(query, "Поиск по ФИО")
        if resp:
            await utils.answer(message, self.strings["result"].format("\n\n".join(resp[-2:])))
        else:
            await utils.answer(message, self.strings["no_response"])

    @loader.command()
    async def doxpcmd(self, message):
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_args"].format(".doxp 654321 или DZ654321"))
            return
        query = args.strip().upper()
        await utils.answer(message, self.strings["searching"])
        resp = await self._get_response(query, "Поиск по паспорту")
        if resp:
            await utils.answer(message, self.strings["result"].format("\n\n".join(resp[-2:])))
        else:
            await utils.answer(message, self.strings["no_response"])

    @loader.command()
    async def doxresetcmd(self, message):
        entity = await self._get_bot_entity()
        if not entity:
            await utils.answer(message, self.strings["bot_not_found"])
            return
        await self._client.send_message(entity, "/start")
        await utils.answer(message, self.strings["reset_done"])
