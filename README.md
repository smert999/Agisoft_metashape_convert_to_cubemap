# Metashape Spherical to Cubemap Converter

A Python script for converting spherical 360° panoramas to cubemap projections within Agisoft Metashape.

## Features

- Convert spherical panoramas to 6 separate cube faces (front, right, left, top, down, back).
- Graphical user interface (GUI) for easy operation and configuration.
- Multi-threaded processing for faster image conversion.
- Automatic calculation of optimal cube face size based on source image width (width / 4, no power-of-two rounding).
- Customizable output settings: overlap, face size, image format (JPG, PNG, TIFF), quality, interpolation method.
- Select specific cube faces to generate.
- Optional post-processing: automatically realign cameras and remove original spherical cameras.
- Artifact correction for the back face seam.
- Automatic coordinate system detection (Y-UP, Z-UP, X-UP) or manual selection.
- Automatic UI language detection based on Metashape settings (English/Russian fallback).
- Detailed progress tracking with time estimation (in GUI mode).
- Support for both GUI and console modes.
- Automatic dependency installation (PyQt5, OpenCV) if needed.
- Handles file paths with non-ASCII characters (Cyrillic support).

## Installation

1.  Download the `convert_to_cubemap_v012.py` file.
2.  In Agisoft Metashape, go to `Tools` > `Scripts...` > `Run Script...`.
3.  Browse to and select the downloaded `convert_to_cubemap_v012.py` script.
4.  Dependencies (PyQt5 for GUI, OpenCV) will be checked and installed automatically if missing. Follow any prompts in the Metashape console.

## Usage

### GUI Mode (Recommended)

Upon running the script (if PyQt5 is available), a graphical interface will appear:

1.  **Select Output Folder**: Choose where the generated cube face images will be saved.
2.  **Adjust Settings**:
    *   **Overlap**: Angle in degrees for face overlap (helps with stitching in other software).
    *   **Face Size**: Choose "Automatically" (recommended, uses source width / 4) or select a specific pixel size (e.g., 1024x1024).
    *   **Coordinate System**: Select "Auto-detect" or manually choose Y_UP, Z_UP, or X_UP based on your project.
    *   **Face Processing Threads**: Number of CPU threads used to process the faces of a *single* spherical image in parallel.
    *   **Image Format**: Choose JPG, PNG, or TIFF.
    *   **Quality**: Set compression quality (75-100 for JPG).
    *   **Interpolation**: Select pixel resampling method (Cubic is best quality, Nearest is fastest).
    *   **Select Faces**: Check the boxes for the cube faces you want to generate (defaults to all).
    *   **Post-conversion Processing**: Optionally check "Realign cameras" and "Remove original spherical cameras".
3.  **Click "Start"**: Begin the conversion process.
4.  **Monitor Progress**: The progress bar, status, and estimated time remaining will update.
5.  **Click "Stop"** to abort processing or **"Close"** when finished or to exit.

### Console Mode

If PyQt5 is not available or fails to install, the script will automatically run in the console:

1.  Follow the prompts in the Metashape console to select the output folder.
2.  Configure the conversion parameters (overlap, face size, format, quality, interpolation, face selection, post-processing) as requested.
3.  The script will process all spherical images found in the active chunk and display progress in the console.

## Settings Explained

-   **Overlap**: How much each cube face overlaps its neighbors (degrees). Useful if importing into software that stitches cube faces.
-   **Face Size**: The resolution (width and height in pixels) of each output cube face image. "Automatic" calculates `source_image_width / 4`.
-   **Coordinate System**: Defines the orientation of the output cube faces relative to the Metashape coordinate system. "Auto-detect" attempts to determine this from existing cameras.
-   **Face Processing Threads**: Controls parallelism *during* the conversion of a single spherical image to its faces. Does not affect processing different cameras in parallel (which is done sequentially for stability with Metashape API).
-   **File Format**: Choose the output image format.
-   **Quality**: For JPG format, controls the compression level (higher means better quality and larger file size).
-   **Interpolation**: Algorithm used when remapping pixels during projection conversion. Cubic generally yields the best visual results but is slower.
-   **Realign Cameras**: If checked, runs Metashape's `matchPhotos` and `alignCameras` on the newly created cube face cameras after conversion.
-   **Remove Original**: If checked, deletes the original spherical cameras from the chunk after conversion and optional realignment.

## Requirements

-   Agisoft Metashape Professional or Standard (tested with recent versions)
-   Python 3.6+ (typically bundled with Metashape)
-   PyQt5 (for GUI, installed automatically)
-   OpenCV (cv2) (for image processing, installed automatically)

## Troubleshooting

-   **GUI Fails to Start**: The script should fall back to console mode. Check the Metashape console for errors during PyQt5 installation or import.
-   **Dependency Installation Issues**: If automatic installation fails, try manual installation using Metashape's Python console or a terminal:
    ```bash
    # Example path, adjust if needed
    "C:\Program Files\Agisoft\Metashape Pro\python\python.exe" -m pip install --upgrade pip
    "C:\Program Files\Agisoft\Metashape Pro\python\python.exe" -m pip install --user pyqt5 opencv-python
    ```
-   **Slow Performance**: Conversion, especially `realign_cameras`, can be time-consuming depending on the number of cameras, image resolution, and system specs. Monitor the console/GUI status.
-   **Incorrect Coordinate System**: If faces appear wrongly oriented, manually select the correct Coordinate System in the GUI/console instead of relying on "Auto-detect".
-   **High RAM Usage / Crashes**: Reduce the number of threads, especially **"Camera processing threads"** (set it to **1**). You might also reduce "Face processing threads".

## Version History

-   **v012 (Current)**:
    *   Restored threaded camera processing (`ProcessCamerasThread`) for stability.
    *   Added explicit memory management (`del`, `gc.collect()`) to reduce RAM usage.
    *   Introduced separate controls for "Camera processing threads" and "Face processing threads".
    *   Updated recommendations for thread settings, especially for low-RAM systems.
-   **v0.11.x (Previous attempts)**: Various changes including GUI improvements, face selection, post-processing options, Cyrillic path support, dependency installation, non-threaded experiments.
    *   **v0.11.0 (Current)**:
        *   Optimized camera addition stage (significantly faster).
        *   Implemented automatic language detection based on Metashape UI (EN/RU).
        *   Removed manual language switcher from GUI.
        *   Removed power-of-two rounding for automatic face size calculation.
        *   Refined multithreading for image conversion.
        *   Added option to select specific faces for conversion.
        *   Added optional post-processing (realign, remove spherical).
        *   General code improvements and stability fixes.
    *   **v0.9.0 (Previous example)**: Added GUI, initial multithreading, automatic face sizing (with rounding), artifact correction.
    *   **v0.7.0**: Basic console version with core functionality.

## License

This project is licensed under the MIT License.

## Acknowledgments

-   Agisoft for the Metashape Python API.
-   OpenCV library for image processing.
-   PyQt5 framework for the graphical user interface.

---

# Metashape Конвертер Сферических Панорам в Кубические Карты

Python-скрипт для преобразования сферических 360° панорам в кубические проекции внутри Agisoft Metashape.

## Возможности

- Преобразование сферических панорам в 6 отдельных граней куба (передняя, правая, левая, верхняя, нижняя, задняя).
- Графический пользовательский интерфейс (GUI) для удобной работы и настройки.
- Многопоточная обработка для ускорения конвертации изображений.
- Автоматический расчет оптимального размера граней куба на основе ширины исходного изображения (ширина / 4, без округления до степени двойки).
- Настраиваемые параметры вывода: перекрытие, размер грани, формат изображения (JPG, PNG, TIFF), качество, метод интерполяции.
- Выбор конкретных граней куба для генерации.
- Опциональная постобработка: автоматическое повторное выравнивание камер и удаление исходных сферических камер.
- Коррекция артефактов на шве задней грани.
- Автоматическое определение системы координат (Y-UP, Z-UP, X-UP) или ручной выбор.
- Автоматическое определение языка интерфейса на основе настроек Metashape (английский/русский).
- Детальное отслеживание прогресса с оценкой времени (в режиме GUI).
- Поддержка как GUI, так и консольного режимов.
- Автоматическая установка зависимостей (PyQt5, OpenCV) при необходимости.
- Обработка путей к файлам с не-ASCII символами (поддержка кириллицы).

## Установка

1.  Скачайте файл `convert_to_cubemap_v012.py`.
2.  В Agisoft Metashape выберите `Инструменты` > `Скрипты...` > `Выполнить скрипт...`.
3.  Найдите и выберите скачанный скрипт `convert_to_cubemap_v012.py`.
4.  Зависимости (PyQt5 для GUI, OpenCV) будут проверены и установлены автоматически при отсутствии. Следуйте инструкциям в консоли Metashape.

## Использование

### Режим GUI (Рекомендуется)

При запуске скрипта (если доступен PyQt5) появится графический интерфейс:

1.  **Выберите выходную папку**: Укажите, куда сохранять сгенерированные изображения граней куба.
2.  **Настройте параметры**:
    *   **Перекрытие**: Угол в градусах для перекрытия граней (помогает при сшивке в другом ПО).
    *   **Размер грани**: Выберите "Автоматически" (рекомендуется, использует ширина_источника / 4) или укажите конкретный размер в пикселях (например, 1024x1024).
    *   **Координатная система**: Выберите "Автоопределение" или вручную укажите Y_UP, Z_UP или X_UP в соответствии с вашим проектом.
    *   **Потоки обработки граней**: Количество потоков ЦП, используемых для параллельной обработки граней *одного* сферического изображения.
    *   **Image Format**: Choose JPG, PNG, or TIFF.
    *   **Quality**: Set compression quality (75-100 for JPG).
    *   **Interpolation**: Select pixel resampling method (Cubic is best quality, Nearest is fastest).
    *   **Select Faces**: Check the boxes for the cube faces you want to generate (defaults to all).
    *   **Post-conversion Processing**: Optionally check "Realign cameras" and "Remove original spherical cameras".
3.  **Click "Start"**: Begin the conversion process.
4.  **Monitor Progress**: The progress bar, status, and estimated time remaining will update.
5.  **Click "Stop"** to abort processing or **"Close"** when finished or to exit.

### Консольный режим

Если PyQt5 недоступен или не устанавливается, скрипт автоматически запустится в консоли:

1.  Следуйте инструкциям в консоли Metashape для выбора выходной папки.
2.  Configure the conversion parameters (overlap, face size, format, quality, interpolation, face selection, post-processing) as requested.
3.  The script will process all spherical images found in the active chunk and display progress in the console.

## Объяснение настроек

-   **Overlap**: How much each cube face overlaps its neighbors (degrees). Useful if importing into software that stitches cube faces.
-   **Face Size**: The resolution (width and height in pixels) of each output cube face image. "Automatic" calculates `source_image_width / 4`.
-   **Coordinate System**: Defines the orientation of the output cube faces relative to the Metashape coordinate system. "Auto-detect" attempts to determine this from existing cameras.
-   **Face Processing Threads**: Controls parallelism *during* the conversion of a single spherical image to its faces. Does not affect processing different cameras in parallel (which is done sequentially for stability with Metashape API).
-   **File Format**: Choose the output image format.
-   **Quality**: For JPG format, controls the compression level (higher means better quality and larger file size).
-   **Interpolation**: Algorithm used when remapping pixels during projection conversion. Cubic generally yields the best visual results but is slower.
-   **Realign Cameras**: If checked, runs Metashape's `matchPhotos` and `alignCameras` on the newly created cube face cameras after conversion.
-   **Remove Original**: If checked, deletes the original spherical cameras from the chunk after conversion and optional realignment.

## Requirements

-   Agisoft Metashape Professional or Standard (протестировано на последних версиях)
-   Python 3.6+ (обычно поставляется с Metashape)
-   PyQt5 (для GUI, устанавливается автоматически)
-   OpenCV (cv2) (для обработки изображений, устанавливается автоматически)

## Устранение неполадок

-   **GUI не запускается**: Скрипт должен переключиться в консольный режим. Проверьте консоль Metashape на наличие ошибок во время установки или импорта PyQt5.
-   **Проблемы с установкой зависимостей**: Если автоматическая установка не удалась, попробуйте ручную установку через Python-консоль Metashape или терминал:
    ```bash
    # Пример пути, измените при необходимости
    "C:\Program Files\Agisoft\Metashape Pro\python\python.exe" -m pip install --upgrade pip
    "C:\Program Files\Agisoft\Metashape Pro\python\python.exe" -m pip install --user pyqt5 opencv-python
    ```
-   **Низкая производительность**: Конвертация, особенно `realign_cameras`, может занять много времени в зависимости от количества камер, разрешения изображений и характеристик системы. Следите за статусом в консоли/GUI.
-   **Неправильная система координат**: Если грани выглядят неправильно ориентированными, выберите вручную правильную систему координат в GUI/консоли вместо "Автоопределение".
-   **High RAM Usage / Crashes**: Reduce the number of threads, especially **"Camera processing threads"** (set it to **1**). You might also reduce "Face processing threads".

## История версий

-   **v012 (Текущая)**:
    *   Восстановлена потоковая обработка камер (`ProcessCamerasThread`) для стабильности.
    *   Добавлено явное управление памятью (`del`, `gc.collect()`) для снижения потребления ОЗУ.
    *   Введены раздельные настройки для "Потоков обработки камер" и "Потоков обработки граней".
    *   Обновлены рекомендации по настройке потоков, особенно для систем с малым объемом ОЗУ.
-   **v0.11.x (Предыдущие попытки)**: Различные изменения, включая улучшения GUI, выбор граней, опции постобработки, поддержку кириллических путей, установку зависимостей, эксперименты без потоков.
    *   **v0.11.0 (Текущая)**:
        *   Оптимизирован этап добавления камер (значительно быстрее).
        *   Реализовано автоматическое определение языка на основе интерфейса Metashape (EN/RU).
        *   Убран ручной переключатель языка из GUI.
        *   Убрано округление до степени двойки при автоматическом расчете размера грани.
        *   Улучшена многопоточность для конвертации изображений.
        *   Добавлена опция выбора конкретных граней для конвертации.
        *   Добавлена опциональная постобработка (выравнивание, удаление сферических камер).
        *   Общие улучшения кода и исправления стабильности.
    *   **v0.9.0 (Предыдущий пример)**: Добавлен GUI, начальная многопоточность, автоматический размер граней (с округлением), коррекция артефактов.
    *   **v0.7.0**: Базовая консольная версия с основным функционалом.

## Лицензия

Проект лицензирован под лицензией MIT.

## Благодарности

-   Agisoft за Python API Metashape.
-   Библиотеке OpenCV за возможности обработки изображений.
-   Фреймворку PyQt5 за графический пользовательский интерфейс.

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

---

*Автор оригинальной идеи и базовых функций преобразования не указан в коде. Данная версия доработана для стабильности, управления памятью и улучшения интерфейса.* 
