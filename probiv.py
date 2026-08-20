# -*- coding: utf-8 -*-
# Hikka модуль: TeledoX Pro v3 (исправленный)
# Команды: .dox (номер), .doxm (домашний), .doxf (ФИО), .doxp (паспорт)
# Бот: @aybotrobot (ID: 7592728076)
# Автор: palofsc

from .. import loader, utils
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from telethon.tl.functions.folders import EditPeerFolders
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from telethon.tl.types import InputPeerNotifySettings, InputNotifyPeer, InputFolderPeer
from telethon.tl.types import KeyboardButtonCallback
import asyncio
import logging

logger = logging.getLogger(__name__)

@loader.tds
class TeledoXProV3Mod(loader.Module):
    """Мульти-запрос с управлением инлайн-кнопками (исправленный)"""
    
    strings = {
        "name": "TeledoXProV3",
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
        """Мут и архив для бота"""
        try:
            entity = await self._client.get_entity(self._target_id)
            await self._client(UpdateNotifySettingsRequest(
                peer=InputNotifyPeer(entity),
                settings=InputPeerNotifySettings(
                    show_previews=False,
                    silent=True,
                    mute_until=2147483647
                )
            ))
            await self._client(EditPeerFolders(
                folder_peers=[InputFolderPeer(peer=entity, folder_id=1)]
            ))
            return True
        except Exception as e:
            logger.error(f"Setup error: {e}")
            return False

    async def _click_button(self, button_text, retries=3):
        """Поиск и нажатие инлайн-кнопки через GetBotCallbackAnswerRequest"""
        for _ in range(retries):
            await asyncio.sleep(1)
            async for msg in self._client.iter_messages(self._target_id, limit=2):
                if msg.sender_id == self._target_id and msg.reply_markup:
                    markup = msg.reply_markup
                    if hasattr(markup, 'rows'):
                        for row in markup.rows:
                            for btn in row.buttons:
                                if isinstance(btn, KeyboardButtonCallback):
                                    if button_text.lower() in btn.text.lower():
                                        # Правильный вызов callback-запроса
                                        await self._client(GetBotCallbackAnswerRequest(
                                            peer=msg.peer_id,
                                            msg_id=msg.id,
                                            data=btn.data
                                        ))
                                        await asyncio.sleep(1.5)
                                        return True
        return False

    async def _send_and_get(self, query, menu_flow=None, wait=6.0):
        """Отправка запроса с навигацией по меню"""
        await self._setup_peer()
        
        # Старт бота
        await self._client.send_message(self._target_id, "/start")
        await asyncio.sleep(2)
        
        # Проход по меню
        if menu_flow:
            for btn_text in menu_flow:
                await self._click_button(btn_text)
                await asyncio.sleep(1.5)
        
        # Отправка запроса
        await self._client.send_message(self._target_id, query)
        await asyncio.sleep(wait)
        
        # Сбор ответов
        responses = []
        async for msg in self._client.iter_messages(self._target_id, limit=5):
            if msg.sender_id == self._target_id:
                text = msg.text or msg.raw_text
                if text and len(text) > 3:
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
