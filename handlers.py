from aiogram import types, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart, StateFilter, CommandObject, CREATOR
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from service import generate_options_keyboard, get_question, new_quiz, get_quiz_index, update_quiz_index, update_statistics,get_statistics,get_table_rows,get_table_row
import os
import logging
import json

router = Router()
image_path = os.getenv("IMAGE_PATH")
@router.callback_query()
async def right_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    user_id=callback.from_user.id
    first_name=callback.from_user.first_name
   
    current_question_index = await get_quiz_index(user_id)
    res=await get_table_row(current_question_index)
    res=json.loads(res)
    correct_index = res['correct_option']
    opts = res['options']

    await callback.message.answer(f'Ваш ответ: {callback.data}')

    if callback.data != opts[correct_index]:
        correct_option = res['correct_option']
        await callback.message.answer(f"Неправильно. Правильный ответ: {res['options'][correct_option]}")
    else:
        point = await get_statistics(user_id)
        point+=1
        await update_statistics(user_id, point,first_name)
        await callback.message.answer('Верно')
    current_question_index += 1
    await update_quiz_index(user_id, current_question_index,first_name)
    table_rows=await get_table_rows('questions1')
    if current_question_index < len(table_rows):
        await get_question(callback.message, 
                            callback.from_user.id,
                            )
    else:
        point = await get_statistics(user_id)
        await callback.message.answer(f'Вы прошли весь квиз! Поздравляем!\nВы набрали {point} балла')
        #Получаем записи из таблицы
        table_rows=await get_table_rows('quiz_state')
        error = {"table_rows": table_rows}
        logging.error(json.dumps(error))
        results=''
        for row in table_rows:
            first_name = row[0]
            results += f"{first_name} набрал {row[2]} балла\n"
        await callback.message.answer(f'Общая статистика игроков\n{results}')
        await new_quiz(callback)
        #await update_quiz_index(user_id, 0, first_name)


# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.bot.send_photo(message.from_user.id, image_path)
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))


# Хэндлер на команду /quiz
@router.message(F.text=="Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)
    

