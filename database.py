import os
import ydb

YDB_ENDPOINT = os.getenv("YDB_ENDPOINT")
YDB_DATABASE = os.getenv("YDB_DATABASE")

def get_ydb_pool(ydb_endpoint, ydb_database, timeout=30):
    ydb_driver_config = ydb.DriverConfig(
        ydb_endpoint,
        ydb_database,
        credentials=ydb.credentials_from_env_variables(),
        root_certificates=ydb.load_ydb_root_certificate(),
    )

    ydb_driver = ydb.Driver(ydb_driver_config)
    ydb_driver.wait(fail_fast=True, timeout=timeout)
    return ydb.SessionPool(ydb_driver)


def _format_kwargs(kwargs):
    return {"${}".format(key): value for key, value in kwargs.items()}


# Заготовки из документации
# https://ydb.tech/en/docs/reference/ydb-sdk/example/python/#param-prepared-queries
def execute_update_query(pool, query, **kwargs):
    def callee(session):
        prepared_query = session.prepare(query)
        session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query, _format_kwargs(kwargs), commit_tx=True
        )

    return pool.retry_operation_sync(callee)


# Заготовки из документации
# https://ydb.tech/en/docs/reference/ydb-sdk/example/python/#param-prepared-queries
def execute_select_query(pool, query, **kwargs):
    def callee(session):
        prepared_query = session.prepare(query)
        result_sets = session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query, _format_kwargs(kwargs), commit_tx=True
        )
        return result_sets[0].rows

    return pool.retry_operation_sync(callee)    

# Зададим настройки базы данных 
pool = get_ydb_pool(YDB_ENDPOINT, YDB_DATABASE)


def execute_select_all_query(pool,query):
    def callee(session):
        prepared_query = session.prepare(query)
        result_sets = session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query, commit_tx=True
        )
        return result_sets[0].rows

    return pool.retry_operation_sync(callee)

# Структура квиза
quiz_data = [
    {
        'question': 'Что такое Python?',
        'options': ['Язык программирования', 'Тип данных', 'Музыкальный инструмент', 'Змея на английском'],
        'correct_option': 0
    },
    {
        'question': 'Какой тип данных используется для хранения целых чисел?',
        'options': ['int', 'float', 'str', 'natural'],
        'correct_option': 0
    },
    {
        'question': 'Какой тип данных используется для хранения вещественных чисел?',
        'options': ['int', 'float', 'str', 'natural'],
        'correct_option': 1
    },
    {
        'question': 'Какая библиотека используется для работы с массивами?',
        'options': ['asyncio', 'aiosqlite', 'numpy', 'aiogram'],
        'correct_option': 2
    },
    {
        'question': 'Как называется функция, которая используется для вычисления ошибки в модели машинного обучения?',
        'options': ['Функция активации', 'Функция потерь', 'Функция плотности вероятности', 'Функция распределения'],
        'correct_option': 1
    },
   
    {
        'question': 'Какая библиотека используется для работы с графиками?',
        'options': ['matplotlib', 'pandas', 'random', 'keras'],
        'correct_option': 0
    },
    {
        'question': 'Какая библиотека используется для работы с датсетами?',
        'options': ['matplotlib', 'pandas', 'random', 'keras'],
        'correct_option': 1
    },
    {
        'question': 'Что такое нейронная сеть?',
        'options': ['Алгоритм сортировки', 'Модель машинного обучения', 'База данных', 'Протокол передачи данных'],
        'correct_option': 1
    },
    {
        'question': 'Как называется процесс, в котором нейронная сеть подгоняет свои параметры, чтобы минимизировать ошибку на обучающих данных?',
        'options': ['Регрессия', 'Оптимизация', 'Тюнинг', 'Регуляризация'],
        'correct_option': 1
    },
    {
        'question': 'Как называется метод предотвращения переобучения в нейронных сетях, который заключается в случайном отключении некоторых нейронов во время обучения?',
        'options': ['Dropout', 'Batch normalization', 'Gradient clipping', 'Data augmentation'],
        'correct_option': 0
    },
    # Добавьте другие вопросы
]
