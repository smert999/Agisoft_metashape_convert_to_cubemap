# === Часть 1: Импорты и вспомогательные функции ===
import os
import sys
import time
import traceback
import Metashape
import subprocess
import concurrent.futures
import locale
import json
import datetime # Добавляем импорт datetime

# === Новая функция логирования ===
def log_message(message):
    """Простая функция логирования с меткой времени."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} {message}")

# Добавляем отладочные сообщения
log_message("Запуск скрипта...") # Используем новую функцию
log_message(f"Версия Python: {sys.version}") # Используем новую функцию
log_message(f"Путь к Metashape: {os.path.dirname(sys.executable)}") # Используем новую функцию

# Глобальная переменная для хранения GUI окна
gui_window = None

# Глобальная переменная для хранения текущего языка (БОЛЬШЕ НЕ НУЖНА В ТАКОМ ВИДЕ)
# current_language = "ru"  # По умолчанию русский - БОЛЬШЕ НЕ ИСПОЛЬЗУЕТСЯ

# Глобальная переменная для хранения текущего языка
LANG = 'en'  # Инициализируем английским по умолчанию

# Словарь переводов для интерфейса
translations = {
    "ru": {},  # Будет заполнен ниже
    "en": {}   # Будет заполнен ниже
}

# Функция для локализации строк
def _(text_key):
    """
    Возвращает локализованную строку по ключу, используя глобальную переменную LANG.
    """
    # Используем глобальную переменную LANG
    # global LANG # Больше не нужно объявлять global, если только читаем
    # Возвращаем перевод для текущего языка LANG, или ключ, если перевод не найден
    return translations.get(LANG, translations.get('en', {})).get(text_key, text_key)

# Заполняем словари переводов
translations["ru"] = {
    "script_title": "Конвертация сферических изображений в кубическую проекцию",
    "version": "Версия",
    "optimized": "Оптимизированная с многопоточностью",
    "starting_script": "Запуск скрипта...",
    "python_version": "Версия Python",
    "metashape_path": "Путь к Metashape",
    "checking_libraries": "Начало проверки необходимых библиотек...",
    "library_installed": "Библиотека {0} уже установлена.",
    "library_not_found": "Библиотека {0} не найдена.",
    "pyqt5_installed": "PyQt5 полностью установлен и работает.",
    "pyqt5_problem": "Проблема с PyQt5: {0}",
    "missing_libraries": "Отсутствуют необходимые библиотеки: {0}",
    "python_path": "Путь к Python: {0}",
    "error_python_not_found": "ОШИБКА: Python не найден по пути {0}",
    "updating_pip": "Обновление pip...",
    "pip_update_result": "Результат обновления pip: {0}",
    "output": "Вывод: {0}",
    "errors": "Ошибки: {0}",
    "warning_pip_update_failed": "Предупреждение: не удалось обновить pip: {0}",
    "removing_pyqt5": "Удаление существующих установок PyQt5...",
    "error_removing_pyqt5": "Ошибка при удалении PyQt5: {0}",
    "installing": "Установка {0}...",
    "installation_result": "Результат установки {0}: {1}",
    "return_code": "Код возврата: {0}",
    "package_installed": "Пакет {0} успешно установлен.",
    "failed_to_install": "Не удалось установить {0}: {1}",
    "alternative_method": "Попытка использовать альтернативный метод установки...",
    "alt_install_result": "Результат альтернативной установки {0}: {1}",
    "alt_install_success": "Пакет {0} успешно установлен через альтернативный репозиторий.",
    "alt_install_failed": "Не удалось установить {0} альтернативным методом: {1}",
    "all_libraries_installed": "Все необходимые библиотеки успешно установлены.",
    "removing_module": "Удаление {0} из sys.modules для перезагрузки",
    "checking_pyqt5": "Проверка импорта PyQt5 после установки...",
    "pyqt5_after_install": "PyQt5 успешно установлен и работает после установки.",
    "pyqt5_not_working": "PyQt5 не работает после установки: {0}",
    "continue_console": "Продолжаем в консольном режиме.",
    "failed_libraries": "Не удалось установить библиотеки: {0}",
    "script_continue": "Скрипт продолжит работу в консольном режиме.",
    "checking_installing": "Проверка и установка необходимых библиотек...",
    "package_install_result": "Результат установки пакетов: {0}",
    "trying_import_opencv": "Попытка импорта OpenCV...",
    "opencv_imported": "OpenCV успешно импортирован, версия: {0}",
    "failed_import_opencv": "Не удалось импортировать OpenCV: {0}",
    "script_cant_work": "Скрипт не может работать без OpenCV.",
    "press_enter": "Нажмите Enter для завершения...",
    "checking_pyqt5_availability": "Проверка доступности PyQt5...",
    "pyqt5_available": "PyQt5 доступен, будет использован графический интерфейс.",
    "pyqt5_unavailable": "PyQt5 недоступен: {0}. Скрипт будет работать в консольном режиме.",
    "importing_pyqt5": "Импорт компонентов PyQt5...",
    "pyqt5_components_imported": "PyQt5 компоненты успешно импортированы.",
    "failed_import_pyqt5_components": "Не удалось импортировать компоненты PyQt5: {0}",
    "script_continue_console": "Скрипт продолжит работу в консольном режиме.",
    "script_first_part_loaded": "Первая часть скрипта успешно загружена.",
    "critical_error": "КРИТИЧЕСКАЯ ОШИБКА",
    "unexpected_error": "Произошла непредвиденная ошибка: {0}",
    "setup_locale": "Настройка системной локали и кодировок...",
    "system_locale": "Системная локаль: {0}",
    "locale_set": "Установлена локаль: {0}",
    "failed_set_locale": "Не удалось установить локаль: {0}",
    "fs_encoding": "Кодировка файловой системы: {0}",
    "console_encoding": "Кодировка консоли: {0}",
    "stdout_reconfigured": "Перенастроен stdout/stderr на UTF-8",
    "locale_warning": "Предупреждение при настройке локали: {0}",
    "showing_message": "Показ сообщения: {0}",
    "error_showing_message": "Ошибка показа сообщения: {0}",
    "option_request": "Запрос выбора опции: {0}",
    "option_variants": "Варианты: {0}",
    "user_selected_index": "Пользователь выбрал индекс: {0}",
    "error_using_getInt": "Ошибка при использовании getInt: {0}",
    "getString_result": "Результат getString: {0}",
    "error_using_getString": "Ошибка при использовании getString: {0}",
    "simple_getString_result": "Результат простого getString: {0}",
    "critical_input_error": "Критическая ошибка при получении ввода: {0}",
    "time_format_hours": "ч",
    "time_format_minutes": "мин",
    "time_format_seconds": "сек",
    "metashape_methods_modified": "Методы Metashape для работы с файлами модифицированы для поддержки кириллицы.",
    "failed_modify_metashape": "Не удалось модифицировать методы Metashape: {0}",
    "detected_system_language": "Определен язык системы: {0}",
    "error_detecting_language": "Ошибка при определении языка системы: {0}",
    "path_normalization_warning": "Предупреждение при нормализации пути: {0}",
    "path_processing_error": "Ошибка при обработке пути: {0}",
    "select_faces_title": "Выбор граней куба",
    "select_faces_label": "Выберите грани для генерации:",
    "face_front": "Передняя грань (front)",
    "face_right": "Правая грань (right)",
    "face_left": "Левая грань (left)",
    "face_top": "Верхняя грань (top)",
    "face_down": "Нижняя грань (down)",
    "face_back": "Задняя грань (back)",
    "selected_faces": "Выбранные грани: {0}",
    "no_faces_selected": "Не выбрано ни одной грани. Будут созданы все грани.",
    "post_processing_group": "Обработка после конвертации",
    "realign_cameras": "Повторно выровнять камеры после создания",
    "remove_spherical": "Удалить исходные сферические камеры",
    "realigning_cameras": "Выполняется повторное выравнивание камер...",
    "removing_spherical": "Удаление исходных сферических камер...",
    "align_completed": "Выравнивание камер завершено",
    "remove_completed": "Удаление исходных сферических камер завершено",
    "select_at_least_one": "Выберите хотя бы одну грань для генерации",
    "processing_camera": "Обработка камеры {} ({}/{})",
    "adding_cube_cameras": "Добавление кубических камер",
    "camera_processed": "Камера {} успешно обработана",
    "camera_added_status": "Камеры для {} добавлены",
    "skipped_no_faces": "Пропущено (нет граней): {}",
    "processing_error": "Ошибка при обработке камеры {}: {}",
    "realigning_cameras": "Повторное выравнивание камер...",
    "removing_spherical": "Удаление сферических камер...",
    "processing_stats": "Обработано: {}/{}, Пропущено: {}",
    "elapsed_time": "Затраченное время: {}",
    "general_processing_error": "Общая ошибка обработки: {}",
    "processing_aborted": "Обработка прервана пользователем.",
    "gui_thread_starting": "Поток обработки GUI запущен.",
    "gui_thread_finished": "Поток обработки GUI завершен.",
    "gui_thread_error": "Ошибка в потоке обработки GUI: {}",
    "conversion_stage": "Конвертация",
    "adding_cube_cameras_stage": "Добавление камер {} ({}/{})",
    "conversion_error": "Ошибка конвертации {}: {}",
    "add_camera_error": "Ошибка добавления камер {}: {}",
    "conversion_error_status": "Ошибка конвертации: {}",
    "add_camera_error_status": "Ошибка добавления камер: {}",
    "realign_error": "Ошибка выравнивания: {}",
    "remove_spherical_error": "Ошибка удаления сфер. камер: {}",
    "processing_finished_status": "Обработка завершена",
    "project_save_error": "Ошибка сохранения проекта: {0}",
    "project_save_error_unexpected": "Непредвиденная ошибка при сохранении проекта: {0}",
    "select_threads": "Количество потоков для граней (рекомендуется {0}):", # Renamed
    "invalid_threads": "Некорректный ввод. Используется {0} потоков для граней.", # Updated message
    "select_camera_threads": "Количество потоков для камер (рекомендуется {0}):", # New
    "invalid_camera_threads": "Некорректный ввод. Используется {0} потоков для камер.", # New
}

translations["en"] = {
    "script_title": "Spherical to Cubemap Image Conversion",
    "version": "Version",
    "optimized": "Optimized with multithreading",
    "starting_script": "Starting script...",
    "python_version": "Python version",
    "metashape_path": "Metashape path",
    "checking_libraries": "Starting checking required libraries...",
    "library_installed": "Library {0} is already installed.",
    "library_not_found": "Library {0} not found.",
    "pyqt5_installed": "PyQt5 is fully installed and working.",
    "pyqt5_problem": "Problem with PyQt5: {0}",
    "missing_libraries": "Missing required libraries: {0}",
    "python_path": "Python path: {0}",
    "error_python_not_found": "ERROR: Python not found at path {0}",
    "updating_pip": "Updating pip...",
    "pip_update_result": "Pip update result: {0}",
    "output": "Output: {0}",
    "errors": "Errors: {0}",
    "warning_pip_update_failed": "Warning: failed to update pip: {0}",
    "removing_pyqt5": "Removing existing PyQt5 installations...",
    "error_removing_pyqt5": "Error removing PyQt5: {0}",
    "installing": "Installing {0}...",
    "installation_result": "Installation result for {0}: {1}",
    "return_code": "Return code: {0}",
    "package_installed": "Package {0} successfully installed.",
    "failed_to_install": "Failed to install {0}: {1}",
    "alternative_method": "Trying alternative installation method...",
    "alt_install_result": "Alternative installation result for {0}: {1}",
    "alt_install_success": "Package {0} successfully installed via alternative repository.",
    "alt_install_failed": "Failed to install {0} via alternative method: {1}",
    "all_libraries_installed": "All required libraries successfully installed.",
    "removing_module": "Removing {0} from sys.modules for reload",
    "checking_pyqt5": "Checking PyQt5 import after installation...",
    "pyqt5_after_install": "PyQt5 successfully installed and working after installation.",
    "pyqt5_not_working": "PyQt5 not working after installation: {0}",
    "continue_console": "Continuing in console mode.",
    "failed_libraries": "Failed to install libraries: {0}",
    "script_continue": "Script will continue in console mode.",
    "checking_installing": "Checking and installing required libraries...",
    "package_install_result": "Package installation result: {0}",
    "trying_import_opencv": "Trying to import OpenCV...",
    "opencv_imported": "OpenCV successfully imported, version: {0}",
    "failed_import_opencv": "Failed to import OpenCV: {0}",
    "script_cant_work": "Script cannot work without OpenCV.",
    "press_enter": "Press Enter to exit...",
    "checking_pyqt5_availability": "Checking PyQt5 availability...",
    "pyqt5_available": "PyQt5 available, graphical interface will be used.",
    "pyqt5_unavailable": "PyQt5 unavailable: {0}. Script will work in console mode.",
    "importing_pyqt5": "Importing PyQt5 components...",
    "pyqt5_components_imported": "PyQt5 components successfully imported.",
    "failed_import_pyqt5_components": "Failed to import PyQt5 components: {0}",
    "script_continue_console": "Script will continue in console mode.",
    "script_first_part_loaded": "First part of the script successfully loaded.",
    "critical_error": "CRITICAL ERROR",
    "unexpected_error": "An unexpected error occurred: {0}",
    "setup_locale": "Setting up system locale and encodings...",
    "system_locale": "System locale: {0}",
    "locale_set": "Locale set: {0}",
    "failed_set_locale": "Failed to set locale: {0}",
    "fs_encoding": "Filesystem encoding: {0}",
    "console_encoding": "Console encoding: {0}",
    "stdout_reconfigured": "Reconfigured stdout/stderr to UTF-8",
    "locale_warning": "Warning during locale setup: {0}",
    "showing_message": "Showing message: {0}",
    "error_showing_message": "Error showing message: {0}",
    "option_request": "Option selection request: {0}",
    "option_variants": "Options: {0}",
    "user_selected_index": "User selected index: {0}",
    "error_using_getInt": "Error using getInt: {0}",
    "getString_result": "getString result: {0}",
    "error_using_getString": "Error using getString: {0}",
    "simple_getString_result": "Simple getString result: {0}",
    "critical_input_error": "Critical error getting input: {0}",
    "time_format_hours": "h",
    "time_format_minutes": "min",
    "time_format_seconds": "sec",
    "metashape_methods_modified": "Metashape file handling methods modified to support Cyrillic.",
    "failed_modify_metashape": "Failed to modify Metashape methods: {0}",
    "detected_system_language": "Detected system language: {0}",
    "error_detecting_language": "Error detecting system language: {0}",
    "path_normalization_warning": "Warning during path normalization: {0}",
    "path_processing_error": "Error processing path: {0}",
    "select_faces_title": "Cube Face Selection",
    "select_faces_label": "Select faces to generate:",
    "face_front": "Front face",
    "face_right": "Right face",
    "face_left": "Left face",
    "face_top": "Top face",
    "face_down": "Bottom face (down)",
    "face_back": "Back face",
    "selected_faces": "Selected faces: {0}",
    "no_faces_selected": "No faces selected. All faces will be created.",
    "post_processing_group": "Post-conversion Processing",
    "realign_cameras": "Realign cameras after creation",
    "remove_spherical": "Remove original spherical cameras",
    "realigning_cameras": "Realigning cameras...",
    "removing_spherical": "Removing original spherical cameras...",
    "align_completed": "Camera alignment completed",
    "remove_completed": "Original spherical cameras removal completed",
    "select_at_least_one": "Select at least one face to generate",
    "processing_camera": "Processing camera {} ({}/{})",
    "adding_cube_cameras": "Adding cubemap cameras",
    "camera_processed": "Camera {} processed successfully",
    "camera_added_status": "Cameras added for {}",
    "skipped_no_faces": "Skipped (no faces): {}",
    "processing_error": "Error processing camera {}: {}",
    "realigning_cameras": "Realigning cameras...",
    "removing_spherical": "Removing spherical cameras...",
    "processing_stats": "Processed: {}/{}, Skipped: {}",
    "elapsed_time": "Elapsed time: {}",
    "general_processing_error": "General processing error: {}",
    "processing_aborted": "Processing aborted by user.",
    "gui_thread_starting": "GUI processing thread started.",
    "gui_thread_finished": "GUI processing thread finished.",
    "gui_thread_error": "Error in GUI processing thread: {}",
    "conversion_stage": "Conversion",
    "adding_cube_cameras_stage": "Adding cameras {} ({}/{})",
    "conversion_error": "Conversion error {}: {}",
    "add_camera_error": "Add cameras error {}: {}",
    "conversion_error_status": "Conversion Error: {}",
    "add_camera_error_status": "Add Camera Error: {}",
    "realign_error": "Realign error: {}",
    "remove_spherical_error": "Remove spherical error: {}",
    "processing_finished_status": "Processing finished",
    "project_save_error": "Project save error: {0}",
    "project_save_error_unexpected": "Unexpected error during project save: {0}",
    "select_threads": "Number of face threads (recommended {0}):", # Renamed
    "invalid_threads": "Invalid input. Using {0} face threads.", # Updated message
    "select_camera_threads": "Number of camera threads (recommended {0}):", # New
    "invalid_camera_threads": "Invalid input. Using {0} camera threads.", # New
}
# Функция для настройки системной локали и кодировок
def setup_locale_and_encoding():
    """
    Настраивает кодировку и локаль для корректной работы с кириллическими путями.
    Важно: Больше не определяет LANG, это делается в main().
    """
    print(_("setup_locale"))
    try:
        # Получаем текущую локаль системы (может пригодиться для других целей)
        system_locale_tuple = locale.getdefaultlocale()
        system_locale_str = system_locale_tuple[0] if system_locale_tuple else "unknown"
        print(_("system_locale").format(system_locale_str))

        # Попытка установить локаль системы (может помочь с форматированием дат/чисел)
        if system_locale_str != "unknown":
            try:
                locale.setlocale(locale.LC_ALL, '') # Используем системную локаль по умолчанию
                print(_("locale_set").format(locale.getlocale()))
            except locale.Error as e:
                print(_("failed_set_locale").format(str(e)))
            except Exception as e: # Ловим другие возможные ошибки при установке локали
                 print(f"Warning setting system locale: {e}")

        # Проверка кодировки файловой системы
        fs_encoding = sys.getfilesystemencoding()
        print(_("fs_encoding").format(fs_encoding))
        
        # Проверка кодировки консоли (безопасная проверка атрибута)
        console_encoding = getattr(sys.stdout, 'encoding', 'unknown')
        print(_("console_encoding").format(console_encoding))
        
        # Установим кодировку для вывода в консоль, если это возможно
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'): # Добавлена проверка для stderr
            sys.stderr.reconfigure(encoding='utf-8')
            print(_("stdout_reconfigured"))
    
    except Exception as e:
        print(_("locale_warning").format(str(e)))

# Функция для работы с кириллическими путями
def normalize_path(path):
    """
    Нормализует путь для корректной работы с кириллицей.
    """
    if not path:
        return path
        
    # Получаем кодировку файловой системы
    fs_encoding = sys.getfilesystemencoding()
    
    try:
        # Проверяем, является ли путь уже строкой unicode
        if isinstance(path, str):
            # Если путь уже является unicode-строкой, но содержит закодированные байты,
            # пробуем привести его к нормальной форме
            try:
                # Для Windows используем абсолютный путь с префиксом "\\?\"
                if os.name == 'nt' and not path.startswith('\\\\?\\'):
                    # Нормализуем путь и добавляем длинный префикс UNC, если он не слишком короткий
                    if len(path) > 240:
                        norm_path = os.path.abspath(path)
                        if not norm_path.startswith('\\\\?\\'):
                            norm_path = '\\\\?\\' + norm_path
                        return norm_path
            except Exception as e:
                print(_("path_normalization_warning").format(str(e)))
        else:
            # Если путь является bytes, конвертируем его в строку
            try:
                path = path.decode(fs_encoding)
            except UnicodeDecodeError:
                # Если стандартная кодировка не работает, пробуем другие распространенные кодировки
                for encoding in ['utf-8', 'cp1251', 'latin1']:
                    try:
                        path = path.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
    except Exception as e:
        print(_("path_processing_error").format(str(e)))
    
    # Обрабатываем специальным образом для Windows
    if os.name == 'nt':
        # Преобразуем относительный путь в абсолютный
        path = os.path.abspath(path)
    
    return path

# Обертка для функций работы с файлами Metashape
def fix_metashape_file_paths():
    """
    Модифицирует методы работы с файлами в Metashape для поддержки кириллицы.
    """
    try:
        # Сохраняем оригинальный метод Photo и переопределяем его
        original_photo_init = Metashape.Photo.__init__
        
        def photo_init_wrapper(self, *args, **kwargs):
            # Вызываем оригинальный метод
            original_photo_init(self, *args, **kwargs)
            
            # Если установлен путь, нормализуем его
            if hasattr(self, 'path') and self.path:
                self.path = normalize_path(self.path)
        
        # Заменяем оригинальный метод на обертку
        Metashape.Photo.__init__ = photo_init_wrapper
        
        print(_("metashape_methods_modified"))
    
    except Exception as e:
        print(_("failed_modify_metashape").format(str(e)))

# Функция для определения языка системы
def detect_system_language():
    """
    Определяет язык системы и устанавливает глобальную переменную current_language
    """
    global current_language
    try:
        # Получаем локаль системы
        system_locale = locale.getdefaultlocale()[0]
        if system_locale:
            # Проверяем, содержит ли локаль ru (русский)
            if 'ru' in system_locale.lower():
                current_language = "ru"
            else:
                current_language = "en"
        
        print(_("detected_system_language").format(current_language))
    except Exception as e:
        print(_("error_detecting_language").format(str(e)))
        # По умолчанию используем русский язык
        current_language = "ru"

# === Проверка и установка зависимостей ===
def check_and_install_packages():
    """Проверяет наличие и устанавливает необходимые библиотеки."""
    print(_("checking_libraries"))
    required_packages = {
        "cv2": "opencv-python"
    }
    # Отдельно обрабатываем PyQt5, так как его установка может быть сложнее
    pyqt5_packages = [
        "pyqt5",
        "pyqt5-tools",
        "pyqt5-sip"
    ]
    
    missing_packages = []
    for module_name, pip_name in required_packages.items():
        try:
            __import__(module_name)
            print(_("library_installed").format(module_name))
        except ImportError:
            missing_packages.append(pip_name)
            print(_("library_not_found").format(module_name))
    
    # Проверка PyQt5
    try:
        # Проверяем не только сам модуль, но и конкретные подмодули
        import PyQt5
        from PyQt5 import QtCore, QtWidgets
        print(_("pyqt5_installed"))
        pyqt5_installed = True
    except ImportError as e:
        print(_("pyqt5_problem").format(str(e)))
        missing_packages.extend(pyqt5_packages)
        pyqt5_installed = False
    
    if missing_packages:
        print(_("missing_libraries").format(', '.join(missing_packages)))
        try:
            # Используем текущий интерпретатор Python вместо поиска пути Metashape
            python_executable = sys.executable
            print(_("python_path").format(python_executable))
            
            if not os.path.exists(python_executable):
                print(_("error_python_not_found").format(python_executable))
                return False
                
            # Сначала обновим pip для надежности
            try:
                print(_("updating_pip"))
                result = subprocess.run([python_executable, "-m", "pip", "install", "--upgrade", "pip"], 
                                       capture_output=True, text=True)
                print(_("pip_update_result").format(result.returncode))
                print(_("output").format(result.stdout))
                if result.stderr:
                    print(_("errors").format(result.stderr))
            except Exception as e:
                print(_("warning_pip_update_failed").format(str(e)))
            
            # Если PyQt5 не установлен, сначала попробуем удалить существующие установки
            if not pyqt5_installed:
                try:
                    print(_("removing_pyqt5"))
                    subprocess.run([python_executable, "-m", "pip", "uninstall", "-y", "pyqt5", "pyqt5-tools", "pyqt5-sip"], 
                                  capture_output=True, text=True)
                except Exception as e:
                    print(_("error_removing_pyqt5").format(str(e)))
            
            # Установка каждого пакета с использованием --no-cache-dir для решения проблем с кешем
            for package in missing_packages:
                print(_("installing").format(package))
                try:
                    # Пробуем установить с отключенным кешем и явно указываем приоритет пользовательских пакетов
                    result = subprocess.run([python_executable, "-m", "pip", "install", "--no-cache-dir", "--user", package],
                                           capture_output=True, text=True)
                    print(_("installation_result").format(package, result.returncode))
                    print(_("output").format(result.stdout))
                    if result.stderr:
                        print(_("errors").format(result.stderr))
                        
                    if result.returncode != 0:
                        raise Exception(_("return_code").format(result.returncode))
                        
                    print(_("package_installed").format(package))
                except Exception as e:
                    print(_("failed_to_install").format(package, str(e)))
                    print(_("alternative_method"))
                    try:
                        # В случае ошибки, пробуем альтернативный репозиторий
                        result = subprocess.run([python_executable, "-m", "pip", "install", "--index-url=https://pypi.org/simple", "--no-cache-dir", "--user", package],
                                              capture_output=True, text=True)
                        print(_("alt_install_result").format(package, result.returncode))
                        print(_("output").format(result.stdout))
                        if result.stderr:
                            print(_("errors").format(result.stderr))
                            
                        if result.returncode != 0:
                            raise Exception(_("return_code").format(result.returncode))
                            
                        print(_("alt_install_success").format(package))
                    except Exception as e2:
                        print(_("alt_install_failed").format(package, str(e2)))
                        # Если это PyQt5, пропускаем ошибку и продолжаем работу в консольном режиме
                        if package not in pyqt5_packages:
                            return False
            
            print(_("all_libraries_installed"))
            
            # Перезагружаем модули после установки
            for module_name in list(sys.modules.keys()):
                if module_name.startswith('PyQt5') or module_name in required_packages:
                    print(_("removing_module").format(module_name))
                    if module_name in sys.modules:
                        del sys.modules[module_name]
            
            # Пытаемся импортировать PyQt5 после установки для проверки
            try:
                print(_("checking_pyqt5"))
                import PyQt5
                from PyQt5 import QtCore, QtWidgets
                print(_("pyqt5_after_install"))
                return True
            except ImportError as e:
                print(_("pyqt5_not_working").format(str(e)))
                print(_("continue_console"))
                return True  # Возвращаем True, чтобы продолжить работу, хотя PyQt5 не доступен
            
        except Exception as e:
            print(_("failed_libraries").format(str(e)))
            print(f"Подробности: {traceback.format_exc()}")
            print(_("script_continue"))
            return False
    
    return True

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
    print(_("showing_message").format(title))
    try:
        # Пробуем вызвать с двумя аргументами (новая версия API)
        Metashape.app.messageBox(title, message)
    except TypeError:
        # Если не работает, пробуем с одним аргументом (старая версия API)
        Metashape.app.messageBox(f"{title}\n\n{message}")
    except Exception as e:
        # Если и это не работает, просто выводим сообщение в консоль
        print(f"\n{title}\n{'-' * len(title)}\n{message}")
        print(_("error_showing_message").format(str(e)))

def get_string_option(prompt, options):
    """
    Запрашивает у пользователя строковый выбор из списка опций.
    Адаптировано для разных версий API Metashape.
    """
    print(_("option_request").format(prompt))
    try:
        # Попытка использовать getInt для выбора из списка
        print(f"{prompt} ({_('option_variants').format(', '.join(options))})")
        for i, option in enumerate(options):
            print(f"{i+1}. {option}")
        
        # Используем безопасный метод запроса числа
        try:
            index = Metashape.app.getInt(f"{prompt} (1-{len(options)})", 1, 1, len(options))
        except TypeError:
            # Если метод не принимает min и max значения, используем только первые два аргумента
            index = Metashape.app.getInt(f"{prompt} (1-{len(options)})", 1)
            # Проверяем, что индекс находится в допустимом диапазоне
            if index < 1:
                index = 1
            elif index > len(options):
                index = len(options)
                
        print(_("user_selected_index").format(index))
        return options[index - 1]
    except Exception as e:
        print(_("error_using_getInt").format(str(e)))
        # Если getInt не работает, пробуем getString
        try:
            # Сначала пробуем новую версию API
            result = Metashape.app.getString(prompt, options[0])
            print(_("getString_result").format(result))
            return result
        except Exception as e2:
            print(_("error_using_getString").format(str(e2)))
            # Если это не работает, используем простой getString и валидируем ввод
            try:
                result = Metashape.app.getString(prompt, options[0])
                print(_("simple_getString_result").format(result))
                if result in options:
                    return result
                return options[0]  # Возвращаем значение по умолчанию, если ввод неверный
            except Exception as e3:
                print(_("critical_input_error").format(str(e3)))
                return options[0]  # В случае ошибки возвращаем первую опцию

def format_time(seconds):
    """Форматирует время в удобочитаемый вид."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    if current_language == "ru":
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# Функции для работы с изображениями с поддержкой кириллицы
def read_image_with_cyrillic(image_path):
    """
    Читает изображение с поддержкой кириллических путей.
    """
    try:
        import cv2
        import numpy as np
        
        # Нормализуем путь
        normalized_path = normalize_path(image_path)
        
        # Пробуем прочитать изображение
        image = cv2.imread(normalized_path)
        
        # Если чтение не удалось, используем альтернативный метод для Windows
        if image is None and os.name == 'nt':
            try:
                # Для Windows: открываем файл как бинарный и читаем его содержимое
                with open(normalized_path, 'rb') as f:
                    img_content = bytearray(f.read())
                
                # Преобразуем содержимое в numpy array и декодируем изображение
                np_arr = np.asarray(img_content, dtype=np.uint8)
                image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                
                print(f"Использован альтернативный метод чтения для {image_path}")
            except Exception as e:
                print(f"Альтернативный метод чтения не удался: {str(e)}")
        
        return image
    
    except Exception as e:
        print(f"Ошибка при чтении изображения '{image_path}': {str(e)}")
        return None

def save_image_with_cyrillic(image, output_path, params=None):
    """
    Сохраняет изображение с поддержкой кириллических путей.
    """
    try:
        import cv2
        import numpy as np
        
        # Нормализуем путь
        normalized_path = normalize_path(output_path)
        
        # Создаем директорию, если она не существует
        os.makedirs(os.path.dirname(normalized_path), exist_ok=True)
        
        # Для Windows используем альтернативный метод
        if os.name == 'nt':
            try:
                # Кодируем изображение в буфер
                if params is not None:
                    _, buffer = cv2.imencode('.jpg' if normalized_path.lower().endswith(('.jpg', '.jpeg')) else 
                                            '.png' if normalized_path.lower().endswith('.png') else 
                                            '.tiff' if normalized_path.lower().endswith(('.tiff', '.tif')) else '.jpg', 
                                            image, params)
                else:
                    _, buffer = cv2.imencode('.jpg' if normalized_path.lower().endswith(('.jpg', '.jpeg')) else 
                                            '.png' if normalized_path.lower().endswith('.png') else 
                                            '.tiff' if normalized_path.lower().endswith(('.tiff', '.tif')) else '.jpg', 
                                            image)
                
                # Записываем буфер в файл
                with open(normalized_path, 'wb') as f:
                    f.write(buffer)
                
                print(f"Использован альтернативный метод сохранения для {output_path}")
                return True
            except Exception as e:
                print(f"Альтернативный метод сохранения не удался: {str(e)}")
        
        # Стандартный метод сохранения
        success = cv2.imwrite(normalized_path, image, params if params is not None else [])
        return success
    
    except Exception as e:
        print(f"Ошибка при сохранении изображения '{output_path}': {str(e)}")
        return False

# Добавляем обработку исключений для всего скрипта
try:
    # Определяем язык системы - БОЛЬШЕ НЕ НУЖНО, делается в main()
    detect_system_language()
    
    # Настройка локали и кодировок
    setup_locale_and_encoding()
    
    # Модификация методов Metashape для поддержки кириллицы
    fix_metashape_file_paths()
    
    # Пытаемся установить необходимые пакеты
    print(_("checking_installing"))
    packages_installed = check_and_install_packages()
    print(_("package_install_result").format(packages_installed))

    # Теперь импортируем cv2 после установки
    try:
        print(_("trying_import_opencv"))
        import cv2
        import numpy as np
        print(_("opencv_imported").format(cv2.__version__))
    except ImportError as e:
        print(_("failed_import_opencv").format(str(e)))
        print(_("script_cant_work"))
        # Ждем ввода перед завершением, чтобы увидеть сообщение об ошибке
        input(_("press_enter"))
        sys.exit(1)

    # Проверяем, можно ли использовать PyQt5
    try:
        print(_("checking_pyqt5_availability"))
        import PyQt5
        from PyQt5 import QtCore, QtWidgets
        use_gui = True
        print(_("pyqt5_available"))
    except ImportError as e:
        use_gui = False
        print(_("pyqt5_unavailable").format(str(e)))

    # Импортируем PyQt5, если он доступен
    if use_gui:
        try:
            print(_("importing_pyqt5"))
            from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                                       QLabel, QPushButton, QProgressBar, QFileDialog, QCheckBox,
                                       QMessageBox, QComboBox, QSpinBox, QDoubleSpinBox, QGroupBox)
            from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
            print(_("pyqt5_components_imported"))
        except ImportError as e:
            print(_("failed_import_pyqt5_components").format(str(e)))
            use_gui = False
            print(_("script_continue_console"))

    print(_("script_first_part_loaded"))

except Exception as global_error:
    print("=================== " + _("critical_error") + " ===================")
    print(_("unexpected_error").format(str(global_error)))
    print(traceback.format_exc())
    print("==========================================================")
    # Ждем ввода перед завершением, чтобы увидеть сообщение об ошибке
    input(_("press_enter"))
    sys.exit(1)

# === Часть 2: Функции для преобразования проекций ===

# Добавляем словари переводов для этой части
translations["ru"].update({
    "equirect_to_persp_map": "Создание карты проекции из эквиректангулярной в перспективную...",
    "fixing_back_face": "Исправление артефакта задней грани...",
    "determining_coordinate_system": "Определение типа координатной системы...",
    "coordinate_system_determined": "Определена координатная система: {0}",
    "unknown_coordinate_system": "Предупреждение: неизвестная координатная система '{0}'. Используем Y_UP.",
    "image_load_error": "Не удалось загрузить изображение: {0}",
    "auto_calculate_face_size": "Автоматически рассчитанный размер грани: {0}px",
    "face_processing_error": "Ошибка при обработке грани {0}: {1}",
    "created_no_faces": "Не удалось создать ни одной грани куба.",
    "alternative_read_method": "Использован альтернативный метод чтения для {0}",
    "alternative_read_failed": "Альтернативный метод чтения не удался: {0}",
    "read_image_error": "Ошибка при чтении изображения '{0}': {1}",
    "creating_directory": "Создание директории: {0}",
    "alternative_save_method": "Использован альтернативный метод сохранения для {0}",
    "alternative_save_failed": "Альтернативный метод сохранения не удался: {0}",
    "save_image_error": "Ошибка при сохранении изображения '{0}': {1}"
})

translations["en"].update({
    "equirect_to_persp_map": "Creating projection map from equirectangular to perspective...",
    "fixing_back_face": "Fixing back face artifact...",
    "determining_coordinate_system": "Determining coordinate system type...",
    "coordinate_system_determined": "Coordinate system determined: {0}",
    "unknown_coordinate_system": "Warning: unknown coordinate system '{0}'. Using Y_UP.",
    "image_load_error": "Failed to load image: {0}",
    "auto_calculate_face_size": "Automatically calculated face size: {0}px",
    "face_processing_error": "Error processing face {0}: {1}",
    "created_no_faces": "Failed to create any cube faces.",
    "alternative_read_method": "Used alternative reading method for {0}",
    "alternative_read_failed": "Alternative reading method failed: {0}",
    "read_image_error": "Error reading image '{0}': {1}",
    "creating_directory": "Creating directory: {0}",
    "alternative_save_method": "Used alternative saving method for {0}",
    "alternative_save_failed": "Alternative saving method failed: {0}",
    "save_image_error": "Error saving image '{0}': {1}"
})

def eqruirect2persp_map(img_shape, FOV, THETA, PHI, Hd, Wd, overlap=10, messages=None):
    """
    Создает карты отображения для преобразования эквиректангулярной проекции в перспективную.
    """
    # Если messages передан, используем его, иначе используем функцию _
    if messages:
        print(messages["equirect_to_persp_map"])
    else:
        print(_("equirect_to_persp_map"))
        
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
    [R1, jacobian] = cv2.Rodrigues(z_axis * np.radians(THETA))
    [R2, jacobian] = cv2.Rodrigues(np.dot(R1, y_axis) * np.radians(-PHI))

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

def fix_back_face_artifact(image, messages=None):
    """
    Исправляет артефакт в виде черной вертикальной полосы в центре изображения.
    """
    # Если messages передан, используем его, иначе используем функцию _
    if messages:
        # Тут не выводим сообщение, чтобы не засорять лог
        pass
    else:
        # Не используем _() внутри функции, так как она может вызываться из потоков
        pass
        
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

def determine_coordinate_system():
    """
    Определяет тип координатной системы на основе анализа положения камер.
    """
    print(_("determining_coordinate_system"))
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
    print(_("coordinate_system_determined").format(determined_orientation))
    return determined_orientation

# === Часть 3: Оптимизированная функция конвертации с многопоточностью ===

# Добавляем переводы для этой части
translations["ru"].update({
    "converting_spherical": "Конвертация сферического изображения в кубическую проекцию...",
    "threading_info": "Используем {0} потоков для параллельной обработки граней...",
    "converting_face": "Обработка грани {0}...",
    "face_converted": "Грань {0} успешно обработана",
    "save_error": "Не удалось сохранить изображение {0}",
    "processing_threads": "Используем {0} потоков для параллельной обработки",
    "cube_face_settings": "Настройки граней куба",
    "conversion_error": "Ошибка конвертации: {0}",
    "adding_cube_cameras": "Добавление камер для граней куба...",
    "camera_added": "Добавлена камера для грани {0}",
    "camera_matrix_set": "Установлена матрица камеры для {0}"
})

translations["en"].update({
    "converting_spherical": "Converting spherical image to cubemap projection...",
    "threading_info": "Using {0} threads for parallel face processing...",
    "converting_face": "Processing face {0}...",
    "face_converted": "Face {0} successfully processed",
    "save_error": "Failed to save image {0}",
    "processing_threads": "Using {0} threads for parallel processing",
    "cube_face_settings": "Cube face settings",
    "conversion_error": "Conversion error: {0}",
    "adding_cube_cameras": "Adding cameras for cube faces...",
    "camera_added": "Added camera for face {0}",
    "camera_matrix_set": "Camera matrix set for {0}"
})

def realign_cameras():
    """
    Выполняет повторное выравнивание ВСЕХ камер в активном чанке,
    сбрасывая их текущее выравнивание.
    Использует параметры, найденные рабочими для API.
    Возвращает True, если выравнивание было успешно запущено, False в противном случае.
    """
    print(_("realigning_cameras"))
    try:
        # Проверка наличия активного чанка
        print("DEBUG: Проверка активного чанка...") # DEBUG
        chunk = Metashape.app.document.chunk
        if not chunk:
            raise Exception("Чанк не найден. Пожалуйста, создайте или выберите чанк.")
        print("DEBUG: Активный чанк найден.") # DEBUG

        # Попытка вызова API с рабочими параметрами
        try:
            print("DEBUG: Попытка вызова chunk.matchPhotos() для всех камер с заданными параметрами...") # DEBUG
            # Параметры из успешного теста (кроме accuracy)
            chunk.matchPhotos(
                # cameras=None - применяем ко всем камерам
                generic_preselection=True, 
                reference_preselection=False, 
                filter_mask=False, 
                keypoint_limit=100000, 
                tiepoint_limit=4000,
                guided_matching=False,
                reset_matches=True # Сбрасываем предыдущие точки
            )
            print("DEBUG: Вызов chunk.matchPhotos() завершен.") # DEBUG
            
            print("DEBUG: Попытка вызова chunk.alignCameras() через API для всех камер с заданными параметрами...") # DEBUG
            chunk.alignCameras(
                # cameras=None - применяем ко всем камерам
                adaptive_fitting=False, 
                reset_alignment=True
                # filter_stationary_points - убрали, т.к. он мог вызывать проблемы ранее
            )
            print("DEBUG: Вызов chunk.alignCameras() успешно завершен.") # DEBUG
            print(_("align_completed")) # Используем стандартное сообщение об успехе
            return True # <--- Успешный запуск API
        
        except Exception as api_error:
            error_message = _("realign_error").format(str(api_error))
            print(f"DEBUG: Ошибка при вызове API (matchPhotos/alignCameras): {api_error}") # DEBUG
            print(error_message)
            print(traceback.format_exc())
            # Показываем ошибку в GUI Metashape
            if Metashape.app is not None:
                Metashape.app.messageBox(f"{_('error_title')}\n\n{error_message}\n\n{traceback.format_exc()}")
            return False # <--- Ошибка API

    except Exception as e:
        # Обработка других ошибок (например, чанк не найден)
        error_message = _("realign_error").format(str(e))
        print(error_message)
        print(traceback.format_exc())
        if Metashape.app is not None:
            Metashape.app.messageBox(f"{_('error_title')}\n\n{error_message}\n\n{traceback.format_exc()}")
        return False # <--- Критическая ошибка внутри функции

# Функция для удаления исходных сферических камер
def remove_spherical_cameras():
    """
    Удаляет исходные сферические камеры из проекта.
    """
    print(_("removing_spherical"))
    try:
        doc = Metashape.app.document
        chunk = doc.chunk
        
        # Получаем список сферических камер по метке
        # Обычно у них нет суффикса _front, _back и т.д.
        spherical_cameras = []
        for camera in chunk.cameras:
            is_spherical = True
            for suffix in ["_front", "_right", "_left", "_top", "_down", "_back"]:
                if camera.label.endswith(suffix):
                    is_spherical = False
                    break
            if is_spherical:
                spherical_cameras.append(camera)
        
        # Удаляем найденные сферические камеры
        for camera in spherical_cameras:
            chunk.remove(camera)
        
        print(_("remove_completed"))
        return True
    except Exception as e:
        print(f"Ошибка при удалении сферических камер: {str(e)}")
        return False

# Модифицируем функцию convert_spherical_to_cubemap для поддержки выборочной генерации граней
def convert_spherical_to_cubemap(spherical_image_path, output_folder, camera_label, persp_size=None, overlap=10, 
                                file_format="jpg", quality=95, interpolation=cv2.INTER_CUBIC, max_workers=None,
                                selected_faces=None):
    """
    Конвертирует сферическое изображение в кубическую проекцию.
    Использует многопоточность для ускорения обработки.
    
    Parameters:
    -----------
    spherical_image_path : str
        Путь к сферическому изображению
    output_folder : str
        Путь к папке для сохранения результатов
    camera_label : str
        Метка камеры для именования файлов
    persp_size : int, optional
        Размер грани куба (ширина и высота), None для автоматического расчета
    overlap : float, optional
        Перекрытие в градусах (по умолчанию 10)
    file_format : str, optional
        Формат выходного файла (jpg, png, tiff)
    quality : int, optional
        Качество сжатия (75-100 для JPEG)
    interpolation : int, optional
        Метод интерполяции (cv2.INTER_NEAREST, cv2.INTER_LINEAR, cv2.INTER_CUBIC)
    max_workers : int, optional
        Максимальное количество потоков для параллельной обработки
    selected_faces : list, optional
        Список выбранных граней для генерации (front, right, left, top, down, back)
        Если None, будут сгенерированы все грани
    
    Returns:
    --------
    dict
        Словарь с путями к созданным изображениям для каждой грани
    """
    # Сначала локализуем все необходимые строки перед созданием потоков
    # и сохраняем в локальный словарь
    messages = {
        "converting_spherical": _("converting_spherical"),
        "threading_info": _("threading_info"),
        "creating_directory": _("creating_directory"),
        "image_load_error": _("image_load_error"),
        "auto_calculate_face_size": _("auto_calculate_face_size"),
        "converting_face": _("converting_face"),
        "face_converted": _("face_converted"),
        "save_error": _("save_error"),
        "face_processing_error": _("face_processing_error"),
        "created_no_faces": _("created_no_faces"),
        "fixing_back_face": _("fixing_back_face"),
        "equirect_to_persp_map": _("equirect_to_persp_map"),
        "selected_faces": _("selected_faces"),
        "no_faces_selected": _("no_faces_selected")
    }
    
    print(messages["converting_spherical"])
    
    # Используем версию с поддержкой кириллицы
    if max_workers is None:
        max_workers = min(6, os.cpu_count() or 1)
    
    print(messages["threading_info"].format(max_workers))
        
    # Нормализуем пути для корректной работы с кириллицей
    normalized_image_path = normalize_path(spherical_image_path)
    normalized_output_folder = normalize_path(output_folder)
    
    # Создаем директорию результатов, если она не существует
    try:
        os.makedirs(normalized_output_folder, exist_ok=True)
        print(messages["creating_directory"].format(normalized_output_folder))
    except Exception as e:
        print(f"Ошибка при создании директории: {str(e)}")
    
    # Загружаем сферическое изображение с поддержкой кириллицы
    spherical_image = read_image_with_cyrillic(normalized_image_path)
    if spherical_image is None:
        raise ValueError(messages["image_load_error"].format(spherical_image_path))

    equirect_height, equirect_width = spherical_image.shape[:2]
    
    # Автоматическое определение размера граней куба, если не указан
    if persp_size is None:
        # Используем примерно четверть ширины исходного изображения
        persp_size = min(max(equirect_width // 4, 512), 4096)
        # persp_size = 2 ** int(np.log2(persp_size) + 0.5) # Убираем округление до степени двойки
        print(messages["auto_calculate_face_size"].format(persp_size))

    # Полный список граней куба
    all_faces = ["front", "right", "left", "top", "down", "back"]
    
    # Если выбраны конкретные грани, используем их, иначе все грани
    faces_to_process = selected_faces if selected_faces else all_faces
    
    # Выводим информацию о выбранных гранях
    if selected_faces:
        print(messages["selected_faces"].format(", ".join(faces_to_process)))
    else:
        print(messages["no_faces_selected"])
    
    # Параметры для каждой грани куба
    faces_params = {
        "front": {"fov": 90, "theta": 0, "phi": 0},
        "right": {"fov": 90, "theta": 90, "phi": 0},
        "left": {"fov": 90, "theta": -90, "phi": 0},
        "top": {"fov": 90, "theta": 0, "phi": 90},
        "down": {"fov": 90, "theta": 0, "phi": -90},
        "back": {"fov": 90, "theta": 180, "phi": 0},
    }
    
    # Отфильтровываем только выбранные грани
    faces_params = {face: params for face, params in faces_params.items() if face in faces_to_process}

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

    # Создаем замыкание для функции обработки грани с доступом к локализованным сообщениям
    def process_face(face_name, params):
        try:
            print(messages["converting_face"].format(face_name))
            
            # Вызываем модифицированные функции с передачей словаря messages
            map_x, map_y = eqruirect2persp_map(
                img_shape=(equirect_height, equirect_width),
                FOV=params["fov"],
                THETA=params["theta"],
                PHI=params["phi"],
                Hd=persp_size,
                Wd=persp_size,
                overlap=overlap,
                messages=messages
            )
    
            perspective_image = cv2.remap(spherical_image, map_x, map_y, interpolation=interpolation)
        
            # Постобработка для грани "back" для устранения черной вертикальной полосы
            if face_name == "back":
                perspective_image = fix_back_face_artifact(perspective_image, messages=messages)
            
            output_filename = f"{camera_label}_{face_name}.{file_ext}"
            output_path = os.path.join(normalized_output_folder, output_filename)
            
            # Используем функцию с поддержкой кириллицы для сохранения изображения
            success = save_image_with_cyrillic(perspective_image, output_path, save_params)
            
            if not success:
                raise ValueError(messages["save_error"].format(output_path))
            
            print(messages["face_converted"].format(face_name))
            return face_name, output_path
        except Exception as e:
            print(messages["face_processing_error"].format(face_name, str(e)))
            return face_name, None
    
    # Если нет граней для обработки, сразу возвращаем пустой словарь
    if not faces_params:
        return image_paths
    
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
                print(messages["face_processing_error"].format(face_name, str(e)))
    
    # Теперь мы проверяем, были ли сгенерированы какие-либо грани
    # Если не было выбрано никаких граней, это не ошибка
    if not image_paths and selected_faces:
        raise ValueError(messages["created_no_faces"])
        
    return image_paths

# === Часть 4: Функция добавления камер ===

# Добавляем переводы для этой части
translations["ru"].update({
    "adding_cameras": "Добавление камер на основе сферической камеры...",
    "cubemap_directions": "Настройка направлений для граней куба ({0})...",
    "camera_added": "Добавлена камера {0}",
    "camera_sensor_created": "Создан сенсор {0}",
    "camera_parameter_set": "Установлены параметры для камеры {0}",
    "camera_transform_set": "Установлена трансформация для камеры {0}",
    "camera_photo_set": "Установлено изображение для камеры {0}",
    "file_not_found": "Ошибка: файл изображения не найден: {0}",
    "camera_metadata_set": "Установлены метаданные для камеры {0}",
    "rotation_matrix_created": "Создана матрица вращения для грани {0}"
})

translations["en"].update({
    "adding_cameras": "Adding cameras based on spherical camera...",
    "cubemap_directions": "Setting up directions for cube faces ({0})...",
    "camera_added": "Added camera {0}",
    "camera_sensor_created": "Created sensor {0}",
    "camera_parameter_set": "Set parameters for camera {0}",
    "camera_transform_set": "Set transformation for camera {0}",
    "camera_photo_set": "Set image for camera {0}",
    "file_not_found": "Error: image file not found: {0}",
    "camera_metadata_set": "Set metadata for camera {0}",
    "rotation_matrix_created": "Created rotation matrix for face {0}"
})

# Модифицируем функцию add_cubemap_cameras для поддержки выборочных граней
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
    print(_("adding_cameras"))
    
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
        print(_("cubemap_directions").format("Y_UP"))
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
        print(_("cubemap_directions").format("Z_UP"))
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
        print(_("cubemap_directions").format("X_UP"))
        cubemap_directions = {
            "front": {"forward": [0, 1, 0], "up": [1, 0, 0]},
            "right": {"forward": [0, 0, 1], "up": [1, 0, 0]},
            "left": {"forward": [0, 0, -1], "up": [1, 0, 0]},
            "top": {"forward": [1, 0, 0], "up": [0, -1, 0]},
            "down": {"forward": [-1, 0, 0], "up": [0, 1, 0]},
            "back": {"forward": [0, -1, 0], "up": [1, 0, 0]},
        }
    else:
        print(_("unknown_coordinate_system").format(coord_system))
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

    # Создаем камеры только для выбранных граней куба
    cameras_created = []
    print(f"DEBUG: Adding cameras for faces: {list(image_paths.keys())}") # DEBUG
    for face_name in image_paths.keys():
        if face_name not in cubemap_directions:
            print(f"DEBUG: Skipping face {face_name}, no directions found.") # DEBUG
            continue

        print(f"DEBUG: Processing face: {face_name}") # DEBUG
        directions = cubemap_directions[face_name]

        # Создаем новую камеру
        print(f"DEBUG: Calling chunk.addCamera() for {face_name}...") # DEBUG
        camera = None # Инициализируем camera как None
        try:
            # === Убираем паузу и обновление перед вызовом ===
            # time.sleep(0.5) # Увеличиваем паузу до 0.5с
            # if Metashape.app is not None: # Проверка, что Metashape запущен с GUI
            #      Metashape.app.update()
            # ===================================================
            print(f"DEBUG: --- BEFORE chunk.addCamera() for {face_name} ---") # DEBUG
            camera = chunk.addCamera() # <--- Потенциальное место зависания
            print(f"DEBUG: --- AFTER chunk.addCamera() for {face_name} (Result: {'Success' if camera else 'None'}) ---") # DEBUG

            if camera is None:
                print(f"ERROR: chunk.addCamera() returned None for face {face_name}") # DEBUG
                continue
        except Exception as e:
            print(f"ERROR: Exception during chunk.addCamera() for face {face_name}: {e}") # DEBUG
            traceback.print_exc() # Печатаем полный трейсбек ошибки
            continue

        camera.label = f"{spherical_camera.label}_{face_name}"
        print(_("camera_added").format(camera.label))

        # Копируем или создаем новый сенсор
        print(f"DEBUG: Finding/creating sensor for {face_name}...") # DEBUG
        # Ищем сенсор с нужным размером
        persp_sensors = [s for s in chunk.sensors if s.type == Metashape.Sensor.Type.Frame and s.width == persp_size and s.height == persp_size]
        if persp_sensors:
            camera.sensor = persp_sensors[0]
            print(f"DEBUG: Reusing existing sensor '{persp_sensors[0].label}'") # DEBUG
        else:
            # Если нет подходящего сенсора, создаем новый
            print(f"DEBUG: Creating new sensor for {face_name}...") # DEBUG
            sensor = chunk.addSensor()
            if sensor is None:
                print(f"ERROR: chunk.addSensor() returned None for face {face_name}") # DEBUG
                continue
            sensor.label = f"Perspective_{persp_size}px"
            sensor.type = Metashape.Sensor.Type.Frame
            sensor.width = persp_size
            sensor.height = persp_size
            camera.sensor = sensor
            print(_("camera_sensor_created").format(sensor.label))

        cameras_created.append(camera)

        # Настройка параметров камеры
        print(f"DEBUG: Setting sensor parameters for {face_name}...") # DEBUG
        sensor = camera.sensor
        sensor.type = Metashape.Sensor.Type.Frame
        sensor.width = persp_size
        sensor.height = persp_size
        # print(_("camera_parameter_set").format(camera.label)) # Less verbose logging

        # Устанавливаем фокусное расстояние для поля зрения 90 градусов
        focal_length = persp_size / (2 * np.tan(np.radians(90 / 2)))
        sensor.focal_length = focal_length
        sensor.pixel_width = 1
        sensor.pixel_height = 1

        # Устанавливаем матрицу внутренних параметров камеры
        print(f"DEBUG: Setting calibration for {face_name}...") # DEBUG
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
        print(f"DEBUG: Setting transform (translation) for {face_name}...") # DEBUG
        camera.transform = Metashape.Matrix.Translation(position)
        # print(_("camera_transform_set").format(camera.label)) # Less verbose logging

        # Устанавливаем ориентацию камеры
        print(f"DEBUG: Calculating rotation matrix for {face_name}...") # DEBUG
        forward = directions["forward"]
        up = directions["up"]
        rotation_matrix = create_rotation_matrix(forward, up, base_rotation_4x4)
        print(_("rotation_matrix_created").format(face_name))
        print(f"DEBUG: Setting transform (rotation) for {face_name}...") # DEBUG
        camera.transform = camera.transform * rotation_matrix

        # Создаем объект Photo для камеры
        print(f"DEBUG: Creating Photo object for {face_name}...") # DEBUG
        camera.photo = Metashape.Photo()

        # Загружаем изображение - используем нормализацию путей для кириллицы
        normalized_path = normalize_path(image_paths[face_name])
        print(f"DEBUG: Setting photo path '{normalized_path}' for {face_name}...") # DEBUG
        camera.photo.path = normalized_path
        # print(_("camera_photo_set").format(camera.label)) # Less verbose logging

        # Проверяем, существует ли файл изображения
        print(f"DEBUG: Checking if file exists for {face_name}...") # DEBUG
        if not os.path.exists(normalized_path):
            print(_("file_not_found").format(normalized_path))
            continue

        # Обновляем метаданные
        print(f"DEBUG: Setting metadata for {face_name}...") # DEBUG
        camera.meta['Image/Width'] = str(persp_size)
        camera.meta['Image/Height'] = str(persp_size)
        camera.meta['Image/Orientation'] = "1"
        print(_("camera_metadata_set").format(camera.label))
        print(f"DEBUG: Finished processing face {face_name}") # DEBUG

    print("DEBUG: Finished add_cubemap_cameras function.") # DEBUG
    return cameras_created

# === Часть 5: Многопоточная обработка камер для GUI ===

# Добавляем переводы для этой части
translations["ru"].update({
    "processing_started": "Начало обработки камер...",
    "processing_camera": "Обработка камеры {0} ({1}/{2})...",
    "camera_processed": "Камера {0} успешно обработана",
    "processing_error": "Ошибка при обработке камеры {0}: {1}",
    "processing_aborted": "Обработка прервана пользователем",
    "processing_complete": "Обработка завершена",
    "general_processing_error": "Общая ошибка обработки: {0}",
    "processing_stats": "Статистика обработки: обработано {0} из {1}, пропущено {2}",
    "elapsed_time": "Затраченное время: {0}",
    "gui_thread_starting": "Запуск потока обработки в GUI...",
    "gui_thread_finished": "Поток обработки в GUI завершен",
    "gui_thread_error": "Ошибка в потоке GUI: {0}"
})

translations["en"].update({
    "processing_started": "Starting camera processing...",
    "processing_camera": "Processing camera {0} ({1}/{2})...",
    "camera_processed": "Camera {0} successfully processed",
    "processing_error": "Error processing camera {0}: {1}",
    "processing_aborted": "Processing aborted by user",
    "processing_complete": "Processing complete",
    "general_processing_error": "General processing error: {0}",
    "processing_stats": "Processing stats: processed {0} of {1}, skipped {2}",
    "elapsed_time": "Elapsed time: {0}",
    "gui_thread_starting": "Starting GUI processing thread...",
    "gui_thread_error": "Error in GUI thread: {0}",
    "gui_thread_finished": "GUI processing thread finished"
})

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
            # Количество потоков для обработки граней ОДНОЙ камеры
            self.faces_threads = self.options.get("faces_threads", min(6, os.cpu_count() or 1))
            # Количество потоков для параллельной обработки РАЗНЫХ камер (ПОКА НЕ ИСПОЛЬЗУЕТСЯ В GUI/CONSOLE)
            # Используем os.cpu_count() как временное значение по умолчанию
            self.camera_threads = self.options.get("camera_threads", os.cpu_count() or 1)
        
        def _process_single_camera(self, camera):
            """Выполняет конвертацию для одной камеры."""
            if self.stop_requested:
                return None # Возвращаем None, если обработка остановлена

            camera_label = camera.label
            spherical_image_path = camera.photo.path
            normalized_path = normalize_path(spherical_image_path)

            try:
                selected_faces = self.options.get("selected_faces", None)
                image_paths = convert_spherical_to_cubemap(
                    spherical_image_path=normalized_path,
                    output_folder=self.output_folder,
                    camera_label=camera_label,
                    persp_size=self.options.get("persp_size"),
                    overlap=self.options.get("overlap", 10),
                    file_format=self.options.get("file_format", "jpg"),
                    quality=self.options.get("quality", 95),
                    interpolation=self.options.get("interpolation", cv2.INTER_CUBIC),
                    max_workers=self.faces_threads, # Потоки для граней этой камеры
                    selected_faces=selected_faces
                )

                if image_paths:
                    # Получаем фактический размер изображения для добавления камер
                    first_image = list(image_paths.values())[0]
                    image = read_image_with_cyrillic(first_image)
                    if image is None:
                         # Используем None как индикатор ошибки чтения для дальнейшей обработки
                        print(f"Предупреждение: Не удалось прочитать изображение {first_image} для камеры {camera_label} после конвертации.")
                        actual_size = None
                    else:
                        actual_size = image.shape[0]

                    return {
                        "camera": camera,
                        "image_paths": image_paths,
                        "actual_size": actual_size, # Может быть None, если чтение не удалось
                        "error": None
                    }
                else:
                    print(f"Не создано ни одной грани для камеры {camera_label}")
                    # Возвращаем результат с ошибкой типа "skipped"
                    return {
                        "camera": camera,
                        "image_paths": None,
                        "actual_size": None,
                        "error": "skipped_no_faces"
                    }

            except Exception as e:
                error_message = _("conversion_error").format(camera_label, str(e))
                print(error_message)
                print(traceback.format_exc())
                # Возвращаем результат с ошибкой
                return {
                    "camera": camera,
                    "image_paths": None,
                    "actual_size": None,
                    "error": error_message
                }

        def run(self):
            try:
                print(_("gui_thread_starting"))
                start_time = time.time()
                total_cameras = len(self.cameras)
                processed_count = 0 # Счетчик успешно ДОБАВЛЕННЫХ камер
                skipped_count = 0   # Счетчик камер, пропущенных на этапе КОНВЕРТАЦИИ
                conversion_errors = [] # Ошибки конвертации
                add_camera_errors = [] # Ошибки добавления камер

                # --- Этап 1: Параллельная конвертация изображений ---
                # Используем self.camera_threads, значение по умолчанию пока os.cpu_count()
                print(f"--- Этап 1: Конвертация изображений ({self.camera_threads} потоков) ---")
                conversion_results = [] # Список для хранения результатов конвертации
                futures = []

                # Используем ThreadPoolExecutor для параллельной КОНВЕРТАЦИИ камер
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.camera_threads) as executor:
                    # Обновляем статус перед отправкой задач
                    self.update_progress.emit(0, total_cameras, "", _("submitting_conversion_tasks"), 0)

                    # Отправляем задачи на конвертацию
                    for i, camera in enumerate(self.cameras):
                        if self.stop_requested:
                            print("Остановка запрошена перед отправкой всех задач конвертации.")
                            break
                        # Передаем self.options в задачу
                        future = executor.submit(self._process_single_camera, camera)
                        futures.append(future)

                    # Собираем результаты по мере готовности
                    self.update_progress.emit(0, total_cameras, "", _("collecting_conversion_results"), 5) # Небольшой прогресс
                    conversion_completed_count = 0
                    for future in concurrent.futures.as_completed(futures):
                        if self.stop_requested:
                            print("Остановка запрошена во время сбора результатов конвертации.")
                            # Попытка отменить оставшиеся задачи (может не сработать, если они уже выполняются)
                            for f in futures:
                                if not f.done():
                                    f.cancel()
                            break

                        result = future.result()
                        conversion_completed_count += 1
                        progress_percent_conv = 5 + int((conversion_completed_count / total_cameras) * 45) # Конвертация - от 5% до 50%

                        if result: # Если не None (не было остановки внутри _process_single_camera)
                             camera_label = result["camera"].label
                             if result["error"]:
                                 skipped_count += 1
                                 if result["error"] != "skipped_no_faces": # Не считаем пропуск без граней за ошибку
                                     conversion_errors.append(result["error"])
                                 # Обновляем прогресс при ошибке/пропуске конвертации
                                 status_msg = _("conversion_error_status").format(camera_label) if result["error"] != "skipped_no_faces" else _("skipped_no_faces").format(camera_label)
                                 self.update_progress.emit(
                                     conversion_completed_count, total_cameras, camera_label,
                                     status_msg,
                                     progress_percent_conv
                                 )
                             elif result["actual_size"] is None: # Ошибка чтения после конвертации
                                 skipped_count += 1
                                 error_msg = f"Ошибка чтения изображения после конвертации для {camera_label}"
                                 conversion_errors.append(error_msg)
                                 self.update_progress.emit(
                                     conversion_completed_count, total_cameras, camera_label,
                                     _("conversion_error_status").format(camera_label),
                                     progress_percent_conv
                                 )
                             else:
                                 conversion_results.append(result)
                                 # Обновляем прогресс после успешной конвертации
                                 self.update_progress.emit(
                                     conversion_completed_count, total_cameras, camera_label,
                                     _("conversion_stage") + f" {_('face_converted').format(camera_label)}", # Уточненный статус
                                     progress_percent_conv
                                 )
                        else:
                            # Обработка была остановлена внутри _process_single_camera
                            print(f"Обработка камеры прервана (результат None).")
                            # Не увеличиваем счетчики, так как это следствие остановки

                # Если была запрошена остановка во время конвертации
                if self.stop_requested:
                    print(_("processing_aborted") + " (во время конвертации)")
                    self.processing_finished.emit(False, {
                        "processed": processed_count, "skipped": skipped_count,
                        "total": total_cameras, "time": time.time() - start_time,
                        "errors": conversion_errors + add_camera_errors
                    })
                    return

                # --- Этап 2: Последовательное добавление всех камер в Metashape ---
                print("--- Этап 2: Добавление камер в Metashape (Последовательно) ---")
                total_to_add = len(conversion_results)
                added_count = 0
                if total_to_add > 0:
                    chunk = Metashape.app.document.chunk # Получаем чанк один раз
                    coord_system = self.options.get("coord_system", "Y_UP")

                    for result in conversion_results: # Итерируем по успешно сконвертированным
                        if self.stop_requested:
                            print(_("processing_aborted") + " (во время добавления камер)")
                            break # Выходим из цикла добавления

                        camera = result["camera"]
                        camera_label = camera.label
                        image_paths = result["image_paths"]
                        actual_size = result["actual_size"]

                        # Обновляем прогресс: этап добавления камер
                        # 50% от конвертации + процент от добавления камер
                        progress_percent_add = 50 + int((added_count / total_to_add) * 40) # Добавление - от 50% до 90%
                        self.update_progress.emit(
                            conversion_completed_count + added_count, # Общий прогресс по задачам
                            total_cameras, # Всего камер
                            camera_label,
                            _("adding_cube_cameras_stage").format(camera_label, added_count + 1, total_to_add) + f" ({actual_size}px)...",
                            progress_percent_add
                        )

                        try:
                            # Добавление новых камер для выбранных граней куба
                            add_cubemap_cameras(
                                chunk=chunk, # Используем ранее полученный чанк
                                spherical_camera=camera,
                                image_paths=image_paths,
                                persp_size=actual_size,
                                coord_system=coord_system # Используем ранее полученную систему координат
                            )
                            processed_count += 1 # Счетчик успешно ДОБАВЛЕННЫХ камер
                            # Обновляем прогресс после успешного добавления
                            self.update_progress.emit(
                                conversion_completed_count + added_count + 1, total_cameras,
                                camera_label,
                                _("camera_added_status").format(camera_label),
                                progress_percent_add
                            )
                            print(_("camera_processed").format(camera_label))

                        except Exception as e:
                            # Ошибка на этапе добавления камер
                            error_message = _("add_camera_error").format(camera_label, str(e))
                            print(error_message)
                            print(traceback.format_exc())
                            add_camera_errors.append(error_message)
                            # Счетчик processed_count не увеличивается
                            # Обновляем прогресс при ошибке добавления
                            self.update_progress.emit(
                                conversion_completed_count + added_count + 1, total_cameras,
                                camera_label,
                                _("add_camera_error_status").format(camera_label),
                                progress_percent_add
                            )
                        finally:
                             added_count += 1 # Увеличиваем счетчик обработанных на этом этапе

                # Если была запрошена остановка во время добавления
                if self.stop_requested:
                     print(_("processing_aborted") + " (во время добавления камер)")
                     # Завершаем с текущей статистикой
                     self.processing_finished.emit(False, {
                         "processed": processed_count, # Сколько успели добавить
                         "skipped": skipped_count + (total_to_add - added_count), # Сконвертировано, но не добавлено + ошибки конвертации
                         "total": total_cameras,
                         "time": time.time() - start_time,
                         "errors": conversion_errors + add_camera_errors
                     })
                     return

                # --- Этап 3: Пост-обработка ---
                print("--- Этап 3: Пост-обработка (Последовательно) ---")
                final_progress = 90 # Начальный прогресс для пост-обработки

                if self.options.get("realign_cameras_after", False):
                    if self.stop_requested: return # Проверка на остановку
                    try:
                        self.update_progress.emit(total_cameras, total_cameras, "", _("realigning_cameras"), final_progress)
                        realign_cameras()
                        final_progress += 5
                    except Exception as e:
                        error_message = _("realign_error").format(str(e))
                        print(error_message); add_camera_errors.append(error_message) # Добавляем в ошибки добавления/пост-обработки

                if self.options.get("remove_spherical_cameras_after", False):
                    if self.stop_requested: return # Проверка на остановку
                    try:
                        self.update_progress.emit(total_cameras, total_cameras, "", _("removing_spherical"), final_progress)
                        remove_spherical_cameras()
                        final_progress += 5
                    except Exception as e:
                        error_message = _("remove_spherical_error").format(str(e))
                        print(error_message); add_camera_errors.append(error_message) # Добавляем в ошибки добавления/пост-обработки

                # --- Завершение ---
                # Убедимся, что прогресс достигает 100%
                self.update_progress.emit(total_cameras, total_cameras, "", _("processing_finished_status"), 100)
                total_time = time.time() - start_time
                final_skipped_count = skipped_count + (total_to_add - processed_count) # Ошибки конвертации + (Сконвертировано, но не добавлено из-за ошибки или остановки)
                print(_("processing_stats").format(processed_count, total_cameras, final_skipped_count))
                print(_("elapsed_time").format(format_time(total_time)))

                self.processing_finished.emit(True, {
                    "processed": processed_count,
                    "skipped": final_skipped_count,
                    "total": total_cameras,
                    "time": total_time,
                    "errors": conversion_errors + add_camera_errors # Объединяем все ошибки
                })
                print(_("gui_thread_finished"))

            except Exception as e:
                # Общая ошибка потока (оставляем без изменений)
                error_message = _("general_processing_error").format(str(e))
                print(error_message)
                print(traceback.format_exc())
                self.error_occurred.emit(error_message)
                print(_("gui_thread_error").format(str(e)))

        def stop(self):
            # Метод stop оставляем без изменений
            self.stop_requested = True
            print(_("processing_aborted"))

# === Часть 6: Графический интерфейс ===

# Добавляем переводы для этой части
translations["ru"].update({
    "gui_title": "Конвертация сферических изображений в кубическую проекцию",
    "settings_group": "Настройки",
    "output_folder_label": "Выходная папка:",
    "not_selected": "Не выбрана",
    "browse_button": "Обзор...",
    "overlap_label": "Перекрытие (градусы):",
    "face_size_label": "Размер грани куба:",
    "auto_size": "Автоматически (рекомендуется)",
    "coord_system_label": "Координатная система:",
    "auto_detect": "Автоопределение",
    "threads_label": "Потоки обработки граней:", # Renamed
    "threads_tooltip": "Количество параллельных потоков для обработки граней ОДНОЙ камеры", # Updated tooltip
    "camera_threads_label": "Потоки обработки камер:", # New label
    "camera_threads_tooltip": "Количество параллельных потоков для конвертации РАЗНЫХ камер", # New tooltip
    "image_group": "Параметры изображения",
    "format_label": "Формат файла:",
    "quality_label": "Качество:",
    "interp_label": "Интерполяция:",
    "nearest": "Ближайшая (быстрее, хуже качество)",
    "linear": "Линейная (средняя)",
    "cubic": "Кубическая (медленнее, лучше качество)",
    "project_info_group": "Информация о проекте",
    "cameras_count_label": "Количество найденных камер:",
    "detected_system_label": "Определённая координатная система:",
    "system_not_detected": "Не определена",
    "progress_group": "Прогресс обработки",
    "current_camera_label": "Текущая камера:",
    "no_camera": "Нет",
    "status_label": "Статус:",
    "waiting_start": "Ожидание запуска",
    "time_remaining_label": "Оставшееся время:",
    "time_format": "--:--:--",
    "start_button": "Запустить",
    "stop_button": "Остановить",
    "close_button": "Закрыть",
    "status_ready": "Готов к работе",
    "select_output_folder": "Выберите папку для сохранения изображений",
    "error_title": "Ошибка",
    "no_chunk_error": "Активный чанк не найден.",
    "no_output_folder": "Пожалуйста, выберите существующую выходную папку.",
    "no_cameras_error": "Не найдено сферических камер для обработки.",
    "processing_status": "Обработка...",
    "processing_info": "Обработка {0} камер используя {1} потоков...",
    "completed_title": "Завершено",
    "processing_completed": "Обработка завершена!",
    "total_cameras": "Всего камер: {0}",
    "successfully_processed": "Успешно обработано: {0}",
    "skipped_errors": "Пропущено/ошибки: {0}",
    "total_time": "Общее время: {0}",
    "errors_count": "Ошибки ({0}):",
    "more_errors": "... и еще {0} ошибок.",
    "aborted_title": "Прервано",
    "processing_aborted_message": "Обработка прервана пользователем.",
    "aborted_status": "Прервано",
    "processing_aborted_status": "Обработка прервана пользователем",
    "processing_status_message": "Обработка {0} камер...",
    "processing_result": "Обработка завершена. Успешно: {0}, Ошибок: {1}",
    "error_status": "Ошибка",
    "processing_error": "Ошибка обработки",
    "confirm_exit": "Подтверждение",
    "confirm_exit_message": "Обработка не завершена. Вы уверены, что хотите выйти?",
    "confirm_abort": "Вы уверены, что хотите прервать обработку?",
    "language_label": "Язык интерфейса:",
    "russian": "Русский",
    "english": "English"
})

translations["en"].update({
    "gui_title": "Spherical to Cubemap Image Conversion",
    "settings_group": "Settings",
    "output_folder_label": "Output folder:",
    "not_selected": "Not selected",
    "browse_button": "Browse...",
    "overlap_label": "Overlap (degrees):",
    "face_size_label": "Cube face size:",
    "auto_size": "Automatically (recommended)",
    "coord_system_label": "Coordinate system:",
    "auto_detect": "Auto-detect",
    "threads_label": "Face processing threads:", # Renamed
    "threads_tooltip": "Number of parallel threads for processing faces of ONE camera", # Updated tooltip
    "camera_threads_label": "Camera processing threads:", # New label
    "camera_threads_tooltip": "Number of parallel threads for converting DIFFERENT cameras", # New tooltip
    "image_group": "Image Parameters",
    "format_label": "File format:",
    "quality_label": "Quality:",
    "interp_label": "Interpolation:",
    "nearest": "Nearest (faster, lower quality)",
    "linear": "Linear (average)",
    "cubic": "Cubic (slower, better quality)",
    "project_info_group": "Project Information",
    "cameras_count_label": "Number of detected cameras:",
    "detected_system_label": "Detected coordinate system:",
    "system_not_detected": "Not detected",
    "progress_group": "Processing Progress",
    "current_camera_label": "Current camera:",
    "no_camera": "None",
    "status_label": "Status:",
    "waiting_start": "Waiting to start",
    "time_remaining_label": "Time remaining:",
    "time_format": "--:--:--",
    "start_button": "Start",
    "stop_button": "Stop",
    "close_button": "Close",
    "status_ready": "Ready",
    "select_output_folder": "Select output folder for images",
    "error_title": "Error",
    "no_chunk_error": "Active chunk not found.",
    "no_output_folder": "Please select a valid output folder.",
    "no_cameras_error": "No spherical cameras found for processing.",
    "processing_status": "Processing...",
    "processing_info": "Processing {0} cameras using {1} threads...",
    "completed_title": "Completed",
    "processing_completed": "Processing completed!",
    "total_cameras": "Total cameras: {0}",
    "successfully_processed": "Successfully processed: {0}",
    "skipped_errors": "Skipped/errors: {0}",
    "total_time": "Total time: {0}",
    "errors_count": "Errors ({0}):",
    "more_errors": "... and {0} more errors.",
    "aborted_title": "Aborted",
    "processing_aborted_message": "Processing aborted by user.",
    "aborted_status": "Aborted",
    "processing_aborted_status": "Processing aborted by user",
    "processing_status_message": "Processing {0} cameras...",
    "processing_result": "Processing complete. Success: {0}, Errors: {1}",
    "error_status": "Error",
    "processing_error": "Processing error",
    "confirm_exit": "Confirmation",
    "confirm_exit_message": "Processing is not complete. Are you sure you want to exit?",
    "confirm_abort": "Are you sure you want to abort processing?",
    "language_label": "Interface language:",
    "russian": "Русский",
    "english": "English"
})

if 'PyQt5' in sys.modules:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QProgressBar, QFileDialog, QCheckBox, 
                               QMessageBox, QComboBox, QSpinBox, QDoubleSpinBox, QGroupBox)
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
    
    class CubemapConverterGUI(QMainWindow):
        def __init__(self):
            super().__init__()
            # Получаем количество CPU перед инициализацией UI
            self.cpu_count = os.cpu_count() or 1
            self.init_ui()
            self.process_thread = None

        def init_ui(self):
            """Инициализация пользовательского интерфейса"""
            # Настройка основного окна
            self.setWindowTitle(_("gui_title"))
            self.setGeometry(100, 100, 800, 650) # Немного увеличим высоту окна

            # Основной виджет и компоновка
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            main_layout = QVBoxLayout(central_widget)

            # Группа настроек
            settings_group = QGroupBox(_("settings_group"))
            settings_layout = QVBoxLayout()

            # Выбор выходной папки
            output_folder_layout = QHBoxLayout()
            self.output_folder_label = QLabel(_("output_folder_label"))
            self.output_folder_path = QLabel(_("not_selected"))
            self.output_folder_path.setStyleSheet("font-weight: bold;")
            self.browse_button = QPushButton(_("browse_button"))
            self.browse_button.clicked.connect(self.select_output_folder)

            output_folder_layout.addWidget(self.output_folder_label)
            output_folder_layout.addWidget(self.output_folder_path, 1)
            output_folder_layout.addWidget(self.browse_button)
            settings_layout.addLayout(output_folder_layout)

            # Настройка перекрытия
            overlap_layout = QHBoxLayout()
            overlap_label = QLabel(_("overlap_label"))
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
            size_label = QLabel(_("face_size_label"))
            self.size_combo = QComboBox()
            self.size_combo.addItem(_("auto_size"), None)
            for size in [512, 1024, 2048, 4096]: # Removed 8192 from GUI for consistency
                self.size_combo.addItem(f"{size}x{size}", size)
            self.size_combo.setCurrentIndex(0)  # Автоматически по умолчанию

            size_layout.addWidget(size_label)
            size_layout.addWidget(self.size_combo)
            settings_layout.addLayout(size_layout)

            # Выбор координатной системы
            coord_system_layout = QHBoxLayout()
            coord_system_label = QLabel(_("coord_system_label"))
            self.coord_system_combo = QComboBox()
            self.coord_system_combo.addItems(["Y_UP", "Z_UP", "X_UP", _("auto_detect")])
            self.coord_system_combo.setCurrentText(_("auto_detect"))

            coord_system_layout.addWidget(coord_system_label)
            coord_system_layout.addWidget(self.coord_system_combo)
            settings_layout.addLayout(coord_system_layout)
            
            # Настройка многопоточности
            thread_layout = QHBoxLayout()
            thread_label = QLabel(_("threads_label"))
            self.thread_spinner = QSpinBox()
            self.thread_spinner.setRange(1, os.cpu_count() or 4)
            self.thread_spinner.setValue(min(6, os.cpu_count() or 1))
            self.thread_spinner.setToolTip(_("threads_tooltip"))
            
            thread_layout.addWidget(thread_label)
            thread_layout.addWidget(self.thread_spinner)
            settings_layout.addLayout(thread_layout)
            
            settings_group.setLayout(settings_layout)
            main_layout.addWidget(settings_group)
            
            # Группа параметров изображения
            image_group = QGroupBox(_("image_group"))
            image_layout = QVBoxLayout()
            
            # Выбор формата файла
            format_layout = QHBoxLayout()
            format_label = QLabel(_("format_label"))
            self.format_combo = QComboBox()
            self.format_combo.addItems(["JPEG (JPG)", "PNG", "TIFF"])
            self.format_combo.setCurrentIndex(0)
            
            format_layout.addWidget(format_label)
            format_layout.addWidget(self.format_combo)
            image_layout.addLayout(format_layout)
            
            # Выбор качества изображения
            quality_layout = QHBoxLayout()
            quality_label = QLabel(_("quality_label"))
            self.quality_spinner = QSpinBox()
            self.quality_spinner.setRange(75, 100)
            self.quality_spinner.setValue(95)
            self.quality_spinner.setSingleStep(1)
            
            quality_layout.addWidget(quality_label)
            quality_layout.addWidget(self.quality_spinner)
            image_layout.addLayout(quality_layout)
            
            # Выбор интерполяции
            interp_layout = QHBoxLayout()
            interp_label = QLabel(_("interp_label"))
            self.interp_combo = QComboBox()
            self.interp_combo.addItem(_("nearest"), cv2.INTER_NEAREST)
            self.interp_combo.addItem(_("linear"), cv2.INTER_LINEAR)
            self.interp_combo.addItem(_("cubic"), cv2.INTER_CUBIC)
            self.interp_combo.setCurrentIndex(2)  # Кубическая по умолчанию
            
            interp_layout.addWidget(interp_label)
            interp_layout.addWidget(self.interp_combo)
            image_layout.addLayout(interp_layout)
            
            image_group.setLayout(image_layout)
            main_layout.addWidget(image_group)
            
            faces_group = QGroupBox(_("select_faces_title"))
            faces_layout = QVBoxLayout()
        
            faces_label = QLabel(_("select_faces_label"))
            faces_layout.addWidget(faces_label)
        
            # Создаем чекбоксы для каждой грани
            self.face_checkboxes = {}
            for face_key, face_label in [
                ("front", _("face_front")),
                ("right", _("face_right")),
                ("left", _("face_left")),
                ("top", _("face_top")),
                ("down", _("face_down")),
                ("back", _("face_back"))
            ]:
                checkbox = QCheckBox(face_label)
                checkbox.setChecked(True)  # По умолчанию все грани выбраны
                self.face_checkboxes[face_key] = checkbox
                faces_layout.addWidget(checkbox)
        
            faces_group.setLayout(faces_layout)
            main_layout.addWidget(faces_group)
        
            # Добавляем группу опций пост-обработки
            post_group = QGroupBox(_("post_processing_group"))
            post_layout = QVBoxLayout()
        
            # Опция повторного выравнивания
            self.realign_checkbox = QCheckBox(_("realign_cameras"))
            post_layout.addWidget(self.realign_checkbox)
        
            # Опция удаления исходных камер
            self.remove_spherical_checkbox = QCheckBox(_("remove_spherical"))
            post_layout.addWidget(self.remove_spherical_checkbox)
        
            post_group.setLayout(post_layout)
            main_layout.addWidget(post_group)
            
            # Информация о проекте
            info_group = QGroupBox(_("project_info_group"))
            info_layout = QVBoxLayout()
            
            # Количество камер
            camera_count_layout = QHBoxLayout()
            camera_count_label = QLabel(_("cameras_count_label"))
            self.camera_count_value = QLabel("0")
            self.camera_count_value.setStyleSheet("font-weight: bold;")
            camera_count_layout.addWidget(camera_count_label)
            camera_count_layout.addWidget(self.camera_count_value)
            info_layout.addLayout(camera_count_layout)
            
            # Определённая координатная система
            detected_system_layout = QHBoxLayout()
            detected_system_label = QLabel(_("detected_system_label"))
            self.detected_system_value = QLabel(_("system_not_detected"))
            self.detected_system_value.setStyleSheet("font-weight: bold;")
            detected_system_layout.addWidget(detected_system_label)
            detected_system_layout.addWidget(self.detected_system_value)
            info_layout.addLayout(detected_system_layout)
            
            info_group.setLayout(info_layout)
            main_layout.addWidget(info_group)
            
            # Прогресс обработки
            progress_group = QGroupBox(_("progress_group"))
            progress_layout = QVBoxLayout()
            
            # Общий прогресс
            self.progress_bar = QProgressBar()
            progress_layout.addWidget(self.progress_bar)
            
            # Текущая камера и статус
            current_camera_layout = QHBoxLayout()
            current_camera_label = QLabel(_("current_camera_label"))
            self.current_camera_value = QLabel(_("no_camera"))
            current_camera_layout.addWidget(current_camera_label)
            current_camera_layout.addWidget(self.current_camera_value, 1)
            progress_layout.addLayout(current_camera_layout)
            
            # Статус обработки
            status_layout = QHBoxLayout()
            status_label = QLabel(_("status_label"))
            self.status_value = QLabel(_("waiting_start"))
            status_layout.addWidget(status_label)
            status_layout.addWidget(self.status_value, 1)
            progress_layout.addLayout(status_layout)
            
            # Оставшееся время
            time_layout = QHBoxLayout()
            time_label = QLabel(_("time_remaining_label"))
            self.time_value = QLabel(_("time_format"))
            time_layout.addWidget(time_label)
            time_layout.addWidget(self.time_value)
            progress_layout.addLayout(time_layout)
            
            progress_group.setLayout(progress_layout)
            main_layout.addWidget(progress_group)
            
            # Кнопки управления
            buttons_layout = QHBoxLayout()
            
            self.start_button = QPushButton(_("start_button"))
            self.start_button.clicked.connect(self.start_processing)
            self.start_button.setMinimumWidth(120)
            
            self.stop_button = QPushButton(_("stop_button"))
            self.stop_button.clicked.connect(self.stop_processing)
            self.stop_button.setEnabled(False)
            self.stop_button.setMinimumWidth(120)
            
            self.close_button = QPushButton(_("close_button"))
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
            self.status_bar.showMessage(_("status_ready"))
            
            # Обновить информацию о проекте при запуске
            QTimer.singleShot(100, self.update_project_info)
        
        def select_output_folder(self):
            """Выбор папки для сохранения изображений"""
            folder = QFileDialog.getExistingDirectory(self, _("select_output_folder"))
            if folder:
                self.output_folder_path.setText(normalize_path(folder))
                
        def update_project_info(self):
            """Обновляет информацию о проекте"""
            try:
                doc = Metashape.app.document
                chunk = doc.chunk
                
                if not chunk:
                    QMessageBox.warning(self, _("error_title"), _("no_chunk_error"))
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
                        self.detected_system_value.setText(_("system_not_detected"))
                else:
                    self.status_bar.showMessage(_("no_cameras_error"))
                    self.detected_system_value.setText(_("system_not_detected"))
            
            except Exception as e:
                QMessageBox.warning(self, _("error_title"), f"{str(e)}")
        
        @staticmethod
        def show_window():
            """Создает и показывает окно GUI"""
            global gui_window
            
            # Если окно уже существует, закрываем его
            if gui_window is not None:
                gui_window.close()
                
            # Создаем новое окно
            gui_window = CubemapConverterGUI()
            gui_window.show()
            
            return gui_window
                
        def start_processing(self):
            """Запускает процесс обработки камер"""
            try:
                # Проверяем выходную папку
                output_folder = self.output_folder_path.text()
                if output_folder == _("not_selected") or not os.path.exists(output_folder):
                    QMessageBox.warning(self, _("error_title"), _("no_output_folder"))
                    return
                
                # Получаем выбранные грани
                selected_faces = [face for face, checkbox in self.face_checkboxes.items() if checkbox.isChecked()]
            
                # Проверяем, что хотя бы одна грань выбрана
                if not selected_faces:
                    QMessageBox.warning(self, _("error_title"), _("select_at_least_one"))
                    return
            
                # Получаем настройки пост-обработки
                realign_cameras_after = self.realign_checkbox.isChecked()
                remove_spherical_cameras_after = self.remove_spherical_checkbox.isChecked()
                
                # Получаем настройки из интерфейса
                overlap = self.overlap_spinner.value()
                persp_size = self.size_combo.currentData()  # None для автоматического размера
                
                # Получаем выбранную координатную систему
                coord_system_option = self.coord_system_combo.currentText()
                if coord_system_option == _("auto_detect"):
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
                    QMessageBox.warning(self, _("error_title"), _("no_chunk_error"))
                    return
                
                spherical_cameras = [cam for cam in chunk.cameras if cam.transform and cam.photo]
                
                if not spherical_cameras:
                    QMessageBox.warning(self, _("error_title"), _("no_cameras_error"))
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
                        "faces_threads": faces_threads,
                        "selected_faces": selected_faces,               # Эти параметры отсутствуют
                        "realign_cameras_after": realign_cameras_after, # в текущей версии кода
                        "remove_spherical_cameras_after": remove_spherical_cameras_after
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
                self.status_value.setText(_("processing_status"))
                self.status_bar.showMessage(_("processing_info").format(len(spherical_cameras), faces_threads))
                
                # Запускаем поток
                self.process_thread.start()
                
                # Запускаем таймер для обновления оставшегося времени
                self.start_time = time.time()
                self.timer = QTimer()
                self.timer.timeout.connect(self.update_remaining_time)
                self.timer.start(1000)  # Обновляем каждую секунду
            
            except Exception as e:
                error_message = f"{str(e)}\n\n{traceback.format_exc()}"
                print(error_message)
                QMessageBox.critical(self, _("error_title"), error_message)
        
        def stop_processing(self):
            """Останавливает процесс обработки"""
            if self.process_thread and self.process_thread.isRunning():
                reply = QMessageBox.question(
                    self, _("confirm_exit"), 
                    _("confirm_abort"), 
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.status_value.setText(_("aborted_status"))
                    self.status_bar.showMessage(_("processing_aborted_status"))
                    self.process_thread.stop()
                    
        def update_progress(self, current, total, camera_name, status, progress_percent):
            """Обновляет информацию о прогрессе"""
            self.progress_bar.setValue(progress_percent)
            self.current_camera_value.setText(camera_name)
            self.status_value.setText(status)
            self.status_bar.showMessage(_("processing_status_message").format(total))
        
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
                message = f"{_('processing_completed')}\n\n"
                message += f"{_('total_cameras')}\n"
                message += f"{_('successfully_processed').format(stats['processed'])}\n"
                message += f"{_('skipped_errors').format(stats['skipped'])}\n"
                message += f"{_('total_time').format(format_time(stats['time']))}"
                
                if stats['skipped'] > 0 and 'errors' in stats and stats['errors']:
                    message += f"\n\n{_('errors_count').format(len(stats['errors']))}\n"
                    for i, error in enumerate(stats['errors'][:5]):  # Показываем первые 5 ошибок
                        message += f"{i+1}. {error}\n"
                    if len(stats['errors']) > 5:
                        message += f"{_('more_errors').format(len(stats['errors']) - 5)}"
                
                QMessageBox.information(self, _("completed_title"), message)
                self.status_value.setText(_("completed_title"))
                self.status_bar.showMessage(_("processing_result").format(stats['processed'], stats['skipped']))
            else:
                message = _("processing_aborted_message")
                QMessageBox.warning(self, _("aborted_title"), message)
                self.status_value.setText(_("aborted_status"))
                self.status_bar.showMessage(_("processing_aborted_status"))
        
        def processing_error(self, error_message):
            """Вызывается при возникновении ошибки в процессе обработки"""
            QMessageBox.critical(self, _("error_title"), f"{error_message}")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.status_value.setText(_("error_status"))
            self.status_bar.showMessage(_("processing_error"))
            
        def closeEvent(self, event):
            """Обрабатывает закрытие окна"""
            if self.process_thread and self.process_thread.isRunning():
                reply = QMessageBox.question(
                    self, _("confirm_exit"), 
                    _("confirm_exit_message"), 
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.process_thread.stop()
                    self.process_thread.wait(1000)  # Даем немного времени на завершение
                    event.accept()
                else:
                    event.ignore()

# === Часть 7: Консольная обработка и главная функция ===

# Добавляем переводы для этой части
translations["ru"].update({
    "console_start": "=== Конвертация сферических изображений в кубическую проекцию ===",
    "version_info": "Версия {0} - {1}",
    "checking_chunk": "Проверка активного чанка...",
    "no_active_chunk": "Не найден активный чанк в документе.",
    "checking_spherical_cameras": "Проверка сферических камер...",
    "no_spherical_cameras": "Не найдено сферических камер для обработки.",
    "found_cameras": "Найдено {0} сферических камер.",
    "select_output_folder_console": "Выберите папку для сохранения изображений",
    "enter_overlap": "Введите значение перекрытия (0-20)",
    "overlap_value_error": "Значение перекрытия должно быть в диапазоне от 0 до 20.",
    "select_face_size": "Выберите размер грани куба",
    "select_file_format": "Выберите формат файла (jpg, png, tiff)",
    "select_quality": "Введите качество изображения (75-100)",
    "select_interpolation": "Выберите метод интерполяции",
    "nearest_option": "Ближайшая",
    "linear_option": "Линейная",
    "cubic_option": "Кубическая",
    "determined_coord_system": "Определена координатная система: {0}",
    "select_threads": "Количество потоков для граней (рекомендуется {0}):", # Renamed
    "invalid_threads": "Некорректный ввод. Используется {0} потоков для граней.", # Updated message
    "select_camera_threads": "Количество потоков для камер (рекомендуется {0}):", # New
    "invalid_camera_threads": "Некорректный ввод. Используется {0} потоков для камер.", # New
    "processing_start": "Начало обработки {0} камер используя {1} потоков...",
    "processing_settings": "Настройки: перекрытие={0}, размер грани={1}, система={2}",
    "format_quality_interp": "Формат={0}, качество={1}, интерполяция={2}",
    "info_message_title": "Информация",
    "processing_info_message": "Начало обработки {0} камер.\n\nНастройки:\n- Перекрытие: {1} градусов\n- Размер грани: {2}\n- Координатная система: {3}\n- Формат файла: {4}\n- Качество: {5}\n- Интерполяция: {6}\n- Потоков: {7}\n\nРезультаты будут сохранены в:\n{8}",
    "processing_camera_console": "[{0}/{1}] Обработка {2}...",
    "general_progress": "Общий прогресс:",
    "camera_success": "  Успешно обработана камера {0}",
    "progress_info": "Прогресс: {0:.1f}% | Прошло: {1} | Осталось: {2}",
    "processing_complete_title": "Обработка завершена",
    "final_report": "==== Итоги обработки ====",
    "init_gui": "Инициализация графического интерфейса...",
    "gui_launched": "Графический интерфейс запущен успешно",
    "non_blocking_mode": "Запуск интерфейса в не блокирующем режиме?",
    "non_blocking_selected": "Выбран не блокирующий режим",
    "blocking_selected": "Выбран блокирующий режим",
    "qt_event_loop_start": "Запуск цикла обработки событий Qt...",
    "qt_event_loop_end": "Цикл обработки событий Qt завершен",
    "gui_init_error": "Ошибка инициализации GUI: {0}",
    "switch_to_console": "Переключение в консольный режим.",
    "info_success_message": "Информация",
    "gui_success_message": "Интерфейс успешно запущен. Если вы видите это сообщение, то все работает корректно."
})

translations["en"].update({
    "console_start": "=== Spherical to Cubemap Image Conversion ===",
    "version_info": "Version {0} - {1}",
    "checking_chunk": "Checking active chunk...",
    "no_active_chunk": "No active chunk found in document.",
    "checking_spherical_cameras": "Checking spherical cameras...",
    "no_spherical_cameras": "No spherical cameras found for processing.",
    "found_cameras": "Found {0} spherical cameras.",
    "select_output_folder_console": "Select output folder for saving images",
    "enter_overlap": "Enter overlap value (0-20)",
    "overlap_value_error": "Overlap value should be between 0 and 20.",
    "select_face_size": "Select cube face size",
    "select_file_format": "Select file format (jpg, png, tiff)",
    "select_quality": "Enter image quality (75-100)",
    "select_interpolation": "Select interpolation method",
    "nearest_option": "Nearest",
    "linear_option": "Linear",
    "cubic_option": "Cubic",
    "determined_coord_system": "Determined coordinate system: {0}",
    "select_threads": "Number of face threads (recommended {0}):", # Renamed
    "invalid_threads": "Invalid input. Using {0} face threads.", # Updated message
    "select_camera_threads": "Number of camera threads (recommended {0}):", # New
    "invalid_camera_threads": "Invalid input. Using {0} camera threads.", # New
    "processing_start": "Starting processing {0} cameras using {1} threads...",
    "processing_settings": "Settings: overlap={0}, face size={1}, system={2}",
    "format_quality_interp": "Format={0}, quality={1}, interpolation={2}",
    "info_message_title": "Information",
    "processing_info_message": "Starting processing {0} cameras.\n\nSettings:\n- Overlap: {1} degrees\n- Face size: {2}\n- Coordinate system: {3}\n- File format: {4}\n- Quality: {5}\n- Interpolation: {6}\n- Threads: {7}\n\nResults will be saved to:\n{8}",
    "processing_camera_console": "[{0}/{1}] Processing {2}...",
    "general_progress": "Overall progress:",
    "camera_success": "  Successfully processed camera {0}",
    "progress_info": "Progress: {0:.1f}% | Elapsed: {1} | Remaining: {2}",
    "processing_complete_title": "Processing Complete",
    "final_report": "==== Processing Results ====",
    "init_gui": "Initializing graphical interface...",
    "gui_launched": "Graphical interface launched successfully",
    "non_blocking_mode": "Launch interface in non-blocking mode?",
    "non_blocking_selected": "Non-blocking mode selected",
    "blocking_selected": "Blocking mode selected",
    "qt_event_loop_start": "Starting Qt event processing loop...",
    "qt_event_loop_end": "Qt event processing loop completed",
    "gui_init_error": "GUI initialization error: {0}",
    "switch_to_console": "Switching to console mode.",
    "info_success_message": "Information",
    "gui_success_message": "Interface successfully launched. If you see this message, everything is working correctly."
})

# Модифицируем функцию console_mode для поддержки новых возможностей
def process_images_console():
    """
    Консольная версия функции для обработки изображений.
    Использует многопоточность для ускорения обработки.
    """
    try:
        # Проверяем, есть ли активный документ и чанк
        print(_("checking_chunk"))
        doc = Metashape.app.document
        if not doc:
            show_message(_("error_title"), _("no_active_chunk"))
            return
            
        chunk = doc.chunk
        if not chunk:
            show_message(_("error_title"), _("no_active_chunk"))
            return
            
        # Получаем список сферических камер
        print(_("checking_spherical_cameras"))
        spherical_cameras = [cam for cam in chunk.cameras if cam.transform and cam.photo]
        
        if not spherical_cameras:
            show_message(_("error_title"), _("no_spherical_cameras"))
            return
            
        print(_("found_cameras").format(len(spherical_cameras)))
            
        # Запрос выходной папки
        output_folder = Metashape.app.getExistingDirectory(_("select_output_folder_console"))
        if not output_folder:
            return
        
        # Нормализуем путь для поддержки кириллицы
        output_folder = normalize_path(output_folder)
            
        # Запрос значения перекрытия
        overlap = Metashape.app.getFloat(_("enter_overlap"), 10.0)
        if overlap is None or overlap < 0 or overlap > 20:
            show_message(_("error_title"), _("overlap_value_error"))
            return
            
        # Запрос размера грани куба
        size_options = [_("auto_size"), "512x512", "1024x1024", "2048x2048", "4096x4096"]
        selected_size = get_string_option(_("select_face_size"), size_options)
        
        persp_size = None  # Автоматический размер по умолчанию
        if selected_size != _("auto_size"):
            persp_size = int(selected_size.split("x")[0])
        
        # Запрос формата файла
        format_options = ["jpg", "png", "tiff"]
        file_format = get_string_option(_("select_file_format"), format_options)
        
        # Запрос качества
        quality = Metashape.app.getInt(_("select_quality"), 95, 75, 100)
        
        # Запрос метода интерполяции
        interp_options = [_("nearest_option"), _("linear_option"), _("cubic_option")]
        interp_option = get_string_option(_("select_interpolation"), interp_options)
        
        interpolation = cv2.INTER_CUBIC  # По умолчанию
        if interp_option == _("nearest_option"):
            interpolation = cv2.INTER_NEAREST
        elif interp_option == _("linear_option"):
            interpolation = cv2.INTER_LINEAR
        
        # Добавляем запрос выбранных граней куба
        face_options = ["front", "right", "left", "top", "down", "back"]
        selected_faces = []
        
        for face in face_options:
            face_label = _("face_" + face)
            if Metashape.app.getBool(f"{face_label}?", True):
                selected_faces.append(face)
        
        # Если не выбрано ни одной грани
        if not selected_faces:
            show_message(_("error_title"), _("select_at_least_one"))
            return
            
        # Запрос пост-обработки
        realign_cameras_after = Metashape.app.getBool(_("realign_cameras"), False)
        remove_spherical_cameras_after = Metashape.app.getBool(_("remove_spherical"), False)
            
        # Определяем координатную систему
        coord_system = determine_coordinate_system()
        print(_("determined_coord_system").format(coord_system))
        
        # Запрос количества потоков для ГРАНЕЙ
        cpu_count_local = os.cpu_count() or 1
        recommended_face_threads = min(6, max(1, cpu_count_local // 2))
        face_threads = Metashape.app.getInt(_("select_threads").format(recommended_face_threads), # Use renamed translation key
                                          recommended_face_threads, 1, max(1, cpu_count_local // 2))

        # Запрос количества потоков для КАМЕР (Новый запрос)
        recommended_camera_threads = cpu_count_local
        camera_threads = Metashape.app.getInt(_("select_camera_threads").format(recommended_camera_threads), # New translation key
                                            recommended_camera_threads, 1, cpu_count_local)

        # --- Начало обработки --- 
        print("\n" + _("processing_console_start").format(f'{len(spherical_cameras)} ({camera_threads} {_("camera_threads_label")[:-1]} / {face_threads} {_("threads_label")[:-1]})')) # Updated info
        print(_("processing_settings").format(overlap, selected_size, coord_system))
        print(_("format_quality_interp").format(file_format, quality, interp_option))
        print(_("selected_faces").format(", ".join(selected_faces)))

        start_time = time.time()
        processed_count = 0 # Успешно ДОБАВЛЕННЫЕ
        skipped_count = 0   # Пропущено/ошибки КОНВЕРТАЦИИ
        add_camera_errors_console = [] # Ошибки добавления
        conversion_results_console = []
        futures_console = []

        # Показываем информационное сообщение
        info_message = _("processing_info_message").format(
            len(spherical_cameras),
            overlap,
            selected_size,
            coord_system,
            file_format,
            quality,
            interp_option,
            f"{camera_threads}/{face_threads}", # Show both threads
            output_folder
        )
        show_message(_("info_message_title"), info_message)

        # --- Этап 1: Параллельная Конвертация --- 
        print(f"--- Этап 1: Конвертация изображений ({camera_threads} потоков) ---")
        with concurrent.futures.ThreadPoolExecutor(max_workers=camera_threads) as executor:
            # Вспомогательная функция для консольного режима
            def _process_single_camera_console(camera_idx, cam):
                try:
                    # Вызываем основную функцию конвертации
                    image_paths_c = convert_spherical_to_cubemap(
                        spherical_image_path=cam.photo.path,
                        output_folder=output_folder,
                        camera_label=cam.label,
                        persp_size=persp_size,
                        overlap=overlap,
                        file_format=file_format,
                        quality=quality,
                        interpolation=interpolation,
                        max_workers=face_threads, # Потоки для граней
                        selected_faces=selected_faces
                    )
                    if image_paths_c:
                        first_img = list(image_paths_c.values())[0]
                        img = read_image_with_cyrillic(first_img)
                        # Обработка ошибки чтения изображения
                        actual_size_c = img.shape[0] if img is not None else None
                        if actual_size_c is None:
                             print(f"\nПредупреждение: Не удалось прочитать {first_img} для камеры {cam.label}")
                             # Возвращаем ошибку, если не удалось прочитать
                             return {"camera": cam, "image_paths": image_paths_c, "actual_size": None, "error": f"Read error for {first_img}"}
                        else:
                             return {"camera": cam, "image_paths": image_paths_c, "actual_size": actual_size_c, "error": None}
                    else:
                        return {"camera": cam, "image_paths": None, "actual_size": None, "error": "skipped_no_faces"}
                except Exception as e:
                    return {"camera": cam, "image_paths": None, "actual_size": None, "error": str(e)}

            # Отправляем задачи
            for i, camera in enumerate(spherical_cameras):
                 future = executor.submit(_process_single_camera_console, i, camera)
                 futures_console.append(future)

            # Собираем результаты
            conversion_completed_count_console = 0
            for future in concurrent.futures.as_completed(futures_console):
                result = future.result()
                conversion_completed_count_console += 1
                camera_label_c = result["camera"].label
                if result["error"]:
                    skipped_count += 1
                    if result["error"] != "skipped_no_faces":
                         print(f"\n{_('console_camera_error').format(camera_label_c, result['error'])} ({_('conversion_stage')})")
                    # Не печатаем ошибку, если просто нет граней или ошибка чтения (уже напечатана)
                    elif not result["error"].startswith("Read error"):
                         pass 
                else:
                    conversion_results_console.append(result)

                # Обновляем прогресс бар консоли
                console_progress_bar(conversion_completed_count_console, len(spherical_cameras), prefix=f"[{_('conversion_stage')}] ", suffix=f"{conversion_completed_count_console}/{len(spherical_cameras)}", length=40)

        # Завершаем прогресс бар для этапа конвертации
        console_progress_bar(len(spherical_cameras), len(spherical_cameras), prefix=f"[{_('conversion_stage')}] ", suffix=f" {_('processing_complete')}", length=40)
        print() # Новая строка после прогресс бара

        # --- Этап 2: Последовательное Добавление камер --- 
        print(f"--- Этап 2: Добавление камер в Metashape (Последовательно) ---")
        total_to_add_console = len(conversion_results_console)
        added_count_console = 0
        if total_to_add_console > 0:
            chunk_c = Metashape.app.document.chunk # Получаем чанк
            for result in conversion_results_console:
                added_count_console += 1
                console_progress_bar(added_count_console, total_to_add_console, prefix=f"[{_('adding_cube_cameras_stage').format('', added_count_console, total_to_add_console)}] ", suffix=f"{result['camera'].label}", length=40)
                try:
                    # Проверяем, что actual_size не None перед добавлением
                    if result["actual_size"] is None:
                        raise ValueError("Actual size is None, cannot add camera.")
                    add_cubemap_cameras(
                        chunk=chunk_c,
                        spherical_camera=result["camera"],
                        image_paths=result["image_paths"],
                        persp_size=result["actual_size"],
                        coord_system=coord_system
                    )
                    processed_count += 1
                except Exception as e:
                     error_msg_add = _('add_camera_error').format(result['camera'].label, str(e))
                     print(f"\n{error_msg_add}")
                     add_camera_errors_console.append(error_msg_add)
                     # processed_count не увеличивается

            # Завершаем прогресс бар для этапа добавления
            console_progress_bar(total_to_add_console, total_to_add_console, prefix=f"[{_('adding_cube_cameras_stage').format('', total_to_add_console, total_to_add_console)}] ", suffix=f" {_('processing_complete')}", length=40)
            print() # Новая строка

        # --- Этап 3: Пост-обработка --- 
        print("--- Этап 3: Пост-обработка ---")
        if realign_cameras_after:
            try:
                print(_("realigning_cameras"))
                realign_cameras()
            except Exception as e:
                print(f"Ошибка при повторном выравнивании камер: {str(e)}")

        if remove_spherical_cameras_after:
            try:
                print(_("removing_spherical"))
                remove_spherical_cameras()
            except Exception as e:
                 print(f"Ошибка при удалении сферических камер: {str(e)}")

        # --- Завершение обработки --- 
        end_time_total = time.time()
        final_skipped_console = skipped_count + (total_to_add_console - processed_count) # Ошибки конвертации + (Сконвертировано, но не добавлено)
        print("\n" + _("final_report"))
        print(_("total_cameras").format(len(spherical_cameras)))
        print(_("successfully_processed").format(processed_count))
        print(_("skipped_errors").format(final_skipped_console))
        # Печатаем ошибки добавления/пост-обработки, если были
        if add_camera_errors_console:
            print(_("errors_count").format(len(add_camera_errors_console)))
            for err in add_camera_errors_console:
                print(f"- {err}")
        print(_("total_time_console").format(format_time(end_time_total - start_time)))

    except Exception as e:
        error_message = f"{str(e)}\n\n{traceback.format_exc()}"
        print(error_message)
        try:
            show_message(_("error_title"), f"{_('general_processing_error').format(str(e))}")
        except:
            print(_("error_showing_message").format(str(e)))

# === Глобальная переменная для хранения окна GUI ===
gui_window = None

# === Основная функция запуска ===
def main():
    """
    Главная функция для запуска из Metashape.
    Определяет язык интерфейса Metashape, настраивает локаль/кодировки,
    выбирает GUI или консольный режим в зависимости от доступности PyQt5.
    """
    global gui_window, LANG # Добавляем LANG в global

    # Настройка локали и кодировок (без определения языка)
    setup_locale_and_encoding()

    # Модификация методов Metashape для поддержки кириллицы
    fix_metashape_file_paths()

    # --- Определение языка интерфейса ---
    try:
        # Проверяем, запущен ли скрипт внутри Metashape
        if Metashape and Metashape.app and Metashape.app.document:
            app_lang_code = Metashape.app.settings.language
            log_message(f"Metashape language code detected: {app_lang_code}")
            if app_lang_code and app_lang_code.lower() == 'ru':
                LANG = 'ru'
            else: # Для 'en' и любого другого языка используем 'en'
                LANG = 'en'
        else:
            # Запуск вне Metashape или до инициализации документа - используем системный язык
            log_message("Running outside Metashape or before document init. Using system language for fallback.")
            system_lang, unused_encoding = locale.getdefaultlocale() # Используем другое имя вместо _
            if system_lang and system_lang.startswith('ru'):
                LANG = 'ru'
            else:
                LANG = 'en' # По умолчанию английский
    except Exception as e:
        log_message(f"Error detecting Metashape/system language: {e}. Defaulting to English.")
        LANG = 'en' # По умолчанию английский при любой ошибке

    log_message(f"Script language set to: {LANG}")
    print(f"--- {_('script_title')} ---") # Используем _() уже после определения LANG
    print(_("version_info").format("1.0.1", _("optimized"))) # Обновим версию для примера

    # Проверяем возможность использования GUI
    if use_gui:
        try:
            print(_("init_gui"))
            # Инициализация QApplication
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            # Создание и отображение окна
            gui_window = CubemapConverterGUI()
            gui_window.show()
            
            # Запускаем главный цикл событий Qt
            print(_("gui_launched"))

            # Запрашиваем режим запуска
            try:
                # Убираем запрос окна и используем неблокирующий режим по умолчанию
                # non_blocking = Metashape.app.getBool(_("non_blocking_mode"))
                non_blocking = True # По умолчанию неблокирующий
                if non_blocking:
                    print(_("non_blocking_selected"))
                    # Показываем сообщение об успешном запуске через 1 секунду, если нужно
                    # def show_success_message():
                    #     QMessageBox.information(None, _(\"info_success_message\"),
                    #                         _(\"gui_success_message\"))
                    # QTimer.singleShot(1000, show_success_message) # Убираем сообщение
                else:
                     print(_("blocking_selected"))
                     # Для блокирующего режима запускаем цикл событий
                     print(_("qt_event_loop_start"))
                     app.exec_()
                     print(_("qt_event_loop_end"))

            except AttributeError:
                # Если Metashape.app недоступно (запуск вне Metashape), getBool вызовет AttributeError
                print(_("running_outside_metashape"))
                print(_("qt_event_loop_start"))
                app.exec_() # Запускаем обычный цикл событий
                print(_("qt_event_loop_end"))
            except Exception as e:
                 # Обработка других возможных ошибок при запросе режима
                 print(_("non_blocking_query_error").format(str(e)))
                 print(_("defaulting_to_non_blocking")) # По умолчанию неблокирующий режим
                 # Показываем сообщение об успешном запуске через 1 секунду, если нужно
                 # def show_success_message():
                 #      QMessageBox.information(None, _(\"info_success_message\"),
                 #                          _(\"gui_success_message\"))
                 # QTimer.singleShot(1000, show_success_message) # Убираем сообщение

        except Exception as e:
            print(_("gui_init_error").format(str(e)))
            print(traceback.format_exc())
            print(_("switch_to_console"))
            process_images_console()
    else:
        # Запускаем консольный режим, если GUI недоступен
        # Убедимся, что язык определен (хотя это должно было случиться выше)
        if not LANG: 
             system_lang, unused_encoding = locale.getdefaultlocale() # Используем другое имя вместо _
             LANG = 'ru' if system_lang and system_lang.startswith('ru') else 'en'
             log_message(f"Setting language for console mode: {LANG}")
        process_images_console()

# Запуск скрипта
if __name__ == "__main__":
    main()