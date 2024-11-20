# Компоненты и соответствующие названия таблиц в БД
COMPONENTS = {
            "Процессор": 'cpu',
            "Материнская плата": 'motherboards',
            "Оперативная память": 'ram',
            "Видеокарта": 'gpu',
            "Устройство памяти": 'disk',
            "Блок питания": 'power',
            "Кулер для ЦП": 'cpu_coolers',
            "Корпус": 'core',
}

# Список параметров для работы с БД
PARAMS = {
    "cpu": {
        "Бренд": "brand",
        "Линейка процессоров": "cpu_group",
        "Сокет": "socket",
        "Вид поставки": "type"
    },
    "cpu_coolers": {
        "Бренд": "brand",
        "Максимальная рассеиваемая\nмощность (TDP), Вт": "tdp",
        "Сокет": "socket"
    },
    "gpu": {
        "Бренд": "brand",
        "Объем видеопамяти, Гб": "memory",
        "Разработчик видеокарты": "developer",
        "Тип памяти": "memory_type"
    },
    "disk": {
        "Бренд": "brand",
        "Емкость, Гб": "capacity"
    },
    "motherboards": {
        "Бренд": "brand",
        "Сокет": "socket",
        "Чипсет": "chipset",
        "Форм-фактор": "form_factor"
    },
    "ram": {
        "Бренд": "brand",
        "Объем памяти, Гб": "memory",
        "Тип памяти": "memory_type",
        "Частота памяти, МГц": "freq"
    },
    "power": {
        "Бренд": "brand",
        "Мощность, Вт": "power"
    },
    "core": {
        "Бренд": "brand",
        "Тип корпуса": "core_type",
        "Форм-фактор материнской платы": "form_factor"
    }
}

ADMIN_KEY = "yndx"
