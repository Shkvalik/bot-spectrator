import asyncio
from datetime import datetime
import random
import string
import httpx
from aiogram import Bot
from aiogram.utils.markdown import hlink, hbold

from src.tgbot.models.database import DataBase


def get_random_string(length: int) -> str:
    letters = string.ascii_uppercase
    result = ''.join(random.choice(letters) for _ in range(length))
    return result


def encoder(*args: str | int) -> str:
    args = [str(arg) for arg in args]
    return "&&".join(args)


def decoder(text: str) -> list:
    return text.split("&&")


def chunks(array, chunk_size):
    for i in range(0, len(array), chunk_size):
        yield array[i:i + chunk_size]


async def check_wallets(bot: Bot, db: DataBase):
    rows = db.get_unique_wallets()

    results = []
    for row in chunks(rows, 100):
        for wallet_id, last_event_id in row:
            await asyncio.sleep(0.3)
            results.extend(await check_wallet(wallet_id, last_event_id, bot, db))

    for result in results:
        if result.get('status'):
            wallet_id = result.get('wallet_id')
            send_info = db.get_send_info(wallet_id)

            for chat_id, wallet_name in send_info:
                wallet_name = wallet_name if wallet_name else f'{wallet_id[:3]}...{wallet_id[-3:]}'
                wallet_hlink = hlink(wallet_name, f'https://tonviewer.com/{wallet_id}')

                text = (
                    f'📊 {hbold("Новое событие")}\n\n'
                    f'💰 {hbold("Кошелек:")} {wallet_hlink}\n\n\n'
                    f'♻️ {hbold("Транзакции:")}\n\n\n'
                    f'{result.get("transactions")}'
                )

                await bot.send_message(
                    chat_id,
                    text
                )


def validate_amount(_amount: str | int) -> float | str:
    if int(_amount) > 0:
        return round(int(_amount) / 1000000000, 2)

    return 'Неизвестно'


async def get_new_events(events: list, last_event_id: str):
    last_event_id_index = next((index for (index, event) in enumerate(events) if event['event_id'] == last_event_id),
                               None)

    if last_event_id_index is None:
        return events

    return events[0:last_event_id_index]


async def process_events(events: list, last_event_id: str, wallet: str, db: DataBase):
    events = await get_new_events(events, last_event_id)

    result = []
    for event_index, event in enumerate(events):
        event_id = event.get('event_id')
        account_id = event.get('account').get('address')
        transactions = ''

        if event_index == 0:
            db.update_wallet_last_event_id(wallet, event_id)

        for action_index, action in enumerate(event.get('actions')):
            if action_index >= 10:
                transactions += f'И {hbold(len(event.get("actions")) - 10)} других транзакций\n\n'
                break

            action_type = action.get('type')
            type_name = action.get('simple_preview', {}).get("name", 0)
            description = action.get('simple_preview', {}).get("description", 'Неизвестно')

            if 'Transfer' in action_type:
                amount = validate_amount(action.get(action_type, {}).get('amount', 0))
                finance_action = action.get(action_type, {}).get('sender', {}).get('address', '')

                if finance_action == '':
                    finance_action = '#Неизвестно'

                elif finance_action == account_id:
                    finance_action = '#Списание'

                else:
                    finance_action = '#Получение'

                transactions += (
                    f'🔑 {hbold("Тип:")} {type_name}\n'
                    f'🔰 {hbold("Описание:")} {description}\n'
                    f'📤 {hbold("Действие:")} {finance_action}\n'
                    f'💶 {hbold("Сумма:")} {amount}\n\n'
                )

            elif 'Contract' in action_type:
                amount = validate_amount(action.get(action_type, {}).get('ton_attached', 0))

                transactions += (
                    f'🔑 {hbold("Тип:")} {type_name}\n'
                    f'🔰 {hbold("Описание:")} {description}\n'
                    f'📤 {hbold("Действие:")} #Списание\n'
                    f'💶 {hbold("Сумма:")} {amount}\n\n'
                )

            elif 'Stake' in action_type:
                amount = validate_amount(action.get(action_type, {}).get('amount', 0))

                transactions += (
                    f'🔑 {hbold("Тип:")} {type_name}\n'
                    f'🔰 {hbold("Описание:")} {description}\n'
                    f'📥 {hbold("Действие:")} #Получение\n'
                    f'💶 {hbold("Сумма:")} {amount}\n\n'
                )

            elif 'Mint' in action_type:
                amount = validate_amount(action.get(action_type, {}).get('amount', 0))

                transactions += (
                    f'🔑 {hbold("Тип:")} {type_name}\n'
                    f'🔰 {hbold("Описание:")} {description}\n'
                    f'📥 {hbold("Действие:")} #Получение\n'
                    f'💶 {hbold("Сумма:")} {amount}\n\n'
                )

            elif 'Swap' in action_type:
                transactions += (
                    f'🔑 {hbold("Тип:")} {type_name}\n'
                    f'🔰 {hbold("Описание:")} {description}\n'
                    f'📥 {hbold("Действие:")} #Обмен\n\n'
                )
            else:
                transactions += (
                    f'🔑 {hbold("Тип:")} {type_name}\n'
                    f'🔰 {hbold("Описание:")} {description}\n'
                    f'❓ {hbold("Действие:")} Неизвестно\n\n'
                )

        result.append({
            'status': True,
            'wallet_id': wallet,
            'transactions': (
                f'{transactions}'
                f'⚜️ {hlink("Детали", f"https://tonviewer.com/transaction/{event_id}")}'
            )
        })

    return result


async def check_wallet(wallet: str, last_event_id: str, bot: Bot, db: DataBase):
    async with httpx.AsyncClient(headers={
        'Authorization': 'Bearer AEHYPKO6ZLFR5BQAAAADNPGK7PJU3J6EJ7GF4GRMYOLUZ3EPDLPULBVZ7Z4SLLPCOTGKQYA'}) as ahttpx:
        response = await ahttpx.get(f'https://tonapi.io/v2/accounts/{wallet}/events?limit=50')

        if response.status_code != 200:
            await bot.send_message(
                '1122881379',
                f'{hbold("Ошибка при проверке")}‼️\n\n'
                f'{hbold("Кошелек:")} {wallet}\n'
                f'{hbold("Статус Код:")} {response.status_code}\n'
                f'{hbold("Ошибка:")} {response.text}'
            )
            return [{
                'status': False,
            }]

    return await process_events(response.json().get('events'), last_event_id, wallet, db)
