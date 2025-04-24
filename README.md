# Metashape Spherical to Cubemap Converter v012

A Python script for Agisoft Metashape Pro that converts a set of spherical (equirectangular) images into separate images for the faces of a cubemap projection (front, back, left, right, top, bottom). It creates new cameras in Metashape for each cube face, inheriting the position and orientation of the original spherical camera.

Version 012 includes stability and memory management improvements, especially when dealing with a large number of cameras.

## Features

*   **Graphical User Interface (GUI)**: User-friendly interface based on PyQt5 for easy parameter configuration and progress monitoring.
*   **Console Mode**: Ability to run without a GUI, prompting for parameters via standard Metashape dialogs.
*   **Multithreading**: Parallel processing to speed up conversion:
    *   Parallel processing of faces for a *single* camera.
    *   Parallel processing of *multiple* cameras simultaneously (configurable).
*   **Face Selection**: Option to generate only specific cube faces.
*   **Parameter Customization**: Control overlap, face size, file format (JPG, PNG, TIFF), compression quality, interpolation method.
*   **Coordinate System Detection**: Automatic detection of the project's primary orientation (Y-Up, Z-Up, X-Up) for correct camera creation.
*   **Post-processing Options**: Optional realignment of cameras and removal of original spherical cameras after conversion.
*   **Cyrillic Path Support**: Correct handling of file paths containing non-Latin characters.
*   **Automatic Dependency Installation**: Checks and attempts to install missing `opencv-python` and `PyQt5` libraries.
*   **Multilingual**: Interface available in English and Russian (automatically detected based on Metashape settings).

## Requirements

*   **Agisoft Metashape Pro**: Version 1.6 or newer recommended.
*   **Python**: Version 3.x (typically bundled with Metashape).
*   **Python Libraries**:
    *   `opencv-python` (cv2)
    *   `PyQt5` (for the GUI)
    *   *(The script will attempt to install these automatically on first run if missing)*

## Installation

1.  Download the script file (`convert_to_cubemap_v012.py`).
2.  On the first run, the script will check for necessary libraries (`opencv-python`, `PyQt5`).
3.  If libraries are missing, it will attempt to install them using `pip`. Administrator privileges or internet access might be required.
4.  If `pip` installation fails (e.g., due to network or permission issues), you may need to install the libraries manually into the Python environment used by Metashape.

## Usage

1.  Open your project in Agisoft Metashape Pro.
2.  Ensure you have an active chunk containing the spherical cameras you wish to convert.
3.  Run the script via the Metashape menu: `Tools -> Scripts -> Run Script...` and select the `convert_to_cubemap_v012.py` file.

### Graphical User Interface (GUI)

If `PyQt5` is available, the graphical interface will launch:

*   **Settings**:
    *   `Output folder`: Specify the directory to save the generated face images.
    *   `Overlap (degrees)`: Set the overlap angle between faces (useful for stitching later).
    *   `Cube face size`: Select the resolution for each cube face. "Automatically" is recommended (uses source width / 4).
    *   `Coordinate system`: Choose "Auto-detect" or manually select the project's coordinate system.
    *   `Face processing threads`: Number of threads for parallel conversion of faces for **one** spherical camera.
    *   `Camera processing threads`: Number of threads for parallel conversion of **different** spherical cameras simultaneously. **See the Threading Guide below!**
*   **Image Parameters**:
    *   `File format`: JPG, PNG, or TIFF.
    *   `Quality`: For JPG (75-100).
    *   `Interpolation`: Resampling method during remapping (Cubic is best quality, Nearest is fastest).
*   **Cube Face Selection**: Check the boxes for the faces you want to generate.
*   **Post-conversion Processing**:
    *   `Realign cameras`: Run `Align Cameras` after adding the new cube cameras.
    *   `Remove original spherical cameras`: Delete the original cameras after successful conversion.
*   **Project Information**: Displays the number of cameras found and the detected coordinate system.
*   **Processing Progress**: Shows overall progress, current operation, and estimated time remaining.
*   **Control Buttons**: "Start", "Stop", "Close".

### Console Mode

If `PyQt5` is unavailable, the script will run in console mode, prompting for parameters sequentially via standard Metashape dialogs. Progress will be displayed in the console.

### Threading Guide

The script uses two parameters to control multithreading:

1.  **Face processing threads**:
    *   **What it does**: Determines how many faces (e.g., front, back, top...) of a **single** spherical camera are processed in parallel during the image conversion stage (`cv2.remap`).
    *   **Impact**: Increasing this speeds up the conversion of *each individual* spherical camera but increases RAM and CPU load *during* that camera's processing.
    *   **Recommendations**: The default (`min(6, CPU_cores // 2)`) is a reasonable starting point. If you experience memory issues *during* a single camera's conversion (before it's added to Metashape), try reducing this value (e.g., to 2-4).

2.  **Camera processing threads**:
    *   **What it does**: Determines how many **different** spherical cameras are converted *simultaneously*. E.g., a value of 4 means the script attempts to convert four different spherical cameras in parallel.
    *   **Impact**: Increasing this can significantly speed up the overall processing of *many* cameras but **greatly increases peak RAM usage** as resources are needed for multiple simultaneous conversions.
    *   **Recommendations**:
        *   **For systems with ample RAM (e.g., 64GB+)**: You can experiment with values up to the number of CPU cores or slightly more if disk I/O is fast.
        *   **❗️ For systems with limited RAM (e.g., 16-32GB or less) ❗️**: It is **strongly recommended to set this value to 1**. This forces the script to process spherical cameras **sequentially**, one after another. Peak RAM usage will then be primarily determined by processing the faces of *one* camera (controlled by the first setting), which is much more stable.
        *   **Successful low-RAM example**:
            *   Camera processing threads: **1**
            *   Face processing threads: **5** (or another moderate value like 4 or 6)
            *   In this case, cameras are converted one by one, but each camera uses 5 threads to process its faces quickly.

## Localization

The script automatically detects the Metashape interface language (`ru` or `en`) and applies corresponding translations. English is used as a fallback for other languages.

## Troubleshooting

*   **Dependency Installation Issues**: Ensure internet access and permissions to install Python packages. Try installing `opencv-python` and `PyQt5` manually via `pip` in Metashape's Python environment.
*   **High RAM Usage / Crashes**: Reduce the number of threads, especially **"Camera processing threads"** (set it to **1**). You might also reduce "Face processing threads".
*   **Path Issues (Cyrillic/Non-ASCII)**: The script includes path normalization, but if issues persist, ensure project and image paths do not contain highly unusual or invalid characters.

## Version History

*   **v012 (Current)**:
    *   Restored threaded camera processing (`ProcessCamerasThread`) for stability.
    *   Added explicit memory management (`del`, `gc.collect()`) to reduce RAM usage.
    *   Introduced separate controls for "Camera processing threads" and "Face processing threads".
    *   Updated recommendations for thread settings, especially for low-RAM systems.
*   **v0.11.x (Previous attempts)**: Various changes including GUI improvements, face selection, post-processing options, Cyrillic path support, dependency installation, non-threaded experiments.
*   **(Older versions)**: Basic console functionality.

## Acknowledgments

*   Agisoft for the Metashape Python API.
*   OpenCV library for image processing capabilities.
*   PyQt5 framework for the graphical user interface.

---


---

# Конвертер Сферических Изображений в Кубическую Проекцию v012 для Metashape

Этот скрипт для Agisoft Metashape Pro преобразует набор сферических (эквиректангулярных) изображений в отдельные изображения для граней кубической проекции (передняя, задняя, левая, правая, верхняя, нижняя). Он создает новые камеры в Metashape для каждой грани куба, копируя положение и ориентацию исходной сферической камеры.

Версия 012 включает улучшения стабильности и управления памятью, особенно при работе с большим количеством камер.

## Основные возможности

*   **Графический интерфейс (GUI)**: Удобный интерфейс на базе PyQt5 для настройки параметров и отслеживания прогресса.
*   **Консольный режим**: Возможность работы без GUI, с запросом параметров через стандартные диалоги Metashape.
*   **Многопоточность**: Параллельная обработка для ускорения конвертации:
    *   Параллельная обработка граней *одной* камеры.
    *   Параллельная обработка *нескольких* камер одновременно (настраивается).
*   **Выбор граней**: Возможность генерировать только нужные грани куба.
*   **Настройка параметров**: Контроль перекрытия, размера граней, формата файла (JPG, PNG, TIFF), качества сжатия, метода интерполяции.
*   **Определение системы координат**: Автоматическое определение основной ориентации проекта (Y-Up, Z-Up, X-Up) для корректного создания камер.
*   **Пост-обработка**: Опциональное повторное выравнивание камер и удаление исходных сферических камер после конвертации.
*   **Поддержка кириллицы**: Корректная работа с путями, содержащими не-латинские символы.
*   **Автоматическая установка зависимостей**: Скрипт проверяет и пытается установить недостающие библиотеки `opencv-python` и `PyQt5`.
*   **Многоязычность**: Интерфейс доступен на русском и английском языках (автоматическое определение по настройкам Metashape).

## Требования

*   **Agisoft Metashape Pro**: Версия 1.6 или новее (рекомендуется последняя).
*   **Python**: Версия 3.x (обычно поставляется с Metashape).
*   **Библиотеки Python**:
    *   `opencv-python` (cv2)
    *   `PyQt5` (для графического интерфейса)
    *   *(Скрипт попытается установить их автоматически при первом запуске, если они отсутствуют)*

## Установка

1.  Скачайте файл скрипта (`convert_to_cubemap_v012.py`).
2.  При первом запуске скрипт проверит наличие необходимых библиотек (`opencv-python`, `PyQt5`).
3.  Если библиотеки отсутствуют, скрипт попытается установить их с помощью `pip`. Вам могут потребоваться права администратора или доступ в интернет.
4.  Если установка через `pip` не удалась (например, из-за ограничений сети или прав), вам может потребоваться установить библиотеки вручную в окружение Python, используемое Metashape.

## Использование

1.  Откройте ваш проект в Agisoft Metashape Pro.
2.  Убедитесь, что у вас есть активный чанк (`Chunk`) со сферическими камерами, которые вы хотите конвертировать.
3.  Запустите скрипт через меню Metashape: `Инструменты -> Скрипты -> Запуск скрипта...` (`Tools -> Run Script...`) и выберите файл `convert_to_cubemap_v012.py`.

### Графический интерфейс (GUI)

Если библиотека `PyQt5` доступна, запустится графический интерфейс:

*   **Настройки**:
    *   `Выходная папка`: Укажите папку для сохранения сгенерированных изображений граней.
    *   `Перекрытие (градусы)`: Установите угол перекрытия между гранями (для улучшения сшивки при необходимости).
    *   `Размер грани куба`: Выберите разрешение для каждой грани куба. "Автоматически" подберет размер на основе разрешения исходного изображения (рекомендуется).
    *   `Координатная система`: Выберите систему координат проекта или оставьте "Автоопределение".
    *   `Потоки обработки граней`: Количество потоков для параллельной конвертации граней **одной** сферической камеры.
    *   `Потоки обработки камер`: Количество потоков для параллельной конвертации **разных** сферических камер одновременно. **См. раздел "Настройка потоков" ниже!**
*   **Параметры изображения**:
    *   `Формат файла`: JPG, PNG или TIFF.
    *   `Качество`: Для JPG (75-100).
    *   `Интерполяция`: Метод интерполяции при ремаппинге (Кубическая - лучше качество, Ближайшая - быстрее).
*   **Выбор граней куба**: Отметьте галочками, какие грани вы хотите сгенерировать.
*   **Обработка после конвертации**:
    *   `Повторно выровнять камеры`: Запустить `Align Cameras` после добавления новых кубических камер.
    *   `Удалить исходные сферические камеры`: Удалить оригинальные сферические камеры после успешной конвертации.
*   **Информация о проекте**: Показывает количество найденных камер и определенную систему координат.
*   **Прогресс обработки**: Отображает общий прогресс, текущую операцию и оценку оставшегося времени.
*   **Кнопки управления**: "Запустить", "Остановить", "Закрыть".

### Консольный режим

Если `PyQt5` недоступен, скрипт запустится в консольном режиме, последовательно запрашивая все необходимые параметры через стандартные диалоговые окна Metashape. Прогресс будет отображаться в консоли.

### Руководство по настройке потоков

Скрипт использует два параметра для управления многопоточностью:

1.  **Потоки обработки граней (`Face processing threads`)**:
    *   **Что делает**: Определяет, сколько граней (например, front, back, top...) **одной** сферической камеры будут обрабатываться параллельно на этапе конвертации изображения (`cv2.remap`).
    *   **Влияние**: Увеличение этого значения ускоряет конвертацию *каждой отдельной* сферической камеры, но увеличивает потребление ОЗУ и нагрузку на CPU *во время* обработки этой камеры.
    *   **Рекомендации**: Значение по умолчанию (`min(6, CPU_cores // 2)`) является хорошей отправной точкой. Если вы наблюдаете нехватку памяти *во время* конвертации одной камеры (до добавления в Metashape), попробуйте уменьшить это значение (например, до 2-4).

2.  **Потоки обработки камер (`Camera processing threads`)**:
    *   **Что делает**: Определяет, сколько **разных** сферических камер будут конвертироваться *одновременно*. Например, если установлено значение 4, скрипт будет параллельно запускать процесс конвертации (включая обработку граней) для четырех разных сферических камер.
    *   **Влияние**: Увеличение этого значения может значительно ускорить общую обработку *большого количества* камер, но **сильно увеличивает пиковое потребление ОЗУ**, так как ресурсы требуются для нескольких одновременных конвертаций.
    *   **Рекомендации**:
        *   **Для систем с большим объемом ОЗУ (например, 64 ГБ+)**: Можно экспериментировать со значениями, равными количеству ядер CPU или даже больше, если дисковая подсистема быстрая.
        *   **❗️ Для систем с ограниченным объемом ОЗУ (например, 16-32 ГБ или меньше) ❗️**: **Настоятельно рекомендуется установить это значение равным 1**. Это заставит скрипт обрабатывать сферические камеры **последовательно**, одну за другой. Пиковое потребление ОЗУ будет определяться в основном обработкой граней *одной* камеры (контролируется первым параметром), что значительно стабильнее.
        *   **Успешный пример для низкого потребления ОЗУ**:
            *   Потоки обработки камер: **1**
            *   Потоки обработки граней: **5** (или другое умеренное значение, например, 4 или 6)
            *   В этом случае камеры конвертируются по очереди, но каждая камера использует 5 потоков для быстрой обработки своих граней.

## Локализация

Скрипт автоматически определяет язык интерфейса Metashape (`ru` или `en`) и использует соответствующие переводы. Если язык не определен или отличается от русского/английского, используется английский язык.

## Устранение неполадок

*   **Ошибка установки библиотек**: Убедитесь, что у вас есть доступ в интернет и права на установку пакетов Python. Попробуйте установить `opencv-python` и `PyQt5` вручную через `pip` в окружении Metashape.
*   **Высокое потребление ОЗУ / Сбои**: Уменьшите количество потоков, особенно **"Потоки обработки камер"** (установите в **1**). Также можно попробовать уменьшить "Потоки обработки граней".
*   **Проблемы с путями (кириллица)**: Скрипт включает функции для нормализации путей, но если проблемы остаются, убедитесь, что пути к проекту и изображениям не содержат очень специфических или невалидных символов.

## История версий

*   **v012 (Текущая)**:
    *   Восстановлена потоковая обработка камер (`ProcessCamerasThread`) для стабильности.
    *   Добавлено явное управление памятью (`del`, `gc.collect()`) для снижения потребления ОЗУ.
    *   Введены раздельные настройки для "Потоков обработки камер" и "Потоков обработки граней".
    *   Обновлены рекомендации по настройке потоков, особенно для систем с малым объемом ОЗУ.
*   **v0.11.x (Предыдущие попытки)**: Различные изменения, включая улучшения GUI, выбор граней, опции постобработки, поддержку кириллических путей, установку зависимостей, эксперименты без потоков.
*   **(Старые версии)**: Базовый консольный функционал.

## Благодарности

*   Agisoft за Python API Metashape.
*   Библиотеке OpenCV за возможности обработки изображений.
*   Фреймворку PyQt5 за графический пользовательский интерфейс.

---

