import os
import sys
import cv2
import numpy as np
import Metashape
from datetime import datetime
import concurrent.futures
import subprocess
import time


# === Проверка наличия OpenCV и установка ===
def check_and_install_opencv():
    """Проверяет наличие OpenCV и устанавливает её автоматически, если возможно."""
    try:
        import cv2
        return True
    except ImportError:
        print("OpenCV не найден. Попытка установки...")
        try:
            metashape_python = os.path.join(os.path.dirname(Metashape.app.applicationPath), "python", "python.exe")
            subprocess.check_call([metashape_python, "-m", "pip", "install", "opencv-python"])
            print("OpenCV успешно установлен.")
            return True
        except Exception as e:
            print(f"Не удалось установить OpenCV: {str(e)}")
            print("Пожалуйста, установите OpenCV вручную, выполнив следующую команду:")
            print(f'"{metashape_python}" -m pip install opencv-python')
            return False


if not check_and_install_opencv():
    exit(1)

import cv2  # Теперь можно безопасно импортировать OpenCV

def get_float_with_limits(prompt, default_value, min_value, max_value):
    """
    Запрашивает у пользователя число с проверкой диапазона.
    Parameters:
        prompt : str - Текстовое сообщение для пользователя
        default_value : float - Значение по умолчанию
        min_value : float - Минимальное допустимое значение
        max_value : float - Максимальное допустимое значение
    Returns:
        float - Введенное пользователем число
    """
    while True:
        value = Metashape.app.getFloat(prompt, default_value)
        if min_value <= value <= max_value:
            return value
        else:
            print(f"Ошибка: значение должно быть в диапазоне от {min_value} до {max_value}. Попробуйте снова.")

# === Функции для преобразования эквиректангулярной проекции ===

def eqruirect2persp_map(
                    img_shape,
                    FOV,
                    THETA,
                    PHI,
                    Hd,
                    Wd,
                    overlap=10  # Увеличили значение по умолчанию для более надежной стыковки
                    ):
    """
    Создает карты отображения для преобразования эквиректангулярной проекции в перспективную.
    
    Parameters:
    -----------
    img_shape : tuple
        Размеры исходного изображения (высота, ширина)
    FOV : float
        Поле зрения для перспективной проекции, в градусах
    THETA : float
        Угол поворота влево/вправо, в градусах
    PHI : float
        Угол вверх/вниз, в градусах
    Hd : int
        Высота результирующего изображения
    Wd : int
        Ширина результирующего изображения
    overlap : float
        Перекрытие в градусах (рекомендуется 10 для надежной стыковки)
    
    Returns:
    --------
    lon, lat : ndarray
        Карты отображения для функции cv2.remap
    """
    # THETA is left/right angle, PHI is up/down angle, both in degree
    equ_h, equ_w = img_shape

    equ_cx = (equ_w) / 2.0
    equ_cy = (equ_h) / 2.0

    # Увеличиваем FOV на величину перекрытия
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


def equirect2cubemap_map(
                        img_shape,
                        side=256,
                        dice=False
                        ):
    """
    Создает карты отображения для преобразования эквиректангулярной проекции в кубическую.
    
    Parameters:
    -----------
    img_shape : tuple
        Размеры исходного изображения (высота, ширина)
    side : int
        Размер грани куба
    dice : bool
        Если True, создает развертку куба в виде "костяшки домино"
    
    Returns:
    --------
    map_x, map_y : ndarray
        Карты отображения для функции cv2.remap
    """
    inShape = img_shape
    mesh = np.stack(
        np.meshgrid(
            np.linspace(-0.5, 0.5, num=side, dtype=np.float32),
            -np.linspace(-0.5, 0.5, num=side, dtype=np.float32),
        ),
        -1,
    )

    # Creating a matrix that contains x,y,z values of all 6 faces
    facesXYZ = np.zeros((side, side * 6, 3), np.float32)

    # Front face (z = 0.5)
    facesXYZ[:, 0 * side: 1 * side, [0, 1]] = mesh
    facesXYZ[:, 0 * side: 1 * side, 2] = 0.5

    # Right face (x = 0.5)
    facesXYZ[:, 1 * side: 2 * side, [2, 1]] = mesh
    facesXYZ[:, 1 * side: 2 * side, 0] = 0.5

    # Back face (z = -0.5)
    facesXYZ[:, 2 * side: 3 * side, [0, 1]] = mesh
    facesXYZ[:, 2 * side: 3 * side, 2] = -0.5

    # Left face (x = -0.5)
    facesXYZ[:, 3 * side: 4 * side, [2, 1]] = mesh
    facesXYZ[:, 3 * side: 4 * side, 0] = -0.5

    # Up face (y = 0.5)
    facesXYZ[:, 4 * side: 5 * side, [0, 2]] = mesh
    facesXYZ[:, 4 * side: 5 * side, 1] = 0.5

    # Down face (y = -0.5)
    facesXYZ[:, 5 * side: 6 * side, [0, 2]] = mesh
    facesXYZ[:, 5 * side: 6 * side, 1] = -0.5

    # Calculating the spherical coordinates phi and theta for given XYZ
    # coordinate of a cube face
    x, y, z = np.split(facesXYZ, 3, axis=-1)
    # phi = tan^-1(x/z)
    phi = np.arctan2(x, z)
    # theta = tan^-1(y/||(x,y)||)
    theta = np.arctan2(y, np.sqrt(x ** 2 + z ** 2))

    h, w = inShape
    # Calculating corresponding coordinate points in
    # the equirectangular image
    eqrec_x = (phi / (2 * np.pi) + 0.5) * w
    eqrec_y = (-theta / np.pi + 0.5) * h
    # Note: we have considered equirectangular image to
    # be mapped to a normalised form and then to the scale of (pi,2pi)

    map_x = eqrec_x
    map_y = eqrec_y
    
    if dice:
        dice_map_x = np.zeros((side * 3, side * 4), dtype='float32')
        dice_map_y = np.zeros((side * 3, side * 4), dtype='float32')
        dice_map_x[:side, side:side*2] = cv2.flip(map_x[:, 4 * side : 5 * side, 0], 0)
        dice_map_y[:side, side:side*2] = map_y[:, 4 * side : 5 * side, 0]

        dice_map_x[side:side*2, :side] = map_x[:, 3 * side: 4 * side, 0]
        dice_map_y[side:side*2, :side] = map_y[:, 3 * side: 4 * side, 0]

        dice_map_x[side:side*2, side:side*2] = map_x[:, :side, 0]
        dice_map_y[side:side*2, side:side*2] = map_y[:, :side, 0]

        dice_map_x[side:side*2, side*2:side*3] = cv2.flip(map_x[:, side:2*side,0],1)
        dice_map_y[side:side*2, side*2:side*3] = map_y[:, side:2*side,0]

        dice_map_x[side:side*2, side*3:] = cv2.flip(map_x[:, 2 * side: 3 * side, 0], 1)
        dice_map_y[side:side*2, side*3:] = map_y[:, 2 * side: 3 * side, 0]

        dice_map_x[side*2:, side:side*2] = map_x[:, 5 * side: 6 * side, 0]
        dice_map_y[side*2:, side:side*2] = map_y[:, 5 * side: 6 * side, 0]
        return dice_map_x, dice_map_y
    else:
        return map_x, map_y

def cubemap2equirect_map(img_size, outShape):
    """
    Создает карты отображения для преобразования кубической проекции в эквиректангулярную.
    
    Parameters:
    -----------
    img_size : int
        Размер грани куба
    outShape : tuple
        Размеры результирующего изображения (высота, ширина)
    
    Returns:
    --------
    map_x, map_y : ndarray
        Карты отображения для функции cv2.remap
    """
    h = outShape[0]
    w = outShape[1]
    face_w = img_size

    phi = np.linspace(-np.pi, np.pi, num=outShape[1], dtype=np.float32)
    theta = np.linspace(np.pi, -np.pi, num=outShape[0], dtype=np.float32) / 2

    phi, theta = np.meshgrid(phi, theta)

    tp = np.zeros((h, w), dtype=np.int32)
    tp[:, : w // 8] = 2
    tp[:, w // 8: 3 * w // 8] = 3
    tp[:, 3 * w // 8: 5 * w // 8] = 0
    tp[:, 5 * w // 8: 7 * w // 8] = 1
    tp[:, 7 * w // 8:] = 2

    # Prepare ceil mask
    mask = np.zeros((h, w // 4), np.bool)
    idx = np.linspace(-np.pi, np.pi, w // 4) / 4
    idx = h // 2 - np.round(np.arctan(np.cos(idx)) * h / np.pi).astype(int)
    for i, j in enumerate(idx):
        mask[:j, i] = 1

    mask = np.roll(mask, w // 8, 1)

    mask = np.concatenate([mask] * 4, 1)

    tp[mask] = 4
    tp[np.flip(mask, 0)] = 5

    tp = tp.astype(np.int32)

    coor_x = np.zeros((h, w))
    coor_y = np.zeros((h, w))

    for i in range(4):
        mask = tp == i
        coor_x[mask] = 0.5 * np.tan(phi[mask] - np.pi * i / 2)
        coor_y[mask] = (
            -0.5 * np.tan(theta[mask]) / np.cos(phi[mask] - np.pi * i / 2)
        )

    mask = tp == 4
    c = 0.5 * np.tan(np.pi / 2 - theta[mask])
    coor_x[mask] = c * np.sin(phi[mask])
    coor_y[mask] = c * np.cos(phi[mask])

    mask = tp == 5
    c = 0.5 * np.tan(np.pi / 2 - np.abs(theta[mask]))
    coor_x[mask] = c * np.sin(phi[mask])
    coor_y[mask] = -c * np.cos(phi[mask])  # Обратите внимание на отрицательный знак
    # Final renormalize
    coor_x = (np.clip(coor_x, -0.5, 0.5) + 0.5) * face_w
    coor_y = (np.clip(coor_y, -0.5, 0.5) + 0.5) * face_w

    map_x = coor_x.astype(np.float32)
    map_y = coor_y.astype(np.float32)

    return map_x, map_y

def verify_cubemap_edges(image_paths, tolerance=0.8):
    """
    Проверяет стыковку граней кубической проекции.
    
    Parameters:
    -----------
    image_paths : dict
        Словарь с путями к изображениям граней куба
    tolerance : float
        Порог схожести для определения корректности стыковки (0-1)
    
    Returns:
    --------
    bool, dict
        Результат проверки и словарь с метриками схожести для каждой пары граней
    """
    pairs = [
        ("front", "right"),
        ("front", "left"),
        ("front", "top"),
        ("front", "down"),
        ("back", "right"),
        ("back", "left"),
        ("back", "top"),
        ("back", "down"),
        ("right", "top"),
        ("right", "down"),
        ("left", "top"),
        ("left", "down")
    ]
    
    # Загрузка всех изображений
    images = {}
    for face, path in image_paths.items():
        img = cv2.imread(path)
        if img is None:
            print(f"Не удалось загрузить изображение: {path}")
            continue
        images[face] = img
    
    results = {}
    overall_success = True
    
    for face1, face2 in pairs:
        if face1 not in images or face2 not in images:
            continue
            
        # Определяем, какие края сравнивать
        img1 = images[face1]
        img2 = images[face2]
        h, w = img1.shape[:2]
        
        # Определяем края для сравнения (упрощенно)
        border_width = int(w * 0.05)  # Берем 5% от ширины для проверки края
        
        # Здесь должна быть логика определения, какие именно края сравнивать
        # Для примера сравниваем правый край первого изображения с левым краем второго
        edge1 = img1[:, -border_width:]
        edge2 = img2[:, :border_width]
        
        # Масштабируем до одинакового размера, если нужно
        if edge1.shape != edge2.shape:
            edge2 = cv2.resize(edge2, (edge1.shape[1], edge1.shape[0]))
        
        # Вычисляем метрику сходства (MSE - среднеквадратичная ошибка)
        mse = np.mean((edge1.astype(np.float32) - edge2.astype(np.float32)) ** 2)
        max_possible_mse = 255.0 ** 2  # Максимально возможная MSE для 8-битного изображения
        similarity = 1.0 - (mse / max_possible_mse)
        
        results[(face1, face2)] = similarity
        if similarity < tolerance:
            overall_success = False
    
    return overall_success, results

def determine_coordinate_system():
    """
    Определяет тип координатной системы на основе анализа положения камер.
    Returns:
        str - Тип координатной системы: "Y_UP", "Z_UP" или "X_UP"
    """
    doc = Metashape.app.document
    chunk = doc.chunk
    cameras = [cam for cam in chunk.cameras if cam.transform]

    if not cameras:
        return "Y_UP"  # По умолчанию

    orientation_votes = {"Y_UP": 0, "Z_UP": 0, "X_UP": 0}

    for camera in cameras[:3]:  # Анализируем только первые 3 камеры
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
    if orientation_votes[determined_orientation] / sum(orientation_votes.values()) > 0.7:
        print(f"Определена координатная система: {determined_orientation} (уверенность высокая)")
    else:
        print(f"Определена координатная система: {determined_orientation} (уверенность низкая)")

    return determined_orientation        
    
def convert_spherical_to_cubemap(spherical_image_path, output_folder, camera_label, persp_size=1024, overlap=10):
    """
    Конвертирует сферическое изображение в кубическую проекцию.
    Parameters:
        spherical_image_path : str - Путь к сферическому изображению
        output_folder : str - Папка для сохранения выходных изображений
        camera_label : str - Метка камеры
        persp_size : int - Размер граней куба
        overlap : float - Перекрытие между гранями в градусах
    Returns:
        dict - Словарь с путями к созданным граням куба
    """
    spherical_image = cv2.imread(spherical_image_path)
    if spherical_image is None:
        raise ValueError(f"Не удалось загрузить изображение: {spherical_image_path}")

    equirect_height, equirect_width = spherical_image.shape[:2]

    faces_params = {
        "front": {"fov": 90, "theta": 0, "phi": 0},
        "right": {"fov": 90, "theta": 90, "phi": 0},
        "left": {"fov": 90, "theta": -90, "phi": 0},
        "top": {"fov": 90, "theta": 0, "phi": 90},
        "down": {"fov": 90, "theta": 0, "phi": -90},
        "back": {"fov": 90, "theta": 180, "phi": 0},
    }

    image_paths = {}

    for face_name, params in faces_params.items():
        map_x, map_y = eqruirect2persp_map(
            img_shape=(equirect_height, equirect_width),
            FOV=params["fov"],
            THETA=params["theta"],
            PHI=params["phi"],
            Hd=persp_size,
            Wd=persp_size,
            overlap=overlap
        )

        perspective_image = cv2.remap(spherical_image, map_x, map_y, interpolation=cv2.INTER_LINEAR)

        output_filename = f"{camera_label}_{face_name}.jpg"
        output_path = os.path.join(output_folder, output_filename)
        cv2.imwrite(output_path, perspective_image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        image_paths[face_name] = output_path

    is_seamless, edge_metrics = verify_cubemap_edges(image_paths)
    if not is_seamless:
        print(f"Предупреждение: возможны проблемы со стыковкой граней для камеры {camera_label}")

    return image_paths


# === Добавление камер для граней куба ===
def add_cubemap_cameras(chunk, spherical_camera, image_paths, persp_size, coord_system="Y_UP"):
    """
    Добавляет камеры для граней куба на основе позиции сферической камеры.
    Учитывает тип координатной системы.
    
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

    # Словарь с направлениями для каждой грани куба
    # Изменена конфигурация для более точного позиционирования
    
    # Для системы Y_UP, где:
    # Y - вверх
    # Z - вперед
    # X - вправо
    if coord_system == "Y_UP":
        cubemap_directions = {
            "front": {"forward": [0, 0, 1], "up": [0, 1, 0]},     # Смотрит вперед
            "right": {"forward": [1, 0, 0], "up": [0, 1, 0]},     # Смотрит вправо
            "left": {"forward": [-1, 0, 0], "up": [0, 1, 0]},     # Смотрит влево
            "top": {"forward": [0, 1, 0], "up": [0, 0, -1]},      # Смотрит вверх
            "down": {"forward": [0, -1, 0], "up": [0, 0, 1]},     # Смотрит вниз
            "back": {"forward": [0, 0, -1], "up": [0, 1, 0]},     # Смотрит назад
        }
    # Для системы Z_UP, где:
    # Z - вверх
    # X - вперед
    # Y - вправо
    elif coord_system == "Z_UP":
        cubemap_directions = {
            "front": {"forward": [1, 0, 0], "up": [0, 0, 1]},     # Смотрит вперед
            "right": {"forward": [0, 1, 0], "up": [0, 0, 1]},     # Смотрит вправо
            "left": {"forward": [0, -1, 0], "up": [0, 0, 1]},     # Смотрит влево
            "top": {"forward": [0, 0, 1], "up": [-1, 0, 0]},      # Смотрит вверх
            "down": {"forward": [0, 0, -1], "up": [1, 0, 0]},     # Смотрит вниз
            "back": {"forward": [-1, 0, 0], "up": [0, 0, 1]},     # Смотрит назад
        }
    # Для системы X_UP, где:
    # X - вверх
    # Y - вперед
    # Z - вправо
    elif coord_system == "X_UP":
        cubemap_directions = {
            "front": {"forward": [0, 1, 0], "up": [1, 0, 0]},     # Смотрит вперед
            "right": {"forward": [0, 0, 1], "up": [1, 0, 0]},     # Смотрит вправо
            "left": {"forward": [0, 0, -1], "up": [1, 0, 0]},     # Смотрит влево
            "top": {"forward": [1, 0, 0], "up": [0, -1, 0]},      # Смотрит вверх
            "down": {"forward": [-1, 0, 0], "up": [0, 1, 0]},     # Смотрит вниз
            "back": {"forward": [0, -1, 0], "up": [1, 0, 0]},     # Смотрит назад
        }
    # Для любой другой системы, используем стандартные настройки Y_UP
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
        """
        Создает матрицу вращения на основе векторов forward и up,
        учитывая базовую ориентацию сферической камеры.
        
        Parameters:
        -----------
        forward : list
            Вектор направления "вперед"
        up : list
            Вектор направления "вверх"
        base_rotation_4x4 : Metashape.Matrix
            Базовая матрица вращения сферической камеры (4x4)
        
        Returns:
        --------
        Metashape.Matrix
            Результирующая матрица вращения
        """
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
        # Создаем новую камеру
        camera = chunk.addCamera()
        camera.label = f"{spherical_camera.label}_{face_name}"
        
        # Копируем или создаем новый сенсор
        # Если у нас есть сенсор для перспективных камер, используем его
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
        sensor.type = Metashape.Sensor.Type.Frame  # Указываем тип сенсора как Frame (плоский)
        sensor.width = persp_size
        sensor.height = persp_size

        # Устанавливаем фокусное расстояние для поля зрения 90 градусов
        # Для FOV = 90 градусов: f = (w/2) / tan(FOV/2)
        focal_length = persp_size / (2 * np.tan(np.radians(90 / 2)))
        sensor.focal_length = focal_length
        sensor.pixel_width = 1  # Размер пикселя в мм
        sensor.pixel_height = 1

        # Устанавливаем матрицу внутренних параметров камеры
        calibration = sensor.calibration
        calibration.f = focal_length  # Фокусное расстояние
        calibration.cx = persp_size / 2  # Центр изображения (по X)
        calibration.cy = persp_size / 2  # Центр изображения (по Y)
        calibration.k1 = 0  # Обнуляем коэффициенты дисторсии
        calibration.k2 = 0
        calibration.k3 = 0
        calibration.p1 = 0
        calibration.p2 = 0

        # Устанавливаем позицию камеры - используем позицию сферической камеры
        camera.transform = Metashape.Matrix.Translation(position)

        # Устанавливаем ориентацию камеры
        forward = directions["forward"]
        up = directions["up"]

        # Создаем матрицу вращения с правильным аргументом
        rotation_matrix = create_rotation_matrix(forward, up, base_rotation_4x4)

        # Применяем вращение
        camera.transform = camera.transform * rotation_matrix

        # Создаем объект Photo для камеры
        camera.photo = Metashape.Photo()

        # Загружаем изображение
        if face_name in image_paths:
            camera.photo.path = image_paths[face_name]
        else:
            print(f"Ошибка: изображение для грани {face_name} не найдено")
            continue

        # Проверяем, существует ли файл изображения
        if not os.path.exists(camera.photo.path):
            print(f"Ошибка: файл изображения не найден: {camera.photo.path}")
            continue

        # Обновляем метаданные
        camera.meta['Image/Width'] = str(persp_size)
        camera.meta['Image/Height'] = str(persp_size)
        camera.meta['Image/Orientation'] = "1"  # 1 = нормальная ориентация
    
    return cameras_created
    
def process_camera(camera, output_folder, equirect_width, equirect_height, persp_size, overlap, coord_system):
    """
    Обрабатывает одну камеру: преобразует её изображение в кубическую проекцию и добавляет новые камеры.
    Parameters:
        camera : Metashape.Camera - Камера для обработки
        output_folder : str - Папка для сохранения выходных изображений
        equirect_width : int - Ширина исходного сферического изображения
        equirect_height : int - Высота исходного сферического изображения
        persp_size : int - Размер граней кубической проекции
        overlap : float - Перекрытие между гранями в градусах
        coord_system : str - Тип координатной системы
    Returns:
        tuple - (camera_label, success, error_message, faces_created)
    """
    try:
        camera_label = camera.label
        spherical_image_path = camera.photo.path

        # Преобразование сферического изображения в кубическую проекцию
        image_paths = convert_spherical_to_cubemap(
            spherical_image_path=spherical_image_path,
            output_folder=output_folder,
            camera_label=camera_label,
            persp_size=persp_size,
            overlap=overlap
        )

        # Добавление новых камер для граней куба
        chunk = Metashape.app.document.chunk
        add_cubemap_cameras(
            chunk=chunk,
            spherical_camera=camera,
            image_paths=image_paths,
            persp_size=persp_size,
            coord_system=coord_system
        )

        return camera_label, True, None, len(image_paths)

    except Exception as e:
        return camera_label, False, str(e), 0


def process_images(output_folder=None, overlap=None):
    """
    Обрабатывает все сферические изображения и добавляет их как кубические грани в проект Metashape.
    Parameters:
        output_folder : str - Путь к выходной папке (если None, запрашивается у пользователя)
        overlap : float - Значение перекрытия (если None, запрашивается у пользователя)
    """
    if not output_folder:
        output_folder = Metashape.app.getExistingDirectory("Выберите папку для сохранения изображений")
        if not output_folder:
            print("Ошибка: путь для сохранения не выбран.")
            return

    # Получение значения перекрытия
    if overlap is None:
        overlap = get_float_with_limits(
            prompt="Введите значение перекрытия (0-20)",
            default_value=10,
            min_value=0,
            max_value=20
        )

    doc = Metashape.app.document
    chunk = doc.chunk

    if not chunk:
        print("Ошибка: активный чанк не найден.")
        return

    coord_system = determine_coordinate_system()
    print(f"Выбрана координатная система: {coord_system}")

    spherical_cameras = [cam for cam in chunk.cameras if cam.transform and cam.photo]

    if not spherical_cameras:
        print("Ошибка: нет доступных сферических камер для обработки.")
        return

    total_cameras = len(spherical_cameras)
    print(f"Начинаем обработку {total_cameras} камер...")

    # Определяем размеры сферического изображения
    example_image = cv2.imread(spherical_cameras[0].photo.path)
    if example_image is None:
        print("Ошибка: не удалось загрузить примерное изображение для определения размеров.")
        return

    equirect_height, equirect_width = example_image.shape[:2]
    persp_size = min(equirect_width, equirect_height) // 2  # Размер грани куба

    print(f"Параметры: размер грани={persp_size}px, перекрытие={overlap}°")

    # Время начала обработки
    start_time = time.time()

    # Многопоточная обработка камер
    processed_count = 0
    skipped_count = 0

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for camera in spherical_cameras:
            futures.append(executor.submit(
                process_camera,
                camera=camera,
                output_folder=output_folder,
                equirect_width=equirect_width,
                equirect_height=equirect_height,
                persp_size=persp_size,
                overlap=overlap,
                coord_system=coord_system
            ))

        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            camera_label, success, error_message, faces_created = future.result()
            if success:
                processed_count += 1
                print(f"[{i + 1}/{total_cameras}] Камера {camera_label} успешно обработана. Создано {faces_created} кубических камер.")
            else:
                skipped_count += 1
                print(f"[{i + 1}/{total_cameras}] Ошибка при обработке камеры {camera_label}: {error_message}")

            # Вывод прогресса
            progress = (i + 1) / total_cameras * 100
            elapsed_time = time.time() - start_time
            estimated_total = elapsed_time / (i + 1) * total_cameras
            remaining_time = estimated_total - elapsed_time
            print(f"Прогресс: {progress:.1f}% | Прошло: {format_time(elapsed_time)} | Осталось: {format_time(remaining_time)}")

    # Итоговая статистика
    total_time = time.time() - start_time
    print("==== Итоги обработки ====")
    print(f"Всего камер: {total_cameras}")
    print(f"Успешно обработано: {processed_count}")
    print(f"Пропущено/ошибки: {skipped_count}")
    print(f"Общее время: {format_time(total_time)}")


def format_time(seconds):
    """Форматирует время в удобочитаемый вид."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours}ч {minutes}м {seconds}с"


# === Точка входа ===
if __name__ == "__main__":
    print("=== Конвертация сферических изображений в кубическую проекцию ===")
    process_images()