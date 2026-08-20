#      _ _ _ _  _ _  _ ____    ____ _  _ ___    _  _ ____ ____ ____ _  _ _  _ 
#      |__| | |_/  |_/  |__|    |__| |\ | |  \   |__| |___ |__/ |  | |_/  |  | 
#      |  | | | \  | \  |  |    |  | | \| |__/   |  | |___ |  \ |__| | \  |__| 
#
#             Created by @aaaiaooaaooa // Channel: @hikka_and_heroku

from .. import loader, utils
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from telethon.tl.functions.folders import EditPeerFolders
from telethon.tl.types import InputPeerNotifySettings, InputNotifyPeer, InputFolderPeer
import asyncio
import logging

logger = logging.getLogger(__name__)

@loader.tds
class TeledoXProMod(loader.Module):
    """Мульти-запрос к боту aybotrobot"""
    
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

    async def _send_and_get(self, query, wait=4.0):
        """Отправка запроса и получение ответа"""
        await self._setup_peer()
        try:
            await self._client.send_message(self._target_id, query)
        except Exception as e:
            logger.warning(f"First send failed, trying start: {e}")
            try:
                await self._client.send_message(self._target_id, "/start")
                await asyncio.sleep(1.5)
                await self._client.send_message(self._target_id, query)
            except Exception as start_err:
                logger.error(f"Failed to send query: {start_err}")
                return None
        
        await asyncio.sleep(wait)
        async for msg in self._client.iter_messages(self._target_id, limit=4):
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
        
