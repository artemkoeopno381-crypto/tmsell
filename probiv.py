# -*- coding: utf-8 -*-
# Hikka модуль: TeledoX Pro v6 (с исправленным определением бота)
# Команды: .dox (номер), .doxm (домашний), .doxf (ФИО), .doxp (паспорт)
# Бот: @aybotrobot
# Автор: palofsc

from .. import loader, utils
import asyncio
import logging

logger = logging.getLogger(__name__)

@loader.tds
class TeledoXProV6Mod(loader.Module):
    """Мульти-запрос к боту с управлением инлайн-кнопками"""
    
    strings = {
        "name": "TeledoXProV6",
        "no_args": "<b>[TeledoX]</b> Укажите аргумент: <code>{}</code>",
        "searching": "<b>[TeledoX]</b> 🔍 Отправка запроса и навигация по меню...",
        "no_response": "<b>[TeledoX]</b> ⚠️ Ответ от бота не получен (тайм-аут).",
        "result": "<b>[TeledoX] 📊 Результат запроса:</b>\n<blockquote>{}</blockquote>",
        "reset_done": "<b>[TeledoX]</b> ✅ Диалог с ботом сброшен.",
        "bot_not_found": "<b>[TeledoX]</b> ❌ Бот @aybotrobot не найден. Убедитесь, что он существует и вы с ним взаимодействовали."
    }

    async def client_ready(self, client, db):
        self._client = client
        self._bot_username = "@aybotrobot"
        self._bot_entity = None
        self._click_delay = 1.8
        self._response_wait = 8.0

    async def _get_bot_entity(self):
        """Получение сущности бота с кешированием и обработкой ошибок"""
        if self._bot_entity:
            return self._bot_entity
        
        try:
            # Пытаемся получить сущность по username
            self._bot_entity = await self._client.get_entity(self._bot_username)
            return self._bot_entity
        except ValueError as e:
            logger.error(f"Bot entity not found: {e}")
            # Пытаемся получить через диалоги
            async for dialog in self._client.iter_dialogs():
                if dialog.entity and hasattr(dialog.entity, 'username'):
                    if dialog.entity.username and dialog.entity.username.lower() == "aybotrobot":
                        self._bot_entity = dialog.entity
                        return self._bot_entity
            return None

    async def _setup_peer(self):
        """Настройка диалога: архив и отключение уведомлений"""
        entity = await self._get_bot_entity()
        if not entity:
            return False
        
        try:
            await self._client.edit_folder(entity, folder=1)
            await self._client.set_notify_settings(entity, silent=True, mute_until=2147483647)
            return True
        except Exception as e:
            logger.error(f"Setup error: {e}")
            return False

    async def _click_button(self, button_text):
        """Нажатие на кнопку через высокоуровневый метод message.click()"""
        entity = await self._get_bot_entity()
        if not entity:
            return False
            
        try:
            async for msg in self._client.iter_messages(entity, limit=2):
                if msg.sender_id == entity.id and msg.reply_markup:
                    await msg.click(text=button_text)
                    await asyncio.sleep(self._click_delay)
                    return True
        except Exception as e:
            logger.debug(f"Click error: {e}")
        return False

    async def _navigate_menu(self, menu_flow):
        """Навигация по меню через последовательные клики"""
        if not menu_flow:
            return True
        for btn_text in menu_flow:
            success = await self._click_button(btn_text)
            if not success:
                await asyncio.sleep(1.0)
                success = await self._click_button(btn_text)
            if not success:
                return False
        return True

    async def _get_bot_response(self, query, menu_flow=None):
        """Основной метод: навигация, отправка запроса, получение ответа"""
        entity = await self._get_bot_entity()
        if not entity:
            return None
        
        await self._setup_peer()
        
        # Отправка /start для инициализации
        await self._client.send_message(entity, "/start")
        await asyncio.sleep(2.5)
        
        # Навигация по меню
        if menu_flow:
            await self._navigate_menu(menu_flow)
        
        # Отправка запроса
        await self._client.send_message(entity, query)
        await asyncio.sleep(self._response_wait)
        
        # Сбор ответов от бота
        responses = []
        async for msg in self._client.iter_messages(entity, limit=5):
            if msg.sender_id == entity.id:
                text = msg.text or msg.raw_text
                if text and len(text) > 3 and not text.startswith("/"):
                    responses.append(text.strip())
        
        return responses if responses else None

    @loader.command()
    async def doxcmd(self, message):
        """<номер> — Поиск по номеру телефона (база 2025)"""
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
            result_text = "\n\n".join(responses[-2:])
            await utils.answer(message, self.strings["result"].format(result_text))
        else:
            await utils.answer(message, self.strings["no_response"])

    @loader.command()
    async def doxmcmd(self, message):
        """<6 цифр> — Поиск по домашнему номеру Ашхабад"""
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
            result_text = "\n\n".join(responses[-2:])
            await utils.answer(message, self.strings["result"].format(result_text))
        else:
            await utils.answer(message, self.strings["no_response"])

    @loader.command()
    async def doxfcmd(self, message):
        """<ФИО> — Поиск по фамилии, имени, отчеству"""
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
            result_text = "\n\n".join(responses[-2:])
            await utils.answer(message, self.strings["result"].format(result_text))
        else:
            await utils.answer(message, self.strings["no_response"])

    @loader.command()
    async def doxpcmd(self, message):
        """<паспорт> — Поиск по паспортным данным"""
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
            result_text = "\n\n".join(responses[-2:])
            await utils.answer(message, self.strings["result"].format(result_text))
        else:
            await utils.answer(message, self.strings["no_response"])

    @loader.command()
    async def doxresetcmd(self, message):
        """Сброс диалога с ботом (/start)"""
        entity = await self._get_bot_entity()
        if not entity:
            await utils.answer(message, self.strings["bot_not_found"])
            return
            
        await self._client.send_message(entity, "/start")
        await utils.answer(message, self.strings["reset_done"])
