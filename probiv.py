#     _  _ _ _  _ _  _ ____    _*___ _  _ ___    _  _ _*___ ____ _**___ _  _ _  _ 
#     |__| | |_/  |_/  |__|    |__| |\ | |  \   |__| |___ |__/ |  | |_/  |  | 
#     |  | | | \  | \  |  |    |  | | \| |__/   |  | |___ |  \ |__| | \  |__| 
#
# Coded by @aaaiaooaaooa
# Channel: https://t.me/hikka_and_heroku

from .. import loader, utils
import asyncio

@loader.tds
class TeledoXMod(loader.Module):
    """Шота там по пробиву чета там"""
    strings = {
        "name": "TeledoX",
        "no_args": "<b>[TeledoX]</b> Слышь, номер то введи: <code>.dox +993...</code>",
        "wait": "<b>[TeledoX]</b> Запрос улетел, ждемс...",
        "no_ans": "<b>[TeledoX]</b> Бот проигнорил или сдох."
    }

    async def client_ready(self, client, db):
        self.client = client
        self.target = 7754279809

    @loader.command()
    async def doxcmd(self, message):
        """быстрый чек номера"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_args"])
            return

        num = args.strip()
        if not num.startswith("+"):
            num = f"+{num}"

        await utils.answer(message, self.strings["wait"])
        
        # отправка
        await self.client.send_message(self.target, num)
        await asyncio.sleep(2.5) # тайминг с запасом

        # ловим ответ
        async for msg in self.client.iter_messages(self.target, limit=3):
            if msg.sender_id == self.target:
                res = msg.text or msg.raw_text
                if res:
                    out = f"<b>[TeledoX] Результат для {num}:</b>\n\n{res}"
                    await utils.answer(message, out)
                    return

        await utils.answer(message, self.strings["no_ans"])
