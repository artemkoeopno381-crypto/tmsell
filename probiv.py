# -*- coding: utf-8 -*-
# Hikka модуль: TeledoX Pro v8 (с улучшенным обнаружением кнопок)
# Команды: .dox (номер), .doxm (домашний), .doxf (ФИО), .doxp (паспорт)
# Бот: @aybotrobot
# Автор: palofsc

from .. import loader, utils
import asyncio
import logging

logger = logging.getLogger(__name__)

@loader.tds
class TeledoXProV8Mod(loader.Module):
    """Мульти-запрос к боту с управлением инлайн-кнопками"""
    
    strings = {
        "name": "TeledoXProV8",
        "no_args": "<b>[TeledoX]</b> Укажите аргумент: <code>{}</code>",
        "searching": "<b>[TeledoX]</b> 🔍 Отправка запроса и навигация по меню...",
        "no_response": "<b>[TeledoX]</b> ⚠️ Ответ от бота не получен (тайм-аут).",
        "result": "<b>[TeledoX] 📊 Результат запроса:</b>\n<blockquote>{}</blockquote>",
        "reset_done": "<b>[TeledoX]</b> ✅ Диалог с ботом сброшен.",
        "bot_not_found": "<b>[TeledoX]</b> ❌ Бот @aybotrobot не найден."
    }

    async def client_ready(self, client, db):
        self._client = client
        self._bot_username = "@aybotrobot"
        self._bot_entity = None
        self._click_delay = 2.0
        self._response_wait = 10.0

    async def _get_bot_entity(self):
        if self._bot_entity:
            return self._bot_entity
        try:
            self._bot_entity = await self._client.get_entity(self._bot_username)
            return self._bot_entity
        except ValueError:
            async for dialog in self._client.iter_dialogs():
                if dialog.entity and hasattr(dialog.entity, 'username'):
                    if dialog.entity.username and dialog.entity.username.lower() == "aybotrobot":
                        self._bot_entity = dialog.entity
                        return self._bot_entity
            return None

    async def _setup_peer(self):
        entity = await self._get_bot_entity()
        if not entity:
            return False
        try:
            await self._client.edit_folder(entity, folder=1)
            await self._client.set_notify_settings(entity, silent=True, mute_until=2147483647)
            return True
        except Exception:
            return False

    async def _click_button(self, button_text, retry=3):
        """Нажатие на кнопку с множественными попытками и альтернативными текстами"""
        entity = await self._get_bot_entity()
        if not entity:
            return False
        
        # Варианты текста кнопки (с учетом разных регистров и раскладок)
        variants = [
            button_text,
            button_text.upper(),
            button_text.lower(),
            button_text.capitalize(),
            button_text.replace(" ", ""),
            button_text.replace(" ", " ").upper()
        ]
        # Уникальные варианты
        variants = list(set(variants))
        
        for attempt in range(retry):
            try:
                async for msg in self._client.iter_messages(entity, limit=4):
                    if msg.sender_id == entity.id and msg.reply_markup:
                        # Проверка всех вариантов текста
                        for variant in variants:
                            try:
                                await msg.click(text=variant)
                                await asyncio.sleep(self._click_delay)
                                return True
                            except Exception:
                                continue
            except Exception as e:
                logger.debug(f"Click attempt {attempt+1} failed: {e}")
                await asyncio.sleep(1.5)
        return False

    async def _navigate_menu(self, menu_flow):
        """Навигация с обязательным нажатием НАЧАТЬ ПОИСК"""
        # Шаг 1: Нажать кнопку начала поиска
        start_buttons = [
            "НАЧАТЬ ПОИСК",
            "Начать поиск",
            "GÖZLEME BAŞLA",
            "Поиск",
            "START"
        ]
        start_pressed = False
        for btn in start_buttons:
            if await self._click_button(btn):
                start_pressed = True
                break
            await asyncio.sleep(0.5)
        
        if not start_pressed:
            # Если не нашли кнопку, пробуем отправить "Начать поиск" текстом
            entity = await self._get_bot_entity()
            if entity:
                await self._client.send_message(entity, "Начать поиск")
                await asyncio.sleep(2.0)
        
        await asyncio.sleep(2.0)
        
        # Шаг 2: Выбор типа поиска
        if menu_flow:
            for btn_text in menu_flow:
                success = await self._click_button(btn_text)
                if not success:
                    # Пробуем отправить текст как сообщение
                    entity = await self._get_bot_entity()
                    if entity:
                        await self._client.send_message(entity, btn_text)
                        await asyncio.sleep(2.0)
        return True

    async def _get_bot_response(self, query, menu_flow=None):
        """Получение ответа с полной навигацией"""
        entity = await self._get_bot_entity()
        if not entity:
            return None
        
        await self._setup_peer()
        
        # Отправка /start для инициализации
        await self._client.send_message(entity, "/start")
        await asyncio.sleep(3.0)
        
        # Полная навигация
        await self._navigate_menu(menu_flow)
        
        # Отправка запроса
        await self._client.send_message(entity, query)
        await asyncio.sleep(self._response_wait)
        
        # Сбор ответов
        responses = []
        async for msg in self._client.iter_messages(entity, limit=8):
            if msg.sender_id == entity.id:
                text = msg.text or msg.raw_text
                if text and len(text) > 5 and not text.startswith("/"):
                    # Проверка на наличие результата (не должно быть сообщений об ошибке)
                    if "не найден" not in text.lower() and "ошибка" not in text.lower():
                        responses.append(text.strip())
        
        # Если ответов нет, берем последнее сообщение даже если оно короткое
        if not responses:
            async for msg in self._client.iter_messages(entity, limit=3):
                if msg.sender_id == entity.id:
                    text = msg.text or msg.raw_text
                    if text and len(text) > 3:
                        responses.append(text.strip())
                        break
        
        return responses if responses else None

    @loader.command()
    async def doxcmd(self, message):
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_args"].format(".dox +99312345678"))
            return
        entity = await self._get_bot_entity()
        if not entity:
            await utils.answer(message, self.strings["bot_not_found"])
            return
        query = args.strip()
        if not query.startswith("+") and query.isdigit():
            query = f"+{query}"
        await utils.answer(message, self.strings["searching"])
        responses = await self._get_bot_response(query, menu_flow=["ПОИСК по номеру"])
        if responses:
            result_text = "\n\n".join(responses[-3:])
            await utils.answer(message, self.strings["result"].format(result_text))
        else:
            await utils.answer(message, self.strings["no_response"])

    @loader.command()
    async def doxmcmd(self, message):
        args = utils.get_args_raw(message)
        if not args or not args.strip().isdigit() or len(args.strip()) != 6:
            await utils.answer(message, self.strings["no_args"].format(".doxm 123456"))
            return
        entity = await self._get_bot_entity()
        if not entity:
            await utils.answer(message, self.strings["bot_not_found"])
            return
        query = args.strip()
        await utils.answer(message, self.strings["searching"])
        responses = await self._get_bot_response(query, menu_flow=["Поиск по Домашнему номеру Ашхабад"])
        if responses:
            result_text = "\n\n".join(responses[-3:])
            await utils.answer(message, self.strings["result"].format(result_text))
        else:
            await utils.answer(message, self.strings["no_response"])

    @loader.command()
    async def doxfcmd(self, message):
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_args"].format(".doxf Иванов Иван"))
            return
        entity = await self._get_bot_entity()
        if not entity:
            await utils.answer(message, self.strings["bot_not_found"])
            return
        query = args.strip()
        await utils.answer(message, self.strings["searching"])
        responses = await self._get_bot_response(query, menu_flow=["Поиск по ФИО"])
        if responses:
            result_text = "\n\n".join(responses[-3:])
            await utils.answer(message, self.strings["result"].format(result_text))
        else:
            await utils.answer(message, self.strings["no_response"])

    @loader.command()
    async def doxpcmd(self, message):
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_args"].format(".doxp 654321 или DZ654321"))
            return
        entity = await self._get_bot_entity()
        if not entity:
            await utils.answer(message, self.strings["bot_not_found"])
            return
        query = args.strip().upper()
        await utils.answer(message, self.strings["searching"])
        responses = await self._get_bot_response(query, menu_flow=["Поиск по паспорту"])
        if responses:
            result_text = "\n\n".join(responses[-3:])
            await utils.answer(message, self.strings["result"].format(result_text))
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
