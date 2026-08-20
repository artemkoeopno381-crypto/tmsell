# -*- coding: utf-8 -*-
# Coded by @aaaiaooaaooa
# Channel: https://t.me/hikka_and_heroku

from .. import loader, utils
import asyncio

class TeledoXCleanMod(loader.Module):
    """Мульти-запрос к боту"""
    
    strings = {
        "name": "TeledoXPro",
        "no_args": "<b>[TeledoX]</b> Укажите аргумент: <code>{}</code>",
        "searching": "<b>[TeledoX]</b> Отправка запроса...",
        "no_response": "<b>[TeledoX]</b> Ответ не получен (тайм-аут).",
        "result": "<b>[TeledoX] Результат:</b>\n<blockquote>{}</blockquote>"
    }

    async def client_ready(self, client, db):
        self._client = client
        self._target_id = 7592728076

    async def _send_and_get(self, query, wait=4.0):
        try:
            await self._client.send_message(self._target_id, query)
        except Exception:
            try:
                await self._client.send_message(self._target_id, "/start")
                await asyncio.sleep(1.5)
                await self._client.send_message(self._target_id, query)
            except Exception:
                return None
        
        await asyncio.sleep(wait)
        async for msg in self._client.iter_messages(self._target_id, limit=3):
            if msg.sender_id == self._target_id:
                text = msg.text or msg.raw_text
                if text:
                    return text
        return None

    @loader.command()
    async def doxcmd(self, message):
        """<номер телефона> — Поиск по мобильному номеру"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_args"].format(".dox +99312345678"))
            return
        query = args.strip()
        if not query.startswith("+") and query.isdigit():
            query = f"+{query}"
        await utils.answer(message, self.strings["searching"])
        resp = await self._send_and_get(query)
        if resp:
            await utils.answer(message, self.strings["result"].format(resp))
        else:
            await utils.answer(message, self.strings["no_response"])

    @loader.command()
    async def doxmcmd(self, message):
        """<6-значный номер> — Поиск по домашнему номеру"""
        args = utils.get_args_raw(message)
        if not args or not args.strip().isdigit() or len(args.strip()) != 6:
            await utils.answer(message, self.strings["no_args"].format(".doxm 123456"))
            return
        query = args.strip()
        await utils.answer(message, self.strings["searching"])
        resp = await self._send_and_get(query)
        if resp:
            await utils.answer(message, self.strings["result"].format(resp))
        else:
            await utils.answer(message, self.strings["no_response"])

    @loader.command()
    async def doxfcmd(self, message):
        """<ФИО> — Поиск по фамилии/имени"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_args"].format(".doxf Иванов Иван"))
            return
        query = args.strip()
        await utils.answer(message, self.strings["searching"])
        resp = await self._send_and_get(query)
        if resp:
            await utils.answer(message, self.strings["result"].format(resp))
        else:
            await utils.answer(message, self.strings["no_response"])

    @loader.command()
    async def doxpcmd(self, message):
        """<серия/номер> — Поиск по паспорту"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_args"].format(".doxp 654321"))
            return
        query = args.strip()
        await utils.answer(message, self.strings["searching"])
        resp = await self._send_and_get(query)
        if resp:
            await utils.answer(message, self.strings["result"].format(resp))
        else:
            await utils.answer(message, self.strings["no_response"])
            
