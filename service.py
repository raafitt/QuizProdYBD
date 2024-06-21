from  database import pool, execute_update_query, execute_select_query, execute_select_all_query
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types
from database import quiz_data
import logging
import json

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=option,
        ))

    builder.adjust(1)
    return builder.as_markup()





async def get_question(message, user_id):
    
    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    print(current_question_index)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    first_name=message.from_user.first_name
    first_name=first_name.encode('utf-8')
    current_question_index = 0
    point=0
    await update_quiz_index(user_id, current_question_index,first_name)
    await update_statistics(user_id, point,first_name)
    await get_question(message, user_id)


async def get_quiz_index(user_id):
    get_user_index = f"""
        DECLARE $user_id AS Uint64;

        SELECT question_index
        FROM `quiz_state`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_index, user_id=user_id)

    if len(results) == 0:
        return 0
    if results[0]["question_index"] is None:
        return 0
    return results[0]["question_index"]    

async def get_statistics(user_id):
    get_user_statistics=f"""
        DECLARE $user_id AS Uint64;

        SELECT stat_query
        FROM `quiz_state`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_statistics, user_id=user_id)
    if len(results) == 0:
        return 0
    if results[0]["stat_query"] is None:
        return 0
    return results[0]["stat_query"]
    

async def update_quiz_index(user_id, question_index,first_name):
    try:
        set_quiz_state = f"""
            DECLARE $user_id AS Uint64;
            DECLARE $question_index AS Uint64;
            DECLARE $first_name AS Utf8;

            UPSERT INTO `quiz_state` (`user_id`, `question_index`,`first_name`)
            VALUES ($user_id, $question_index,$first_name);
        """

        execute_update_query(
            pool,
            set_quiz_state,
            user_id=user_id,
            question_index=question_index,
            first_name=first_name
        )
    except Exception as e:
        error = {"error": str(e), "location": "update_quiz_index()"}
        logging.error(json.dumps(error))

async def update_statistics(user_id, stat_query,first_name):
    set_quiz_state = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $stat_query AS Uint64;
        DECLARE $first_name AS Utf8;

        UPSERT INTO `quiz_state` (`user_id`, `stat_query`,`first_name`)
        VALUES ($user_id, $stat_query,$first_name);
    """

    execute_update_query(
        pool,
        set_quiz_state,
        user_id=user_id,
        stat_query=stat_query,
        first_name=first_name
    )

async def get_table_rows():
    try:
        query = f"""SELECT * FROM `quiz_state`"""
        results=execute_select_query(pool,query)
        if len(results) == 0:
            return 0
        return results
    except Exception as e:
        error = {"error": str(e), "location": "get_table_rows()"}
        logging.error(json.dumps(error))
