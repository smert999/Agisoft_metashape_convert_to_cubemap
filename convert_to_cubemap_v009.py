# === Часть 1: Импорты и вспомогательные функции ===
import os
import sys
import time
import traceback
import Metashape
import cv2
import numpy as np
import subprocess
import concurrent.futures

# Глобальная переменная для хранения GUI окна
gui_window = None

# === Проверка и установка зависимостей ===
def check_and_install_packages():
    """Проверяет наличие и устанавливает необходимые библиотеки."""
    required_packages = {
        "PyQt5": "pyqt5"
    }
    
    missing_packages = []
    for module_name, pip_name in required_packages.items():
        try:
            __import__(module_name)
            print(f"Библиотека {module_name} уже установлена.")
        except ImportError:
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"Отсутствуют необходимые библиотеки: {', '.join(missing_packages)}")
        try:
            metashape_python = os.path.join(os.path.dirname(Metashape.app.applicationPath), "python", "python.exe")
            for package in missing_packages:
                print(f"Установка {package}...")
                subprocess.check_call([metashape_python, "-m", "pip", "install", package])
            print("Все необходимые библиотеки успешно установлены.")
            
            # Перезагружаем модули после установки
            for module_name in required_packages.keys():
                if module_name in sys.modules:
                    del sys.modules[module_name]
            
            return True
        except Exception as e:
            print(f"Не удалось установить библиотеки: {str(e)}")
            print("Скрипт продолжит работу в консольном режиме.")
            return False
    
    return True

# Пытаемся установить и импортировать PyQt5
use_gui = check_and_install_packages()

# Импортируем PyQt5, если установка прошла успешно
if use_gui:
    try:
        from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                                   QLabel, QPushButton, QProgressBar, QFileDialog, 
                                   QMessageBox, QComboBox, QSpinBox, QDoubleSpinBox, QGroupBox)
        from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
        print("PyQt5 успешно импортирован, будет использован графический интерфейс.")
    except ImportError as e:
        print(f"Ошибка импорта PyQt5: {str(e)}")
        print("Скрипт продолжит работу в консольном режиме.")
        use_gui = False

# === Вспомогательные функции ===
def console_progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█', print_end="\r"):
    """
    Создает текстовый индикатор прогресса в консоли.
    """
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '░' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    if iteration == total:
        print()

def show_message(title, message):
    """
    Отображает сообщение с использованием API Metashape.
    Адаптирует вызов в зависимости от версии API.
    """
    try:
        # Пробуем вызвать с двумя аргументами (новая версия API)
        Metashape.app.messageBox(title, message)
    except TypeError:
        # Если не работает, пробуем с одним аргументом (старая версия API)
        Metashape.app.messageBox(f"{title}\n\n{message}")
    except Exception as e:
        # Если и это не работает, просто выводим сообщение в консоль
        print(f"\n{title}\n{'-' * len(title)}\n{message}")

def get_string_option(prompt, options):
    """
    Запрашивает у пользователя строковый выбор из списка опций.
    Адаптировано для разных версий API Metashape.
    """
    try:
        # Попытка использовать getInt для выбора из списка
        print(f"{prompt} (варианты: {', '.join(options)})")
        for i, option in enumerate(options):
            print(f"{i+1}. {option}")
        index = Metashape.app.getInt(f"{prompt} (1-{len(options)})", 1, 1, len(options))
        return options[index - 1]
    except:
        # Если getInt не работает, пробуем getString
        try:
            # Сначала пробуем новую версию API
            return Metashape.app.getString(prompt, options[0])
        except:
            # Если это не работает, используем простой getString и валидируем ввод
            result = Metashape.app.getString(prompt, options[0])
            if result in options:
                return result
            return options[0]  # Возвращаем значение по умолчанию, если ввод неверный

def format_time(seconds):
    """Форматирует время в удобочитаемый вид."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# === Часть 2: Функции для преобразования проекций ===
def eqruirect2persp_map(img_shape, FOV, THETA, PHI, Hd, Wd, overlap=10):
    """
    Создает карты отображения для преобразования эквиректангулярной проекции в перспективную.
    """
    equ_h, equ_w = img_shape
    equ_cx = (equ_w) / 2.0
    equ_cy = (equ_h) / 2.0

    wFOV = FOV + overlap
    hFOV = float(Hd) / Wd * wFOV

    c_x = (Wd) / 2.0
    c_y = (Hd) / 2.0

    w_len = 2 * np.tan(np.radians(wFOV / 2.0))
    w_interval = w_len / (Wd)

    h_len = 2 * np.tan(np.radians(hFOV / 2.0))
    h_interval = h_len / (Hd)

    x_map = np.zeros([Hd, Wd], np.float32) + 1
    y_map = np.tile((np.arange(0, Wd) - c_x) * w_interval, [Hd, 1])
    z_map = -np.tile((np.arange(0, Hd) - c_y) * h_interval, [Wd, 1]).T
    D = np.sqrt(x_map ** 2 + y_map ** 2 + z_map ** 2)

    xyz = np.zeros([Hd, Wd, 3], np.float64)
    xyz[:, :, 0] = (x_map / D)[:, :]
    xyz[:, :, 1] = (y_map / D)[:, :]
    xyz[:, :, 2] = (z_map / D)[:, :]

    y_axis = np.array([0.0, 1.0, 0.0], np.float32)
    z_axis = np.array([0.0, 0.0, 1.0], np.float32)
    [R1, _] = cv2.Rodrigues(z_axis * np.radians(THETA))
    [R2, _] = cv2.Rodrigues(np.dot(R1, y_axis) * np.radians(-PHI))

    xyz = xyz.reshape([Hd * Wd, 3]).T
    xyz = np.dot(R1, xyz)
    xyz = np.dot(R2, xyz).T
    lat = np.arcsin(xyz[:, 2] / 1)
    lon = np.zeros([Hd * Wd], np.float64)
    theta = np.arctan(xyz[:, 1] / xyz[:, 0])
    idx1 = xyz[:, 0] > 0
    idx2 = xyz[:, 1] > 0

    idx3 = ((1 - idx1) * idx2).astype(np.bool)
    idx4 = ((1 - idx1) * (1 - idx2)).astype(np.bool)

    lon[idx1] = theta[idx1]
    lon[idx3] = theta[idx3] + np.pi
    lon[idx4] = theta[idx4] - np.pi

    lon = lon.reshape([Hd, Wd]) / np.pi * 180
    lat = -lat.reshape([Hd, Wd]) / np.pi * 180
    lon = lon / 180 * equ_cx + equ_cx
    lat = lat / 90 * equ_cy + equ_cy

    return lon.astype(np.float32), lat.astype(np.float32)

def determine_coordinate_system():
    """
    Определяет тип координатной системы на основе анализа положения камер.
    """
    doc = Metashape.app.document
    chunk = doc.chunk
    cameras = [cam for cam in chunk.cameras if cam.transform]

    if not cameras:
        return "Y_UP"  # По умолчанию

    orientation_votes = {"Y_UP": 0, "Z_UP": 0, "X_UP": 0}

    for camera in cameras[:5]:
        rotation = camera.transform.rotation()
        up_vector = rotation * Metashape.Vector([0, 1, 0])

        y_alignment = abs(up_vector.y)
        z_alignment = abs(up_vector.z)
        x_alignment = abs(up_vector.x)

        if y_alignment > z_alignment and y_alignment > x_alignment:
            orientation_votes["Y_UP"] += 1
        elif z_alignment > y_alignment and z_alignment > x_alignment:
            orientation_votes["Z_UP"] += 1
        elif x_alignment > y_alignment and x_alignment > z_alignment:
            orientation_votes["X_UP"] += 1

    determined_orientation = max(orientation_votes, key=orientation_votes.get)
    return determined_orientation

def fix_back_face_artifact(image):
    """
    Исправляет артефакт в виде черной вертикальной полосы в центре изображения.
    
    Parameters:
    -----------
    image : numpy.ndarray
        Исходное изображение грани куба с артефактом
        
    Returns:
    --------
    numpy.ndarray
        Исправленное изображение
    """
    height, width = image.shape[:2]
    center_x = width // 2
    
    # Ширина полосы, которую нужно обработать
    strip_width = 3
    
    # Создаем копию изображения для обработки
    fixed_image = image.copy()
    
    # Определяем диапазон пикселей для обработки
    left_x = max(0, center_x - strip_width)
    right_x = min(width - 1, center_x + strip_width)
    
    # Для каждой строки изображения
    for y in range(height):
        # Проверяем, есть ли черные пиксели в центральной полосе
        strip = image[y, left_x:right_x+1]
        
        # Если есть слишком темные пиксели (возможно артефакт)
        if np.any(np.mean(strip, axis=1) < 30):  # Порог может требовать настройки
            # Используем значения с левой и правой стороны от полосы для интерполяции
            left_value = image[y, left_x-1] if left_x > 0 else image[y, right_x+1]
            right_value = image[y, right_x+1] if right_x < width-1 else image[y, left_x-1]
            
            # Линейная интерполяция между левым и правым значением
            for i, x in enumerate(range(left_x, right_x+1)):
                alpha = i / (right_x - left_x + 1)
                fixed_image[y, x] = (1 - alpha) * left_value + alpha * right_value
    
    # Применяем сглаживание только к исправленной полосе для лучшего смешивания
    temp_mask = np.zeros_like(image)
    temp_mask[:, left_x:right_x+1] = 255
    
    # Применяем размытие по Гауссу к исправленной области
    blur_region = cv2.GaussianBlur(fixed_image, (5, 5), 0)
    
    # Используем маску для объединения исходного изображения и размытой области
    mask = temp_mask.astype(np.float32) / 255.0
    blended = (mask * blur_region + (1.0 - mask) * fixed_image).astype(np.uint8)
    
    return blended

# === Часть 3: Оптимизированная функция конвертации с многопоточностью ===
def convert_spherical_to_cubemap(spherical_image_path, output_folder, camera_label, persp_size=None, overlap=10, 
                                file_format="jpg", quality=95, interpolation=cv2.INTER_CUBIC, max_workers=None):
    """
    Конвертирует сферическое изображение в кубическую проекцию.
    Использует многопоточность для ускорения обработки.
    
    Parameters:
    -----------
    spherical_image_path : str
        Путь к сферическому изображению
    output_folder : str
        Папка для сохранения выходных изображений
    camera_label : str
        Метка камеры
    persp_size : int, optional
        Размер граней куба. Если None, рассчитывается автоматически
    overlap : float
        Перекрытие между гранями в градусах
    file_format : str
        Формат файла: "jpg", "png", "tiff"
    quality : int
        Качество изображения (для JPEG): 1-100
    interpolation : int
        Метод интерполяции при ремаппинге
    max_workers : int, optional
        Максимальное количество рабочих потоков. По умолчанию минимум из 6 и количества ядер CPU.
    
    Returns:
    --------
    dict
        Словарь с путями к созданным граням куба
    """
    if max_workers is None:
        max_workers = min(6, os.cpu_count() or 1)
        
    spherical_image = cv2.imread(spherical_image_path)
    if spherical_image is None:
        raise ValueError(f"Не удалось загрузить изображение: {spherical_image_path}")

    equirect_height, equirect_width = spherical_image.shape[:2]
    
    # Автоматическое определение размера граней куба, если не указан
    if persp_size is None:
        # Используем примерно четверть ширины исходного изображения
        persp_size = min(max(equirect_width // 4, 512), 4096)
        persp_size = 2 ** int(np.log2(persp_size) + 0.5)
        print(f"Автоматически рассчитанный размер грани: {persp_size}px")

    faces_params = {
        "front": {"fov": 90, "theta": 0, "phi": 0},
        "right": {"fov": 90, "theta": 90, "phi": 0},
        "left": {"fov": 90, "theta": -90, "phi": 0},
        "top": {"fov": 90, "theta": 0, "phi": 90},
        "down": {"fov": 90, "theta": 0, "phi": -90},
        "back": {"fov": 90, "theta": 180, "phi": 0},
    }

    image_paths = {}
    
    # Настройки сохранения в зависимости от формата
    save_params = []
    file_ext = file_format.lower()
    
    if file_ext == "jpg" or file_ext == "jpeg":
        save_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        file_ext = "jpg"
    elif file_ext == "png":
        save_params = [cv2.IMWRITE_PNG_COMPRESSION, min(9, 10 - quality//10)]
        file_ext = "png"
    elif file_ext == "tiff" or file_ext == "tif":
        save_params = [cv2.IMWRITE_TIFF_COMPRESSION, 1]
        file_ext = "tiff"
    else:
        # По умолчанию используем JPEG
        save_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        file_ext = "jpg"

    # Функция для обработки одной грани куба (для многопоточности)
    def process_face(face_name, params):
        try:
            map_x, map_y = eqruirect2persp_map(
                img_shape=(equirect_height, equirect_width),
                FOV=params["fov"],
                THETA=params["theta"],
                PHI=params["phi"],
                Hd=persp_size,
                Wd=persp_size,
                overlap=overlap
            )
    
            perspective_image = cv2.remap(spherical_image, map_x, map_y, interpolation=interpolation)
        
            # Постобработка для грани "back" для устранения черной вертикальной полосы
            if face_name == "back":
                perspective_image = fix_back_face_artifact(perspective_image)
            
            output_filename = f"{camera_label}_{face_name}.{file_ext}"
            output_path = os.path.join(output_folder, output_filename)
            cv2.imwrite(output_path, perspective_image, save_params)
            return face_name, output_path
        except Exception as e:
            print(f"Ошибка при обработке грани {face_name}: {str(e)}")
            return face_name, None
    
    # Используем ThreadPoolExecutor для параллельной обработки граней
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Запускаем задачи на обработку граней
        future_to_face = {executor.submit(process_face, face_name, params): face_name 
                          for face_name, params in faces_params.items()}
        
        # Собираем результаты
        for future in concurrent.futures.as_completed(future_to_face):
            face_name = future_to_face[future]
            try:
                face_name, path = future.result()
                if path:
                    image_paths[face_name] = path
            except Exception as e:
                print(f"Ошибка при обработке грани {face_name}: {str(e)}")
    
    if not image_paths:
        raise ValueError("Не удалось создать ни одной грани куба.")
        
    return image_paths

# === Часть 4: Функция добавления камер ===
def add_cubemap_cameras(chunk, spherical_camera, image_paths, persp_size, coord_system="Y_UP"):
    """
    Добавляет камеры для граней куба на основе позиции сферической камеры.
    
    Parameters:
    -----------
    chunk : Metashape.Chunk
        Активный чанк Metashape
    spherical_camera : Metashape.Camera
        Исходная сферическая камера
    image_paths : dict
        Словарь с путями к изображениям граней куба
    persp_size : int
        Размер перспективного изображения (ширина и высота)
    coord_system : str
        Тип координатной системы ("Y_UP", "Z_UP", "X_UP")
    
    Returns:
    --------
    list
        Список созданных камер
    """
    # Позиция исходной сферической камеры
    position = spherical_camera.transform.translation()

    # Ориентация исходной сферической камеры
    base_rotation = spherical_camera.transform.rotation()

    # Преобразуем base_rotation (3x3) в матрицу 4x4
    def convert_to_4x4(matrix_3x3):
        return Metashape.Matrix([
            [matrix_3x3[0, 0], matrix_3x3[0, 1], matrix_3x3[0, 2], 0],
            [matrix_3x3[1, 0], matrix_3x3[1, 1], matrix_3x3[1, 2], 0],
            [matrix_3x3[2, 0], matrix_3x3[2, 1], matrix_3x3[2, 2], 0],
            [0, 0, 0, 1]
        ])

    base_rotation_4x4 = convert_to_4x4(base_rotation)

    # Словарь с направлениями для граней куба для разных координатных систем
    cubemap_directions = {}
    
    # Для системы Y_UP (Y - вверх, Z - вперед, X - вправо)
    if coord_system == "Y_UP":
        cubemap_directions = {
            "front": {"forward": [0, 0, 1], "up": [0, 1, 0]},
            "right": {"forward": [1, 0, 0], "up": [0, 1, 0]},
            "left": {"forward": [-1, 0, 0], "up": [0, 1, 0]},
            "top": {"forward": [0, 1, 0], "up": [0, 0, -1]},
            "down": {"forward": [0, -1, 0], "up": [0, 0, 1]},
            "back": {"forward": [0, 0, -1], "up": [0, 1, 0]},
        }
    # Для системы Z_UP (Z - вверх, X - вперед, Y - вправо)
    elif coord_system == "Z_UP":
        cubemap_directions = {
            "front": {"forward": [1, 0, 0], "up": [0, 0, 1]},
            "right": {"forward": [0, 1, 0], "up": [0, 0, 1]},
            "left": {"forward": [0, -1, 0], "up": [0, 0, 1]},
            "top": {"forward": [0, 0, 1], "up": [-1, 0, 0]},
            "down": {"forward": [0, 0, -1], "up": [1, 0, 0]},
            "back": {"forward": [-1, 0, 0], "up": [0, 0, 1]},
        }
    # Для системы X_UP (X - вверх, Y - вперед, Z - вправо)
    elif coord_system == "X_UP":
        cubemap_directions = {
            "front": {"forward": [0, 1, 0], "up": [1, 0, 0]},
            "right": {"forward": [0, 0, 1], "up": [1, 0, 0]},
            "left": {"forward": [0, 0, -1], "up": [1, 0, 0]},
            "top": {"forward": [1, 0, 0], "up": [0, -1, 0]},
            "down": {"forward": [-1, 0, 0], "up": [0, 1, 0]},
            "back": {"forward": [0, -1, 0], "up": [1, 0, 0]},
        }
    else:
        print(f"Предупреждение: неизвестная координатная система '{coord_system}'. Используем Y_UP.")
        cubemap_directions = {
            "front": {"forward": [0, 0, 1], "up": [0, 1, 0]},
            "right": {"forward": [1, 0, 0], "up": [0, 1, 0]},
            "left": {"forward": [-1, 0, 0], "up": [0, 1, 0]},
            "top": {"forward": [0, 1, 0], "up": [0, 0, -1]},
            "down": {"forward": [0, -1, 0], "up": [0, 0, 1]},
            "back": {"forward": [0, 0, -1], "up": [0, 1, 0]},
        }

    # Функция для создания матрицы вращения
    def create_rotation_matrix(forward, up, base_rotation_4x4):
        # Нормализуем вектор forward
        forward = Metashape.Vector(forward).normalized()

        # Рассчитываем вектор right как перпендикулярный forward и up
        up = Metashape.Vector(up)
        right = Metashape.Vector.cross(forward, up).normalized()

        # Пересчитываем up, чтобы он был перпендикулярен forward и right
        up = Metashape.Vector.cross(right, forward).normalized()

        # Создаем матрицу вращения
        rotation_matrix = Metashape.Matrix([
            [right.x, right.y, right.z, 0],
            [up.x, up.y, up.z, 0],
            [forward.x, forward.y, forward.z, 0],
            [0, 0, 0, 1]
        ])

        # Применяем базовую ориентацию сферической камеры
        return base_rotation_4x4 * rotation_matrix

    # Создаем камеры для каждой грани куба
    cameras_created = []
    for face_name, directions in cubemap_directions.items():
        # Пропускаем грани, для которых нет изображений
        if face_name not in image_paths:
            continue
            
        # Создаем новую камеру
        camera = chunk.addCamera()
        camera.label = f"{spherical_camera.label}_{face_name}"
        
        # Копируем или создаем новый сенсор
        persp_sensors = [s for s in chunk.sensors if s.type == Metashape.Sensor.Type.Frame]
        if persp_sensors:
            camera.sensor = persp_sensors[0]
        else:
            # Если нет подходящего сенсора, создаем новый
            sensor = chunk.addSensor()
            sensor.label = f"Perspective_{persp_size}px"
            sensor.type = Metashape.Sensor.Type.Frame
            sensor.width = persp_size
            sensor.height = persp_size
            camera.sensor = sensor
        
        cameras_created.append(camera)

        # Настройка параметров камеры
        sensor = camera.sensor
        sensor.type = Metashape.Sensor.Type.Frame
        sensor.width = persp_size
        sensor.height = persp_size

        # Устанавливаем фокусное расстояние для поля зрения 90 градусов
        focal_length = persp_size / (2 * np.tan(np.radians(90 / 2)))
        sensor.focal_length = focal_length
        sensor.pixel_width = 1
        sensor.pixel_height = 1

        # Устанавливаем матрицу внутренних параметров камеры
        calibration = sensor.calibration
        calibration.f = focal_length
        calibration.cx = persp_size / 2
        calibration.cy = persp_size / 2
        calibration.k1 = 0
        calibration.k2 = 0
        calibration.k3 = 0
        calibration.p1 = 0
        calibration.p2 = 0

        # Устанавливаем позицию камеры
        camera.transform = Metashape.Matrix.Translation(position)

        # Устанавливаем ориентацию камеры
        forward = directions["forward"]
        up = directions["up"]
        rotation_matrix = create_rotation_matrix(forward, up, base_rotation_4x4)
        camera.transform = camera.transform * rotation_matrix

        # Создаем объект Photo для камеры
        camera.photo = Metashape.Photo()

        # Загружаем изображение
        camera.photo.path = image_paths[face_name]

        # Проверяем, существует ли файл изображения
        if not os.path.exists(camera.photo.path):
            print(f"Ошибка: файл изображения не найден: {camera.photo.path}")
            continue

        # Обновляем метаданные
        camera.meta['Image/Width'] = str(persp_size)
        camera.meta['Image/Height'] = str(persp_size)
        camera.meta['Image/Orientation'] = "1"
    
    return cameras_created

# === Часть 5: Многопоточная обработка камер для GUI ===
if 'PyQt5' in sys.modules:
    from PyQt5.QtCore import QThread, pyqtSignal
    
    class ProcessCamerasThread(QThread):
        update_progress = pyqtSignal(int, int, str, str, int)  # прогресс, всего, имя камеры, статус, процент
        processing_finished = pyqtSignal(bool, dict)  # успех, статистика
        error_occurred = pyqtSignal(str)  # сообщение об ошибке
        
        def __init__(self, cameras, output_folder, options):
            super().__init__()
            self.cameras = cameras
            self.output_folder = output_folder
            self.options = options
            self.stop_requested = False
            # Количество потоков для обработки граней
            self.faces_threads = self.options.get("faces_threads", min(6, os.cpu_count() or 1))
        
        def run(self):
            try:
                start_time = time.time()
                total_cameras = len(self.cameras)
                processed_count = 0
                skipped_count = 0
                errors = []
                
                # Обработка камер по одной (для возможности остановки)
                for i, camera in enumerate(self.cameras):
                    if self.stop_requested:
                        self.processing_finished.emit(False, {
                            "processed": processed_count,
                            "skipped": skipped_count,
                            "total": total_cameras,
                            "time": time.time() - start_time
                        })
                        return
                    
                    try:
                        camera_label = camera.label
                        spherical_image_path = camera.photo.path
                        
                        self.update_progress.emit(
                            i + 1, total_cameras, 
                            camera_label, "Преобразование изображения...", 
                            int((i + 0.4) / total_cameras * 100)
                        )
                        
                        # Преобразование сферического изображения в кубическую проекцию 
                        # с использованием многопоточности
                        image_paths = convert_spherical_to_cubemap(
                            spherical_image_path=spherical_image_path,
                            output_folder=self.output_folder,
                            camera_label=camera_label,
                            persp_size=self.options.get("persp_size"),
                            overlap=self.options.get("overlap", 10),
                            file_format=self.options.get("file_format", "jpg"),
                            quality=self.options.get("quality", 95),
                            interpolation=self.options.get("interpolation", cv2.INTER_CUBIC),
                            max_workers=self.faces_threads
                        )
                        
                        # Получаем фактический размер изображения
                        actual_size = cv2.imread(list(image_paths.values())[0]).shape[0]
                        
                        self.update_progress.emit(
                            i + 1, total_cameras, 
                            camera_label, f"Добавление камер ({actual_size}px)...", 
                            int((i + 0.8) / total_cameras * 100)
                        )
                        
                        # Добавление новых камер для граней куба
                        add_cubemap_cameras(
                            chunk=Metashape.app.document.chunk,
                            spherical_camera=camera,
                            image_paths=image_paths,
                            persp_size=actual_size,
                            coord_system=self.options.get("coord_system", "Y_UP")
                        )
                        
                        processed_count += 1
                        self.update_progress.emit(
                            i + 1, total_cameras, 
                            camera_label, "Обработка завершена", 
                            int((i + 1) / total_cameras * 100)
                        )
                        
                    except Exception as e:
                        error_message = f"Ошибка при обработке камеры {camera.label}: {str(e)}"
                        print(error_message)
                        print(traceback.format_exc())
                        errors.append(error_message)
                        skipped_count += 1
                        self.update_progress.emit(
                            i + 1, total_cameras, 
                            camera.label, "Ошибка", 
                            int((i + 1) / total_cameras * 100)
                        )
                
                total_time = time.time() - start_time
                self.processing_finished.emit(True, {
                    "processed": processed_count,
                    "skipped": skipped_count,
                    "total": total_cameras,
                    "time": total_time,
                    "errors": errors
                })
                
            except Exception as e:
                error_message = f"Общая ошибка обработки: {str(e)}"
                print(error_message)
                print(traceback.format_exc())
                self.error_occurred.emit(error_message)
        
        def stop(self):
            self.stop_requested = True

# === Часть 6: Графический интерфейс ===
if 'PyQt5' in sys.modules:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QProgressBar, QFileDialog, 
                               QMessageBox, QComboBox, QSpinBox, QDoubleSpinBox, QGroupBox)
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
    
    class CubemapConverterGUI(QMainWindow):
        def __init__(self):
            super().__init__()
            self.init_ui()
            self.process_thread = None
            
        def init_ui(self):
            # Настройка основного окна
            self.setWindowTitle('Конвертация сферических изображений в кубическую проекцию')
            self.setGeometry(100, 100, 800, 600)
            
            # Основной виджет и компоновка
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            main_layout = QVBoxLayout(central_widget)
            
            # Группа настроек
            settings_group = QGroupBox("Настройки")
            settings_layout = QVBoxLayout()
            
            # Выбор выходной папки
            output_folder_layout = QHBoxLayout()
            self.output_folder_label = QLabel("Выходная папка:")
            self.output_folder_path = QLabel("Не выбрана")
            self.output_folder_path.setStyleSheet("font-weight: bold;")
            self.browse_button = QPushButton("Обзор...")
            self.browse_button.clicked.connect(self.select_output_folder)
            
            output_folder_layout.addWidget(self.output_folder_label)
            output_folder_layout.addWidget(self.output_folder_path, 1)
            output_folder_layout.addWidget(self.browse_button)
            settings_layout.addLayout(output_folder_layout)
            
            # Настройка перекрытия
            overlap_layout = QHBoxLayout()
            overlap_label = QLabel("Перекрытие (градусы):")
            self.overlap_spinner = QDoubleSpinBox()
            self.overlap_spinner.setRange(0, 20)
            self.overlap_spinner.setValue(10)
            self.overlap_spinner.setDecimals(1)
            self.overlap_spinner.setSingleStep(0.5)
            
            overlap_layout.addWidget(overlap_label)
            overlap_layout.addWidget(self.overlap_spinner)
            settings_layout.addLayout(overlap_layout)
            
            # Выбор размера грани куба
            size_layout = QHBoxLayout()
            size_label = QLabel("Размер грани куба:")
            self.size_combo = QComboBox()
            self.size_combo.addItem("Автоматически (рекомендуется)", None)
            for size in [512, 1024, 2048, 4096]:
                self.size_combo.addItem(f"{size}x{size}", size)
            self.size_combo.setCurrentIndex(0)  # Автоматически по умолчанию
            
            size_layout.addWidget(size_label)
            size_layout.addWidget(self.size_combo)
            settings_layout.addLayout(size_layout)
            
            # Выбор координатной системы
            coord_system_layout = QHBoxLayout()
            coord_system_label = QLabel("Координатная система:")
            self.coord_system_combo = QComboBox()
            self.coord_system_combo.addItems(["Y_UP", "Z_UP", "X_UP", "Автоопределение"])
            self.coord_system_combo.setCurrentText("Автоопределение")
            
            coord_system_layout.addWidget(coord_system_label)
            coord_system_layout.addWidget(self.coord_system_combo)
            settings_layout.addLayout(coord_system_layout)
            
            # Настройка многопоточности
            thread_layout = QHBoxLayout()
            thread_label = QLabel("Количество потоков:")
            self.thread_spinner = QSpinBox()
            self.thread_spinner.setRange(1, os.cpu_count() or 4)
            self.thread_spinner.setValue(min(6, os.cpu_count() or 1))
            self.thread_spinner.setToolTip("Количество параллельных потоков для обработки граней куба")
            
            thread_layout.addWidget(thread_label)
            thread_layout.addWidget(self.thread_spinner)
            settings_layout.addLayout(thread_layout)
            
            # Группа параметров изображения
            image_group = QGroupBox("Параметры изображения")
            image_layout = QVBoxLayout()
            
            # Выбор формата файла
            format_layout = QHBoxLayout()
            format_label = QLabel("Формат файла:")
            self.format_combo = QComboBox()
            self.format_combo.addItems(["JPEG (JPG)", "PNG", "TIFF"])
            self.format_combo.setCurrentIndex(0)
            
            format_layout.addWidget(format_label)
            format_layout.addWidget(self.format_combo)
            image_layout.addLayout(format_layout)
            
            # Выбор качества изображения
            quality_layout = QHBoxLayout()
            quality_label = QLabel("Качество:")
            self.quality_spinner = QSpinBox()
            self.quality_spinner.setRange(75, 100)
            self.quality_spinner.setValue(95)
            self.quality_spinner.setSingleStep(1)
            
            quality_layout.addWidget(quality_label)
            quality_layout.addWidget(self.quality_spinner)
            image_layout.addLayout(quality_layout)
            
            # Выбор интерполяции
            interp_layout = QHBoxLayout()
            interp_label = QLabel("Интерполяция:")
            self.interp_combo = QComboBox()
            self.interp_combo.addItem("Ближайшая (быстрее, хуже качество)", cv2.INTER_NEAREST)
            self.interp_combo.addItem("Линейная (средняя)", cv2.INTER_LINEAR)
            self.interp_combo.addItem("Кубическая (медленнее, лучше качество)", cv2.INTER_CUBIC)
            self.interp_combo.setCurrentIndex(2)  # Кубическая по умолчанию
            
            interp_layout.addWidget(interp_label)
            interp_layout.addWidget(self.interp_combo)
            image_layout.addLayout(interp_layout)
            
            image_group.setLayout(image_layout)
            
            # Добавляем группы настроек в основную компоновку
            settings_group.setLayout(settings_layout)
            main_layout.addWidget(settings_group)
            main_layout.addWidget(image_group)
            
            # Информация о проекте
            info_group = QGroupBox("Информация о проекте")
            info_layout = QVBoxLayout()
            
            # Количество камер
            camera_count_layout = QHBoxLayout()
            camera_count_label = QLabel("Количество найденных камер:")
            self.camera_count_value = QLabel("0")
            self.camera_count_value.setStyleSheet("font-weight: bold;")
            camera_count_layout.addWidget(camera_count_label)
            camera_count_layout.addWidget(self.camera_count_value)
            info_layout.addLayout(camera_count_layout)
            
            # Определённая координатная система
            detected_system_layout = QHBoxLayout()
            detected_system_label = QLabel("Определённая координатная система:")
            self.detected_system_value = QLabel("Не определена")
            self.detected_system_value.setStyleSheet("font-weight: bold;")
            detected_system_layout.addWidget(detected_system_label)
            detected_system_layout.addWidget(self.detected_system_value)
            info_layout.addLayout(detected_system_layout)
            
            info_group.setLayout(info_layout)
            main_layout.addWidget(info_group)
            
            # Прогресс обработки
            progress_group = QGroupBox("Прогресс обработки")
            progress_layout = QVBoxLayout()
            
            # Общий прогресс
            self.progress_bar = QProgressBar()
            progress_layout.addWidget(self.progress_bar)
            
            # Текущая камера и статус
            current_camera_layout = QHBoxLayout()
            current_camera_label = QLabel("Текущая камера:")
            self.current_camera_value = QLabel("Нет")
            current_camera_layout.addWidget(current_camera_label)
            current_camera_layout.addWidget(self.current_camera_value, 1)
            progress_layout.addLayout(current_camera_layout)
            
            # Статус обработки
            status_layout = QHBoxLayout()
            status_label = QLabel("Статус:")
            self.status_value = QLabel("Ожидание запуска")
            status_layout.addWidget(status_label)
            status_layout.addWidget(self.status_value, 1)
            progress_layout.addLayout(status_layout)
            
            # Оставшееся время
            time_layout = QHBoxLayout()
            time_label = QLabel("Оставшееся время:")
            self.time_value = QLabel("--:--:--")
            time_layout.addWidget(time_label)
            time_layout.addWidget(self.time_value)
            progress_layout.addLayout(time_layout)
            
            progress_group.setLayout(progress_layout)
            main_layout.addWidget(progress_group)
            
            # Кнопки управления
            buttons_layout = QHBoxLayout()
            
            self.start_button = QPushButton("Запустить")
            self.start_button.clicked.connect(self.start_processing)
            self.start_button.setMinimumWidth(120)
            
            self.stop_button = QPushButton("Остановить")
            self.stop_button.clicked.connect(self.stop_processing)
            self.stop_button.setEnabled(False)
            self.stop_button.setMinimumWidth(120)
            
            self.close_button = QPushButton("Закрыть")
            self.close_button.clicked.connect(self.close)
            self.close_button.setMinimumWidth(120)
            
            buttons_layout.addStretch()
            buttons_layout.addWidget(self.start_button)
            buttons_layout.addWidget(self.stop_button)
            buttons_layout.addWidget(self.close_button)
            buttons_layout.addStretch()
            
            main_layout.addLayout(buttons_layout)
            
            # Статусная строка
            self.status_bar = self.statusBar()
            self.status_bar.showMessage("Готов к работе")
            
            # Обновить информацию о проекте при запуске
            QTimer.singleShot(100, self.update_project_info)
        
        def select_output_folder(self):
            """Выбор папки для сохранения изображений"""
            folder = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения изображений")
            if folder:
                self.output_folder_path.setText(folder)
                
        def update_project_info(self):
            """Обновляет информацию о проекте"""
            try:
                doc = Metashape.app.document
                chunk = doc.chunk
                
                if not chunk:
                    QMessageBox.warning(self, "Ошибка", "Активный чанк не найден.")
                    return
                
                # Получаем список сферических камер
                spherical_cameras = [cam for cam in chunk.cameras if cam.transform and cam.photo]
                self.camera_count_value.setText(str(len(spherical_cameras)))
                
                # Определяем координатную систему
                if spherical_cameras:
                    try:
                        coord_system = determine_coordinate_system()
                        self.detected_system_value.setText(coord_system)
                    except Exception as e:
                        print(f"Ошибка при определении координатной системы: {str(e)}")
                        self.detected_system_value.setText("Ошибка определения")
                else:
                    self.status_bar.showMessage("Не найдено сферических камер для обработки")
                    self.detected_system_value.setText("Невозможно определить")
            
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось получить информацию о проекте: {str(e)}")
        
        def start_processing(self):
            """Запускает процесс обработки камер"""
            try:
                # Проверяем выходную папку
                output_folder = self.output_folder_path.text()
                if output_folder == "Не выбрана" or not os.path.exists(output_folder):
                    QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите существующую выходную папку.")
                    return
                
                # Получаем настройки из интерфейса
                overlap = self.overlap_spinner.value()
                persp_size = self.size_combo.currentData()  # None для автоматического размера
                
                # Получаем выбранную координатную систему
                coord_system_option = self.coord_system_combo.currentText()
                if coord_system_option == "Автоопределение":
                    coord_system = determine_coordinate_system()
                else:
                    coord_system = coord_system_option
                
                # Получаем настройки изображения
                format_text = self.format_combo.currentText()
                if "JPEG" in format_text:
                    file_format = "jpg"
                elif "PNG" in format_text:
                    file_format = "png"
                elif "TIFF" in format_text:
                    file_format = "tiff"
                else:
                    file_format = "jpg"
                
                quality = self.quality_spinner.value()
                interpolation = self.interp_combo.currentData()
                
                # Получаем настройки многопоточности
                faces_threads = self.thread_spinner.value()
                
                # Получаем список сферических камер
                doc = Metashape.app.document
                chunk = doc.chunk
                
                if not chunk:
                    QMessageBox.warning(self, "Ошибка", "Активный чанк не найден.")
                    return
                
                spherical_cameras = [cam for cam in chunk.cameras if cam.transform and cam.photo]
                
                if not spherical_cameras:
                    QMessageBox.warning(self, "Ошибка", "Не найдено сферических камер для обработки.")
                    return
                
                # Создаем и запускаем поток обработки
                self.process_thread = ProcessCamerasThread(
                    cameras=spherical_cameras,
                    output_folder=output_folder,
                    options={
                        "persp_size": persp_size,
                        "overlap": overlap,
                        "coord_system": coord_system,
                        "file_format": file_format,
                        "quality": quality,
                        "interpolation": interpolation,
                        "faces_threads": faces_threads
                    }
                )
                
                # Подключаем сигналы
                self.process_thread.update_progress.connect(self.update_progress)
                self.process_thread.processing_finished.connect(self.processing_finished)
                self.process_thread.error_occurred.connect(self.processing_error)
                
                # Обновляем интерфейс
                self.start_button.setEnabled(False)
                self.stop_button.setEnabled(True)
                self.progress_bar.setValue(0)
                self.status_value.setText("Обработка...")
                self.status_bar.showMessage(f"Обработка {len(spherical_cameras)} камер используя {faces_threads} потоков...")
                
                # Запускаем поток
                self.process_thread.start()
                
                # Запускаем таймер для обновления оставшегося времени
                self.start_time = time.time()
                self.timer = QTimer()
                self.timer.timeout.connect(self.update_remaining_time)
                self.timer.start(1000)  # Обновляем каждую секунду
            
            except Exception as e:
                error_message = f"Ошибка при запуске обработки: {str(e)}\n\n{traceback.format_exc()}"
                print(error_message)
                QMessageBox.critical(self, "Ошибка", error_message)

        # === Методы из Части 7 ===
        def stop_processing(self):
            """Останавливает процесс обработки"""
            if self.process_thread and self.process_thread.isRunning():
                reply = QMessageBox.question(
                    self, 'Подтверждение', 
                    'Вы уверены, что хотите прервать обработку?', 
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.status_value.setText("Прерывание...")
                    self.status_bar.showMessage("Прерывание обработки...")
                    self.process_thread.stop()
                    
        def update_progress(self, current, total, camera_name, status, progress_percent):
            """Обновляет информацию о прогрессе"""
            self.progress_bar.setValue(progress_percent)
            self.current_camera_value.setText(camera_name)
            self.status_value.setText(status)
        
        def update_remaining_time(self):
            """Обновляет оценку оставшегося времени"""
            if self.process_thread and self.process_thread.isRunning():
                elapsed = time.time() - self.start_time
                progress = self.progress_bar.value() / 100.0
                
                if progress > 0:
                    estimated_total = elapsed / progress
                    remaining = estimated_total - elapsed
                    self.time_value.setText(format_time(remaining))
        
        def processing_finished(self, success, stats):
            """Вызывается при завершении обработки"""
            if hasattr(self, 'timer') and self.timer:
                self.timer.stop()
            
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            
            # Формируем сообщение о результатах
            if success:
                message = f"Обработка завершена!\n\n"
                message += f"Всего камер: {stats['total']}\n"
                message += f"Успешно обработано: {stats['processed']}\n"
                message += f"Пропущено/ошибки: {stats['skipped']}\n"
                message += f"Общее время: {format_time(stats['time'])}"
                
                if stats['skipped'] > 0 and 'errors' in stats and stats['errors']:
                    message += f"\n\nОшибки ({len(stats['errors'])}):\n"
                    for i, error in enumerate(stats['errors'][:5]):  # Показываем первые 5 ошибок
                        message += f"{i+1}. {error}\n"
                    if len(stats['errors']) > 5:
                        message += f"... и еще {len(stats['errors']) - 5} ошибок."
                
                QMessageBox.information(self, "Завершено", message)
                self.status_value.setText("Завершено")
                self.status_bar.showMessage(f"Обработка завершена. Успешно: {stats['processed']}, Ошибок: {stats['skipped']}")
            else:
                message = "Обработка прервана пользователем."
                QMessageBox.warning(self, "Прервано", message)
                self.status_value.setText("Прервано")
                self.status_bar.showMessage("Обработка прервана пользователем")
        
        def processing_error(self, error_message):
            """Вызывается при возникновении ошибки в процессе обработки"""
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка:\n\n{error_message}")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.status_value.setText("Ошибка")
            self.status_bar.showMessage("Ошибка обработки")
            
        def closeEvent(self, event):
            """Обрабатывает закрытие окна"""
            if self.process_thread and self.process_thread.isRunning():
                reply = QMessageBox.question(
                    self, 'Подтверждение', 
                    'Обработка не завершена. Вы уверены, что хотите выйти?', 
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.process_thread.stop()
                    self.process_thread.wait(1000)  # Даем немного времени на завершение
                    event.accept()
                else:
                    event.ignore()

# === Часть 7: Методы GUI (продолжение) ===
if 'PyQt5' in sys.modules:
    from PyQt5.QtWidgets import QMessageBox, QDialogButtonBox
    
    # Продолжение класса CubemapConverterGUI (дополнительные методы)
    def stop_processing(self):
        """Останавливает процесс обработки"""
        if self.process_thread and self.process_thread.isRunning():
            reply = QMessageBox.question(
                self, 'Подтверждение', 
                'Вы уверены, что хотите прервать обработку?', 
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.status_value.setText("Прерывание...")
                self.status_bar.showMessage("Прерывание обработки...")
                self.process_thread.stop()
                
    def update_progress(self, current, total, camera_name, status, progress_percent):
        """Обновляет информацию о прогрессе"""
        self.progress_bar.setValue(progress_percent)
        self.current_camera_value.setText(camera_name)
        self.status_value.setText(status)
    
    def update_remaining_time(self):
        """Обновляет оценку оставшегося времени"""
        if self.process_thread and self.process_thread.isRunning():
            elapsed = time.time() - self.start_time
            progress = self.progress_bar.value() / 100.0
            
            if progress > 0:
                estimated_total = elapsed / progress
                remaining = estimated_total - elapsed
                self.time_value.setText(format_time(remaining))
    
    def processing_finished(self, success, stats):
        """Вызывается при завершении обработки"""
        if hasattr(self, 'timer') and self.timer:
            self.timer.stop()
        
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # Формируем сообщение о результатах
        if success:
            message = f"Обработка завершена!\n\n"
            message += f"Всего камер: {stats['total']}\n"
            message += f"Успешно обработано: {stats['processed']}\n"
            message += f"Пропущено/ошибки: {stats['skipped']}\n"
            message += f"Общее время: {format_time(stats['time'])}"
            
            if stats['skipped'] > 0 and 'errors' in stats and stats['errors']:
                message += f"\n\nОшибки ({len(stats['errors'])}):\n"
                for i, error in enumerate(stats['errors'][:5]):  # Показываем первые 5 ошибок
                    message += f"{i+1}. {error}\n"
                if len(stats['errors']) > 5:
                    message += f"... и еще {len(stats['errors']) - 5} ошибок."
            
            QMessageBox.information(self, "Завершено", message)
            self.status_value.setText("Завершено")
            self.status_bar.showMessage(f"Обработка завершена. Успешно: {stats['processed']}, Ошибок: {stats['skipped']}")
        else:
            message = "Обработка прервана пользователем."
            QMessageBox.warning(self, "Прервано", message)
            self.status_value.setText("Прервано")
            self.status_bar.showMessage("Обработка прервана пользователем")
    
    def processing_error(self, error_message):
        """Вызывается при возникновении ошибки в процессе обработки"""
        QMessageBox.critical(self, "Ошибка", f"Произошла ошибка:\n\n{error_message}")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_value.setText("Ошибка")
        self.status_bar.showMessage("Ошибка обработки")
        
    def closeEvent(self, event):
        """Обрабатывает закрытие окна"""
        if self.process_thread and self.process_thread.isRunning():
            reply = QMessageBox.question(
                self, 'Подтверждение', 
                'Обработка не завершена. Вы уверены, что хотите выйти?', 
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.process_thread.stop()
                self.process_thread.wait(1000)  # Даем немного времени на завершение
                event.accept()
            else:
                event.ignore()

# === Функция для консольной обработки с многопоточностью ===
def process_images_console():
    """
    Консольная версия функции для обработки изображений.
    Использует многопоточность для ускорения обработки.
    """
    try:
        # Проверяем, есть ли активный документ и чанк
        doc = Metashape.app.document
        if not doc:
            show_message("Ошибка", "Не найден активный документ Metashape.")
            return
            
        chunk = doc.chunk
        if not chunk:
            show_message("Ошибка", "Не найден активный чанк в документе.")
            return
            
        # Получаем список сферических камер
        spherical_cameras = [cam for cam in chunk.cameras if cam.transform and cam.photo]
        
        if not spherical_cameras:
            show_message("Ошибка", "Не найдено сферических камер для обработки.")
            return
            
        # Запрос выходной папки
        output_folder = Metashape.app.getExistingDirectory("Выберите папку для сохранения изображений")
        if not output_folder:
            return
            
        # Запрос значения перекрытия
        overlap = Metashape.app.getFloat("Введите значение перекрытия (0-20)", 10.0)
        if overlap is None:
            overlap = 10.0  # Устанавливаем значение по умолчанию
        if overlap < 0 or overlap > 20:
            show_message("Ошибка", "Значение перекрытия должно быть в диапазоне от 0 до 20.")
            return
            
        # Запрос размера грани куба
        size_options = ["Автоматически", "512x512", "1024x1024", "2048x2048", "4096x4096"]
        selected_size = get_string_option("Выберите размер грани куба", size_options)
        
        persp_size = None  # Автоматический размер по умолчанию
        if selected_size != "Автоматически":
            persp_size = int(selected_size.split("x")[0])
        
        # Запрос формата файла
        format_options = ["jpg", "png", "tiff"]
        file_format = get_string_option("Выберите формат файла (jpg, png, tiff)", format_options)
        
        # Запрос качества
        quality = Metashape.app.getInt("Введите качество изображения (75-100)", 95, 75, 100)
        
        # Запрос метода интерполяции
        interp_options = ["Ближайшая", "Линейная", "Кубическая"]
        interp_option = get_string_option("Выберите метод интерполяции", interp_options)
        
        interpolation = cv2.INTER_CUBIC  # По умолчанию
        if interp_option == "Ближайшая":
            interpolation = cv2.INTER_NEAREST
        elif interp_option == "Линейная":
            interpolation = cv2.INTER_LINEAR
            
        # Определяем координатную систему
        coord_system = determine_coordinate_system()
        print(f"Определена координатная система: {coord_system}")
        
        # Запрос количества потоков
        max_cpus = os.cpu_count() or 4
        faces_threads = Metashape.app.getInt("Введите количество потоков для обработки (1-{})".format(max_cpus), 
                                          min(6, max_cpus), 1, max_cpus)

# === Часть 8: Консольная обработка и главная функция ===
        # Начинаем обработку
        print(f"Начало обработки {len(spherical_cameras)} камер используя {faces_threads} потоков...")
        print(f"Настройки: перекрытие={overlap}, размер грани={selected_size}, система={coord_system}")
        print(f"Формат={file_format}, качество={quality}, интерполяция={interp_option}")
        
        start_time = time.time()
        processed_count = 0
        skipped_count = 0
        
        # Показываем информационное сообщение
        info_message = (f"Начало обработки {len(spherical_cameras)} камер.\n\n"
                       f"Настройки:\n"
                       f"- Перекрытие: {overlap} градусов\n"
                       f"- Размер грани: {selected_size}\n"
                       f"- Координатная система: {coord_system}\n"
                       f"- Формат файла: {file_format}\n"
                       f"- Качество: {quality}\n"
                       f"- Интерполяция: {interp_option}\n"
                       f"- Потоков: {faces_threads}\n\n"
                       f"Результаты будут сохранены в:\n{output_folder}")
        show_message("Информация", info_message)
        
        # Обработка камер
        for i, camera in enumerate(spherical_cameras):
            try:
                camera_label = camera.label
                spherical_image_path = camera.photo.path
                
                print(f"\n[{i+1}/{len(spherical_cameras)}] Обработка {camera_label}...")
                console_progress_bar(i + 1, len(spherical_cameras), 
                                    prefix='Общий прогресс:', 
                                    suffix=f'({i+1}/{len(spherical_cameras)})', 
                                    length=40)
                
                print(f"  Преобразование изображения используя {faces_threads} потоков...")
                
                # Преобразование сферического изображения в кубическую проекцию 
                # с параллельной обработкой граней
                image_paths = convert_spherical_to_cubemap(
                    spherical_image_path=spherical_image_path,
                    output_folder=output_folder,
                    camera_label=camera_label,
                    persp_size=persp_size,
                    overlap=overlap,
                    file_format=file_format,
                    quality=quality,
                    interpolation=interpolation,
                    max_workers=faces_threads
                )
                
                # Получаем фактический размер изображения (если был автоматический)
                actual_size = cv2.imread(list(image_paths.values())[0]).shape[0]
                print(f"  Добавление камер (размер грани: {actual_size}px)...")
                
                # Добавление новых камер для граней куба
                add_cubemap_cameras(
                    chunk=chunk,
                    spherical_camera=camera,
                    image_paths=image_paths,
                    persp_size=actual_size,
                    coord_system=coord_system
                )
                
                processed_count += 1
                print(f"  Успешно обработана камера {camera_label}")
                
                # Обновляем информацию о прогрессе
                elapsed_time = time.time() - start_time
                progress = (i + 1) / len(spherical_cameras) * 100
                remaining_time = elapsed_time / (i + 1) * (len(spherical_cameras) - i - 1)
                
                print(f"Прогресс: {progress:.1f}% | Прошло: {format_time(elapsed_time)} | Осталось: {format_time(remaining_time)}")
                
            except Exception as e:
                print(f"Ошибка при обработке камеры {camera.label}: {str(e)}")
                print(traceback.format_exc())
                skipped_count += 1
        
        # Завершение обработки
        total_time = time.time() - start_time
        
        # Показываем финальный отчет
        result_message = (f"Обработка завершена!\n\n"
                         f"Всего камер: {len(spherical_cameras)}\n"
                         f"Успешно обработано: {processed_count}\n"
                         f"Пропущено/ошибки: {skipped_count}\n"
                         f"Общее время: {format_time(total_time)}")
        show_message("Обработка завершена", result_message)
        
        print("\n==== Итоги обработки ====")
        print(f"Всего камер: {len(spherical_cameras)}")
        print(f"Успешно обработано: {processed_count}")
        print(f"Пропущено/ошибки: {skipped_count}")
        print(f"Общее время: {format_time(total_time)}")
        
    except Exception as e:
        error_message = f"Ошибка: {str(e)}\n\n{traceback.format_exc()}"
        print(error_message)
        try:
            show_message("Ошибка", f"Произошла ошибка при обработке:\n\n{str(e)}")
        except:
            print("Не удалось отобразить диалоговое окно с ошибкой.")

# === Глобальная переменная для хранения окна GUI ===
gui_window = None

# === Основная функция запуска ===
def main():
    """
    Главная функция для запуска из Metashape.
    Выбирает GUI или консольный режим в зависимости от доступности PyQt5.
    """
    global gui_window
    
    print("=== Конвертация сферических изображений в кубическую проекцию ===")
    print("Версия 1.0.0 - Оптимизированная с многопоточностью")
    
    # Проверяем возможность использования GUI
    if use_gui:
        try:
            # Инициализация QApplication
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            # Создание и отображение окна
            gui_window = CubemapConverterGUI()
            gui_window.show()
            
            # Запускаем главный цикл событий Qt
            print("Графический интерфейс запущен успешно")
            
            # Запрашиваем режим запуска
            try:
                non_blocking = Metashape.app.getBool("Запустить интерфейс в не блокирующем режиме?")
                print(f"Выбран {'не' if non_blocking else ''} блокирующий режим")
                
                if non_blocking:
                    # Для не блокирующего режима просто сохраняем окно в глобальной переменной
                    # Показываем сообщение об успешном запуске через 1 секунду
                    def show_success_message():
                        QMessageBox.information(None, "Информация", 
                                            "Интерфейс успешно запущен. Если вы видите это сообщение, то все работает корректно.")
                    QTimer.singleShot(1000, show_success_message)
                else:
                    # Для блокирующего режима запускаем цикл событий
                    print("Запуск цикла обработки событий Qt...")
                    app.exec_()
                    print("Цикл обработки событий Qt завершен")
            except:
                # Если запрос режима не работает, используем неблокирующий режим по умолчанию
                print("Не удалось запросить режим работы, используем неблокирующий режим.")
            
        except Exception as e:
            print(f"Ошибка инициализации GUI: {str(e)}")
            print(traceback.format_exc())
            print("Переключение в консольный режим.")
            process_images_console()
    else:
        # Запускаем консольный режим, если GUI недоступен
        process_images_console()

# Запуск скрипта
if __name__ == "__main__":
    main()