import os
import pyxlsb
import pandas as pd
def read_file_excel_formats(file_path: str, skip_top_rows: int = 0, header_rows: int = 1, skip_bottom_rows: int = 0, csv_delimiter: str = ';') -> pd.DataFrame:
    """
    Читает файл по указанному пути в зависимости от его формата и возвращает DataFrame.
    Поддерживаемые форматы: .xlsx, .xls, .xlsm, .xlsb, .xlt, .xltm, .xltx, .csv
    Формат .xml и другие форматы (ods, txt, prn, dif, slik, xps) пока не реализованы.

    params:
        file_path: Путь к файлу.
        skip_top_rows: Количество строк для пропуска сверху.
        header_rows: Количество строк, которые рассматриваются как заголовки.
        skip_bottom_rows: Количество строк для пропуска снизу.
        csv_delimiter: Разделитель для CSV файлов.
    return:
        DataFrame, содержащий данные из файла.
    raises:
        FileNotFoundError: Если файл не найден.
        ValueError: Если файл имеет неподдерживаемый формат или более одной страницы (для Excel файлов).
        RuntimeError: Если произошла ошибка при чтении файла.
    """

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    # Определение расширения файла
    file_extension = os.path.splitext(file_path)[1].lower()

    try:
        if file_extension in ['.xlsx', '.xls', '.xlsm', '.xlt', '.xltm', '.xltx', '.xlsb']:
            # Определение движка для чтения файлов
            if file_extension in ['.xls', '.xlt']:
                engine = 'xlrd'
            elif file_extension == '.xlsb':
                engine = 'pyxlsb'
            else:
                engine = 'openpyxl'

            # Создание объекта ExcelFile для работы с файлами
            excel_file = pd.ExcelFile(file_path, engine=engine)

            # Проверка, что в файле только одна страница
            if len(excel_file.sheet_names) > 1:
                raise ValueError("Файл содержит более одной страницы.")

            df = pd.read_excel(
                file_path,
                sheet_name=0,
                skiprows=skip_top_rows,  # Пропуск указанных строк сверху
                header=list(range(header_rows)),  # Установка заголовков из указанного количества строк
                skipfooter=skip_bottom_rows,  # Пропуск строк снизу
                engine=engine,  # Использование указанного движка для чтения
                dtype=str,  # Принудительное чтение всех данных как строк
            )
            # Преобразование всех уровней MultiIndex в строки

            df.columns = pd.MultiIndex.from_tuples([
                                tuple([str(level) for level in column]) if isinstance(column, tuple) else (str(column),)
                                for column in df.columns])
            # Обеспечиваем уникальность колонок
            df.columns = pd.MultiIndex.from_tuples(pd.io.common.dedup_names(df.columns, is_potential_multiindex=True))

        elif file_extension == '.csv':
            # Чтение CSV файла без заголовков
            df = pd.read_csv(
                file_path,
                skiprows=skip_top_rows,
                skipfooter=skip_bottom_rows,
                engine='python',
                header=None,
                delimiter=csv_delimiter,
                dtype=str
            )
            # Создание MultiIndex для заголовков
            headers = [list(df.iloc[i]) for i in range(header_rows)]
            multi_index = pd.MultiIndex.from_arrays(headers, names=[f'Level_{i+1}' for i in range(header_rows)])
            # Назначение MultiIndex в качестве заголовков
            df.columns = multi_index
            #Склеивает заголовки
            # df.columns = ['_'.join(map(str, col)) for col in df.columns]
            df = df.iloc[header_rows:]
            # Обеспечиваем уникальность колонок
            df.columns = pd.MultiIndex.from_tuples(pd.io.common.dedup_names(df.columns, is_potential_multiindex=True))

        # # Чтение XML файлов
        # elif file_extension == '.xml':
        #     # Чтение XML файла с использованием lxml (необходима установка библиотеки lxml)
        #     df = pd.read_xml(file_path, parser='lxml')

        else:
            raise ValueError(f"Не поддерживаемый формат файла: {file_extension}")

    except Exception as e:
        raise RuntimeError(f"Ошибка при чтении файла: {e}")

    # Возвращаем DataFrame с прочитанными данными
    return df.reset_index(drop=True)
