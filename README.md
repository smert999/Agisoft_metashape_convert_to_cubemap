# Cube Map Converter for Metashape

A Python script for converting spherical 360° panoramas to cubemap projections in Agisoft Metashape.

## Features

- Convert spherical panoramas to 6 separate cube faces
- Graphical user interface for easy operation
- Multi-threaded processing for faster conversion
- Automatic optimal cube face size calculation
- Custom quality and format settings (JPG, PNG, TIFF)
- Artifact correction for cleaner results
- Automatically handles coordinate systems (Y-UP, Z-UP, X-UP)
- Detailed progress tracking with time estimation
- Support for both GUI and console modes

## Installation

1. Download the `convert_to_cubemap_v009.py` file
2. In Agisoft Metashape, go to Tools > Run Script...
3. Browse to and select the downloaded script
4. Dependencies (PyQt5) will be installed automatically if needed

## Usage

### GUI Mode

Upon running the script, a graphical interface will appear:

1. Select an output folder for the cube face images
2. Adjust settings as needed:
   - Face overlap (0-20°)
   - Cube face size (automatic or manual)
   - Coordinate system
   - Image format and quality
   - Interpolation method
3. Click "Start" to begin processing
4. Monitor progress and wait for completion

### Console Mode

If PyQt5 is not available or cannot be installed, the script will fall back to console mode:

1. Follow the prompts to select the output folder
2. Configure the conversion parameters as requested
3. The script will process all spherical images in the active chunk

## Settings

- **Overlap**: Controls how much each face overlaps (higher value helps with stitching)
- **Face Size**: Size of each cube face in pixels
- **Coordinate System**: Determines the orientation of the cube faces
- **File Format**: JPG (smaller files), PNG (lossless), or TIFF (highest quality)
- **Quality**: Compression quality for JPG format
- **Interpolation**: Method used for pixel resampling

## Requirements

- Agisoft Metashape Professional or Standard
- Python 3.6 or higher
- PyQt5 (installed automatically)
- OpenCV (installed automatically)

## Troubleshooting

- If GUI mode fails, the script will automatically switch to console mode
- For manual installation of dependencies, run:
  ```
  "C:\Program Files\Agisoft\Metashape Pro\python\python.exe" -m pip install pyqt5
  ```
- If image output appears corrupted, try changing the interpolation method

## Version History

- **v9.0.0**: Added GUI, multithreading, automatic face sizing, artifact correction
- **v7.0.0**: Basic console version with core functionality

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Agisoft for Metashape Python API
- OpenCV for image processing capabilities
- PyQt5 for GUI framework

---

# Конвертер Кубических Карт для Metashape

Python-скрипт для преобразования сферических 360° панорам в кубические проекции в Agisoft Metashape.

## Возможности

- Преобразование сферических панорам в 6 отдельных граней куба
- Графический интерфейс для удобной работы
- Многопоточная обработка для быстрого преобразования
- Автоматический расчет оптимального размера граней куба
- Настраиваемые параметры качества и формата (JPG, PNG, TIFF)
- Коррекция артефактов для более чистых результатов
- Автоматическая обработка координатных систем (Y-UP, Z-UP, X-UP)
- Детальное отслеживание прогресса с оценкой времени
- Поддержка как GUI, так и консольного режимов

## Установка

1. Скачайте файл `convert_to_cubemap_v009.py`
2. В Agisoft Metashape выберите Инструменты > Выполнить скрипт...
3. Найдите и выберите скачанный скрипт
4. Зависимости (PyQt5) будут установлены автоматически при необходимости

## Использование

### Режим GUI

При запуске скрипта появится графический интерфейс:

1. Выберите выходную папку для изображений граней куба
2. Настройте параметры:
   - Перекрытие граней (0-20°)
   - Размер грани куба (автоматический или ручной)
   - Координатная система
   - Формат и качество изображения
   - Метод интерполяции
3. Нажмите "Запустить", чтобы начать обработку
4. Следите за прогрессом и дождитесь завершения

### Консольный режим

Если PyQt5 недоступен или не может быть установлен, скрипт переключится в консольный режим:

1. Следуйте подсказкам для выбора выходной папки
2. Настройте параметры конвертации
3. Скрипт обработает все сферические изображения в активном чанке

## Настройки

- **Перекрытие**: Определяет насколько каждая грань перекрывается (большее значение помогает при сшивке)
- **Размер грани**: Размер каждой грани куба в пикселях
- **Координатная система**: Определяет ориентацию граней куба
- **Формат файла**: JPG (меньшие файлы), PNG (без потерь) или TIFF (наивысшее качество)
- **Качество**: Качество сжатия для формата JPG
- **Интерполяция**: Метод, используемый для передискретизации пикселей

## Требования

- Agisoft Metashape Professional или Standard
- Python 3.6 или выше
- PyQt5 (устанавливается автоматически)
- OpenCV (устанавливается автоматически)

## Устранение неполадок

- Если режим GUI не запускается, скрипт автоматически переключится в консольный режим
- Для ручной установки зависимостей выполните:
  ```
  "C:\Program Files\Agisoft\Metashape Pro\python\python.exe" -m pip install pyqt5
  ```
- Если изображения выглядят искаженными, попробуйте изменить метод интерполяции

## История версий

- **v9.0.0**: Добавлен GUI, многопоточность, автоматический расчет размера граней, коррекция артефактов
- **v7.0.0**: Базовая консольная версия с основным функционалом

## Лицензия

Проект лицензирован под лицензией MIT - подробности см. в файле LICENSE.

## Благодарности

- Agisoft за Python API Metashape
- OpenCV за возможности обработки изображений
- PyQt5 за фреймворк GUI
