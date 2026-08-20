# -*- coding: utf-8 -*-
# Hikka модуль: TeledoX Pro v4 (оптимизированный)
# Команды: .dox (номер), .doxm (домашний), .doxf (ФИО), .doxp (паспорт)
# Бот: @aybotrobot (ID: 7592728076)
# Автор: palofsc

from .. import loader, utils
import asyncio
import logging

logger = logging.getLogger(__name__)

@loader.tds
class TeledoXProV4Mod(loader.Module):
    """Мульти-запрос с управлением инлайн-кнопками (оптимизированный)"""
    
    strings = {
        "name": "TeledoXProV4",
        "no_args": "<b>[TeledoX]</b> Укажите аргумент: <code>{}</code>",
        "searching": "<b>[TeledoX]</b> Отправка запроса...",
        "no_response": "<b>[TeledoX]</b> Ответ не получен (тайм-аут).",
        "result": "<b>[TeledoX] Результат:</b>\n<blockquote>{}</blockquote>"
    }

    async def client_ready(self, client, db):
        self._client = client
        self._target_id = 7592728076
        self._target_username = "@aybotrobot"

    async def _setup_peer(self):
        """Мут и архив для бота (через высокоуровневые методы)"""
        try:
            entity = await self._client.get_entity(self._target_id)
            # Отключение уведомлений через высокоуровневый метод
            await self._client.edit_folder(entity, folder=1)
            await self._client.set_notify_settings(entity, silent=True, mute_until=2147483647)
            return True
        except Exception as e:
            logger.error(f"Setup error: {e}")
            return False

    async def _click_button(self, button_text, retries=3):
        """Нажатие на инлайн-кнопку через встроенный метод message.click()"""
        for _ in range(retries):
            await asyncio.sleep(1)
            async for msg in self._client.iter_messages(self._target_id, limit=3):
                if msg.sender_id == self._target_id and msg.reply_markup:
                    try:
                        # Высокоуровневый метод click() - работает во всех версиях Telethon
                        await msg.click(text=button_text)
                        await asyncio.sleep(1.5)
                        return True
                    except Exception as e:
                        logger.debug(f"Click error: {e}")
                        continue
        return False

    async def _send_and_get(self, query, menu_flow=None, wait=7.0):
        """Отправка запроса с навигацией по меню"""
        await self._setup_peer()
        
        # Старт бота
        await self._client.send_message(self._target_id, "/start")
        await asyncio.sleep(2.5)
        
        # Проход по меню через высокоуровневые методы
        if menu_flow:
            for btn_text in menu_flow:
                await self._click_button(btn_text)
                await asyncio.sleep(2.0)
        
        # Отправка запроса
        await self._client.send_message(self._target_id, query)
        await asyncio.sleep(wait)
        
        # Сбор ответов
        responses = []
        async for msg in self._client.iter_messages(self._target_id, limit=6):
            if msg.sender_id == self._target_id:
                text = msg.text or msg.raw_text
                if text and len(text) > 5:
                    responses.append(text)
        return responses if responses else None

    @loader.command()
    async def doxcmd(self, message):
        """<номер> — Поиск по номеру (база 2025)"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_args"].format(".dox +99312345678"))
            return
        query = args.strip()
        if not query.startswith("+") and query.isdigit():
            query = f"+{query}"
        await utils.answer(message, self.strings["searching"])
        resp = await self._send_and_get(query, menu_flow=["ПОИСК по номеру"])
        if resp:
            await utils.answer(message, self.strings["result"].format("\n\n".join(resp[-2:])))
        else:
            await utils.answer(message, self.strings["no_response"])

    @loader.command()
    async def doxmcmd(self, message):
        """<6 цифр> — Поиск по домашнему номеру"""
        args = utils.get_args_raw(message)
        if not args or not args.strip().isdigit() or len(args.strip()) != 6:
            await utils.answer(message, self.strings["no_args"].format(".doxm 123456"))
            return
        query = args.strip()
        await utils.answer(message, self.strings["searching"])
        resp = await self._send_and_get(query, menu_flow=["Поиск по Домашнему номеру Ашхабад"])
        if resp:
            await utils.answer(message, self.strings["result"].format("\n\n".join(resp[-2:])))
        else:
            await utils.answer(message, self.strings["no_response"])

    @loader.command()
    async def doxfcmd(self, message):
        """<ФИО> — Поиск по ФИО"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_args"].format(".doxf Иванов Иван"))
            return
        query = args.strip()
        await utils.answer(message, self.strings["searching"])
        resp = await self._send_and_get(query, menu_flow=["Поиск по ФИО"])
        if resp:
            await utils.answer(message, self.strings["result"].format("\n\n".join(resp[-2:])))
        else:
            await utils.answer(message, self.strings["no_response"])

    @loader.command()
    async def doxpcmd(self, message):
        """<паспорт> — Поиск по паспорту"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_args"].format(".doxp 654321 или DZ654321"))
            return
        query = args.strip().upper()
        await utils.answer(message, self.strings["searching"])
        resp = await self._send_and_get(query, menu_flow=["Поиск по паспорту"])
        if resp:
            await utils.answer(message, self.strings["result"].format("\n\n".join(resp[-2:])))
        else:
            await utils.answer(message, self.strings["no_response"])

    @loader.command()
    async def doxresetcmd(self, message):
        """Сбросить диалог с ботом"""
        await self._client.send_message(self._target_id, "/start")
        await utils.answer(message, "<b>[TeledoX]</b> Диалог сброшен.")
