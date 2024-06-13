from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.tgbot.keyboards import inline
from src.tgbot.misc.states import AddUser
from src.tgbot.services.utils import decoder

router = Router()


@router.callback_query(
    AddUser.get_date_of_expiry,
    decoder(F.data)[0].in_(['prev_month', 'next_month', 'none'])
)
async def pagination_calendar(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    calendar_title = data.get('calendar_title')
    calldata = decoder(call.data)

    if calldata[0] == 'none':
        return await call.answer('Не тыкай туда, куда не надо)')

    data, month, year = calldata[0], int(calldata[1]), int(calldata[2])

    await call.answer()

    if data == 'prev_month':
        month -= 1
        month, year = (12, year - 1) if month < 1 else (month, year)

        return await call.message.edit_text(
            text=calendar_title,
            reply_markup=inline.create_calendar(month, year)
        )

    if data == 'next_month':
        month += 1
        month, year = (1, year + 1) if month > 12 else (month, year)

        return await call.message.edit_text(
            text=calendar_title,
            reply_markup=inline.create_calendar(month, year)
        )
