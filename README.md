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

1.  Download the `convert_to_cubemap_v011.py` file.
2.  In Agisoft Metashape, go to `Tools` > `Scripts...` > `Run Script...`.
3.  Browse to and select the downloaded `convert_to_cubemap_v011.py` script.
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
-   **Errors during `add_cubemap_cameras`**: Check Metashape console for specific API errors. Ensure sufficient system resources.

## Version History

-   **v0.11.0 (Current)**:
    *   Optimized camera addition stage (significantly faster).
    *   Implemented automatic language detection based on Metashape UI (EN/RU).
    *   Removed manual language switcher from GUI.
    *   Removed power-of-two rounding for automatic face size calculation.
    *   Refined multithreading for image conversion.
    *   Added option to select specific faces for conversion.
    *   Added optional post-processing (realign, remove spherical).
    *   General code improvements and stability fixes.
-   **v0.9.0 (Previous example)**: Added GUI, initial multithreading, automatic face sizing (with rounding), artifact correction.
-   **v0.7.0**: Basic console version with core functionality.

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

1.  Скачайте файл `convert_to_cubemap_v011.py`.
2.  В Agisoft Metashape выберите `Инструменты` > `Скрипты...` > `Выполнить скрипт...`.
3.  Найдите и выберите скачанный скрипт `convert_to_cubemap_v011.py`.
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
    *   **Формат файла**: Выберите JPG, PNG или TIFF.
    *   **Качество**: Установите качество сжатия (75-100 для JPG).
    *   **Интерполяция**: Выберите метод передискретизации пикселей (Кубическая - лучшее качество, Ближайшая - быстрее).
    *   **Выберите грани**: Отметьте галочками грани куба, которые нужно сгенерировать (по умолчанию все).
    *   **Обработка после конвертации**: Опционально отметьте "Повторно выровнять камеры" и "Удалить исходные сферические камеры".
3.  **Нажмите "Запустить"**: Начать процесс конвертации.
4.  **Следите за прогрессом**: Индикатор выполнения, статус и оставшееся время будут обновляться.
5.  **Нажмите "Остановить"** для прерывания обработки или **"Закрыть"** по завершении или для выхода.

### Консольный режим

Если PyQt5 недоступен или не устанавливается, скрипт автоматически запустится в консоли:

1.  Следуйте инструкциям в консоли Metashape для выбора выходной папки.
2.  Настройте параметры конвертации (перекрытие, размер грани, формат, качество, интерполяция, выбор граней, постобработка), отвечая на запросы.
3.  Скрипт обработает все сферические изображения, найденные в активном чанке, и отобразит прогресс в консоли.

## Объяснение настроек

-   **Перекрытие**: Насколько каждая грань куба перекрывает соседние (в градусах). Полезно, если вы импортируете результат в ПО, которое сшивает грани куба.
-   **Размер грани**: Разрешение (ширина и высота в пикселях) каждого выходного изображения грани куба. "Автоматически" рассчитывает как `ширина_исходного_изображения / 4`.
-   **Координатная система**: Определяет ориентацию выходных граней куба относительно системы координат Metashape. "Автоопределение" пытается определить ее по существующим камерам.
-   **Потоки обработки граней**: Контролирует параллелизм *во время* конвертации одного сферического изображения в его грани. Не влияет на параллельную обработку разных камер (которая выполняется последовательно для стабильности с API Metashape).
-   **Формат файла**: Выберите формат выходных изображений.
-   **Качество**: Для формата JPG контролирует уровень сжатия (выше значение - лучше качество и больше размер файла).
-   **Интерполяция**: Алгоритм, используемый при пересчете пикселей во время преобразования проекции. Кубическая обычно дает лучшие визуальные результаты, но медленнее.
-   **Повторно выровнять камеры**: Если отмечено, запускает `matchPhotos` и `alignCameras` Metashape для вновь созданных камер граней куба после конвертации.
-   **Удалить исходные**: Если отмечено, удаляет исходные сферические камеры из чанка после конвертации и опционального выравнивания.

## Требования

-   Agisoft Metashape Professional или Standard (протестировано на последних версиях)
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
-   **Ошибки во время `add_cubemap_cameras`**: Проверьте консоль Metashape на наличие конкретных ошибок API. Убедитесь, что достаточно системных ресурсов.

## История версий

-   **v0.11.0 (Текущая)**:
    *   Оптимизирован этап добавления камер (значительно быстрее).
    *   Реализовано автоматическое определение языка на основе интерфейса Metashape (EN/RU).
    *   Убран ручной переключатель языка из GUI.
    *   Убрано округление до степени двойки при автоматическом расчете размера грани.
    *   Улучшена многопоточность для конвертации изображений.
    *   Добавлена опция выбора конкретных граней для конвертации.
    *   Добавлена опциональная постобработка (выравнивание, удаление сферических камер).
    *   Общие улучшения кода и исправления стабильности.
-   **v0.9.0 (Предыдущий пример)**: Добавлен GUI, начальная многопоточность, автоматический размер граней (с округлением), коррекция артефактов.
-   **v0.7.0**: Базовая консольная версия с основным функционалом.

## Лицензия

Проект лицензирован под лицензией MIT.

## Благодарности

-   Agisoft за Python API Metashape.
-   Библиотеке OpenCV за возможности обработки изображений.
-   Фреймворку PyQt5 за графический пользовательский интерфейс. 
