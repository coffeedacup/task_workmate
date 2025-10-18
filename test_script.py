import pytest
import csv
import tempfile
import os
import sys
from unittest.mock import patch, mock_open
from script import read_csv_files, calculate_average_rating, main


@pytest.fixture
def sample_csv_files():
    """Создает временные CSV-файлы с корректными данными для тестирования."""
    files_data = [
        "name,brand,price,rating\niphone,apple,1000,4.7\ngalaxy,samsung,800,4.5\n",
        "name,brand,price,rating\npoco,xiaomi,300,4.3\n"
    ]
    files = []
    for data in files_data:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(data)
            files.append(f.name)
    yield files
    for f in files:
        if os.path.exists(f):
            os.unlink(f)


@pytest.fixture
def invalid_csv_files():
    """Создает временные CSV-файлы с некорректными данными для тестирования."""
    files_data = [
        "name,brand,price,rating\niphone,apple,1000,invalid\n,sony,500,4.0\n",  # некорректный рейтинг и пустой бренд
        "name,price,rating\nphone,1000,4.7\n",  # отсутствует колонка brand
    ]
    files = []
    for data in files_data:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(data)
            files.append(f.name)
    yield files
    for f in files:
        if os.path.exists(f):
            os.unlink(f)


@pytest.fixture
def edge_case_csv_files():
    """Создает временные CSV-файлы с крайними случаями."""
    files_data = [
        "name,brand,price,rating\n",  # пустой файл с заголовком
        "name,brand,price,rating\nphone,,1000,4.5\n,sony,500,4.0\n",  # пустые бренды
        "name,brand,price,rating\nphone,sony,1000,\nphone,apple,500,4.5\n",  # пустые рейтинги
    ]
    files = []
    for data in files_data:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(data)
            files.append(f.name)
    yield files
    for f in files:
        if os.path.exists(f):
            os.unlink(f)


def test_read_csv_files(sample_csv_files):
    """Тест корректного чтения CSV-файлов."""
    data = read_csv_files(sample_csv_files)
    assert len(data) == 3
    assert data[0]['brand'] == 'apple'
    assert data[1]['brand'] == 'samsung'
    assert data[2]['brand'] == 'xiaomi'


def test_read_nonexistent_file():
    """Тест обработки несуществующих файлов."""
    with pytest.raises(SystemExit):
        read_csv_files(['nonexistent.csv'])


def test_read_invalid_csv(invalid_csv_files):
    """Тест обработки CSV-файлов с некорректными данными."""
    data = read_csv_files([invalid_csv_files[0]])
    # Должен обработать только валидные данные (в данном случае - ни одной строки)
    assert len(data) == 0


def test_read_csv_missing_columns(invalid_csv_files):
    """Тест обработки CSV-файлов с отсутствующими колонками."""
    data = read_csv_files([invalid_csv_files[1]])
    # Файл без колонки brand должен быть пропущен
    assert len(data) == 0


def test_read_csv_edge_cases(edge_case_csv_files):
    """Тест обработки CSV-файлов с крайними случаями."""
    data = read_csv_files(edge_case_csv_files)
    # Должен обработать только валидные данные
    assert len(data) == 1  # только строка с apple из третьего файла


def test_read_csv_with_out_of_range_ratings():
    """Тест обработки рейтингов вне диапазона 0-5."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write("name,brand,price,rating\nphone,apple,1000,6.0\nphone,sony,500,-1.0\nphone,samsung,800,5.0\n")
        temp_file = f.name
    
    try:
        data = read_csv_files([temp_file])
        # Должен обработать только валидные данные (рейтинг 5.0)
        assert len(data) == 1
        assert data[0]['brand'] == 'samsung'
        assert data[0]['rating'] == 5.0
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_calculate_average_rating():
    """Тест корректного вычисления среднего рейтинга."""
    sample_data = [
        {'brand': 'apple', 'rating': 4.7},
        {'brand': 'apple', 'rating': 4.9},
        {'brand': 'samsung', 'rating': 4.5}
    ]
    report = calculate_average_rating(sample_data)
    assert len(report) == 2
    assert report[0]['brand'] == 'apple'
    assert report[0]['average_rating'] == 4.8
    assert report[1]['brand'] == 'samsung'
    assert report[1]['average_rating'] == 4.5


def test_calculate_rating_with_invalid_data():
    """Тест вычисления рейтинга с некорректными данными."""
    sample_data = [
        {'brand': 'apple', 'rating': 4.7},
        {'brand': 'apple'},  # отсутствует рейтинг
        {'brand': '', 'rating': 4.5},  # пустой бренд
        {'not_brand': 'sony', 'rating': 4.0},  # отсутствует ключ 'brand'
    ]
    report = calculate_average_rating(sample_data)
    # Должен обработать только валидные данные
    assert len(report) == 1
    assert report[0]['brand'] == 'apple'
    assert report[0]['average_rating'] == 4.7


def test_calculate_rating_empty_data():
    """Тест вычисления рейтинга с пустыми данными."""
    sample_data = []
    report = calculate_average_rating(sample_data)
    assert report == []


def test_calculate_rating_all_invalid():
    """Тест вычисления рейтинга когда все данные некорректны."""
    sample_data = [
        {'brand': '', 'rating': 4.5},
        {'not_brand': 'sony', 'rating': 4.0},
    ]
    report = calculate_average_rating(sample_data)
    assert report == []


def test_calculate_rating_single_brand():
    """Тест вычисления рейтинга для одного бренда."""
    sample_data = [
        {'brand': 'apple', 'rating': 4.5},
        {'brand': 'apple', 'rating': 5.0},
    ]
    report = calculate_average_rating(sample_data)
    assert len(report) == 1
    assert report[0]['brand'] == 'apple'
    assert report[0]['average_rating'] == 4.75


def test_calculate_rating_rounding():
    """Тест округления среднего рейтинга."""
    sample_data = [
        {'brand': 'apple', 'rating': 4.0},
        {'brand': 'apple', 'rating': 4.0},
        {'brand': 'apple', 'rating': 5.0},
    ]
    report = calculate_average_rating(sample_data)
    assert report[0]['average_rating'] == 4.33  # (4+4+5)/3 = 4.333... округляется до 4.33


def test_file_encoding_error():
    """Тест обработки ошибки кодировки файла."""
    # Создаем файл с бинарными данными (не UTF-8)
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.csv') as f:
        f.write(b'\xff\xfe\xff\xfe')  # невалидные UTF-8 данные
        temp_file = f.name
    
    try:
        # Должен завершиться с ошибкой SystemExit
        with pytest.raises(SystemExit):
            read_csv_files([temp_file])
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_permission_error():
    """Тест обработки ошибки прав доступа к файлу."""
    # Мокаем open чтобы вызвать PermissionError
    with patch('builtins.open', side_effect=PermissionError("No permission")):
        with pytest.raises(SystemExit):
            read_csv_files(['dummy.csv'])


@patch('script.read_csv_files')
@patch('script.calculate_average_rating')
@patch('script.tabulate')
def test_main_success(mock_tabulate, mock_calculate, mock_read):
    """Тест успешного выполнения main функции."""
    mock_read.return_value = [{'brand': 'apple', 'rating': 4.5}]
    mock_calculate.return_value = [{'brand': 'apple', 'average_rating': 4.5}]
    mock_tabulate.return_value = "table output"
    
    test_args = ["script.py", "--files", "test.csv", "--report", "average-rating"]
    with patch.object(sys, 'argv', test_args):
        # Не должно вызывать SystemExit при успешном выполнении
        try:
            main()
        except SystemExit as e:
            # Если main завершается с кодом 0, это нормально
            if e.code != 0:
                raise
        else:
            # Если не было SystemExit, тоже нормально
            pass
    
    mock_read.assert_called_once_with(["test.csv"])
    mock_calculate.assert_called_once()
    mock_tabulate.assert_called_once()


@patch('script.read_csv_files')
def test_main_no_data(mock_read):
    """Тест main функции когда нет данных."""
    mock_read.return_value = []  # Нет данных
    
    test_args = ["script.py", "--files", "test.csv", "--report", "average-rating"]
    with patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit) as exc_info:
            main()
        # Должен завершиться с кодом 1 (ошибка)
        assert exc_info.value.code == 1


@patch('script.read_csv_files')
def test_main_empty_report(mock_read):
    """Тест main функции когда отчет пустой."""
    mock_read.return_value = [{'brand': 'apple', 'rating': 4.5}]
    
    # Мокаем calculate_average_rating чтобы вернуть пустой отчет
    with patch('script.calculate_average_rating', return_value=[]):
        test_args = ["script.py", "--files", "test.csv", "--report", "average-rating"]
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # Должен завершиться с кодом 0 (успех, но пустой отчет)
            assert exc_info.value.code == 0


def test_main_keyboard_interrupt():
    """Тест обработки KeyboardInterrupt в main функции."""
    with patch('script.argparse.ArgumentParser.parse_args') as mock_parse:
        mock_parse.side_effect = KeyboardInterrupt
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        # Должен завершиться с кодом 1
        assert exc_info.value.code == 1


def test_main_general_exception():
    """Тест обработки общего исключения в main функции."""
    with patch('script.argparse.ArgumentParser.parse_args') as mock_parse:
        mock_parse.side_effect = Exception("Test exception")
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        # Должен завершиться с кодом 1
        assert exc_info.value.code == 1


def test_file_not_csv():
    """Тест обработки файла с неправильным расширением."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("name,brand,price,rating\nphone,apple,1000,4.5\n")
        temp_file = f.name
    
    try:
        # Должен завершиться с ошибкой SystemExit
        with pytest.raises(SystemExit):
            # Мокаем sys.argv чтобы передать аргументы
            test_args = ["script.py", "--files", temp_file, "--report", "average-rating"]
            with patch.object(sys, 'argv', test_args):
                main()
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])