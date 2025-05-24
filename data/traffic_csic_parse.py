import pandas as pd

# Загрузка исходного CSV-файла
print("[*] Загрузка данных из csic_database.csv...")
try:
    data = pd.read_csv("csic_database.csv")
except FileNotFoundError:
    print("[!] Ошибка: Файл 'csic_database.csv' не найден. Укажите правильный путь.")
    exit(1)

# Обработка пропущенных значений
data.fillna('', inplace=True)

# Нормализация имен столбцов (для учета возможных различий в написании)
data.columns = data.columns.str.lower().str.replace('-', '')

# Словарь для сопоставления возможных имен столбцов
column_mapping = {
    'method': ['method'],
    'cookie': ['cookie', 'cookies'],
    'contenttype': ['contenttype', 'content-type'],
    'length': ['length', 'lenght', 'contentlength', 'content-length'],
    'content': ['content', 'body'],
    'url': ['url'],
    'classification': ['classification', 'label']
}

# Проверка наличия столбцов и выбор первого подходящего
selected_columns = {}
for target_col, possible_names in column_mapping.items():
    for name in possible_names:
        if name in data.columns:
            selected_columns[target_col] = name
            break
    else:
        print(f"[!] Предупреждение: Столбец {target_col} не найден. Будет создан пустой столбец.")
        selected_columns[target_col] = None

# Создание нового DataFrame с нужными столбцами
new_data = pd.DataFrame()

# Копирование данных или создание пустых столбцов
for target_col, source_col in selected_columns.items():
    if source_col:
        new_data[target_col] = data[source_col]
    else:
        new_data[target_col] = ''

# Фильтрация записей: оставляем только нормальный трафик
# Предполагаем, что classification = 0 или 'Normal' соответствует нормальному трафику
if new_data['classification'].dtype == 'object':
    # Если classification строка (например, 'Normal', 'Anomalous')
    new_data = new_data[new_data['classification'].str.lower() == 'normal']
else:
    # Если classification числовой (0 или 1)
    new_data = new_data[new_data['classification'] == 0]

# Переименование столбцов для соответствия запросу
new_data = new_data.rename(columns={
    'contenttype': 'content-type',
    'length': 'lenght'
})

# Проверка структуры нового датасета
print("[*] Структура нового датасета (первые 5 строк):")
print(new_data.head())
print("\n[*] Информация о столбцах:")
print(new_data.info())
print(f"\n[*] Количество записей после фильтрации: {len(new_data)}")

# Сохранение нового датасета в CSV
output_file = "csic_filtered_normal_traffic.csv"
new_data.to_csv(output_file, index=False)
print(f"[*] Новый датасет сохранен в {output_file}")