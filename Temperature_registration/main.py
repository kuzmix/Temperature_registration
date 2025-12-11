import serial
import csv
import time
from datetime import datetime
import pandas as pd  # для удобного CSV (опционально)

# Настройки
SERIAL_PORT = 'COM3'  # Windows: COM3, Linux/Mac: /dev/ttyUSB0
BAUD_RATE = 115200
CSV_FILE = f'.data//rtd_temperatures_{datetime.now().strftime('%Y-%m-%d %H:%M:%S)}.csv'


def parse_line(line):
    """Парсит строку вида: "Канал 0: 23.45" или "0, 23.45" """
    line = line.strip()
    if not line or line.startswith('---') or line == '':
        return None

    # Различные форматы из вашего Arduino кода
    if line.startswith('Канал'):
        parts = line.split(': ')
        if len(parts) == 2:
            chan_str, temp_str = parts
            chan = int(chan_str.split()[-1])  # "Канал 0" -> 0
            try:
                temp = float(temp_str)
                return {'channel': chan, 'temperature': temp}
            except:
                return None
    elif ',' in line:
        parts = line.split(', ')
        if len(parts) == 2:
            try:
                chan = int(parts[0])
                temp = float(parts[1])
                return {'channel': chan, 'temperature': temp}
            except:
                print(f'Unable to parse string "{parts}"')
                return None
    return None


# Инициализация CSV с заголовками
with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['timestamp', 'channel', 'temperature_C'])

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
print(f"Подключен к {SERIAL_PORT}, BAUD={BAUD_RATE}")
print(f"Данные пишутся в {CSV_FILE}")
time.sleep(2)  # Ждем стабилизации Arduino

try:
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore')
                data = parse_line(line)

                if data:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    row = [timestamp, data['channel'], data['temperature']]
                    writer.writerow(row)
                    writer.writerows([])  # flush

                    # Вывод в консоль
                    print(f"{timestamp} | Канал {data['channel']}: {data['temperature']:.2f}°C")

                    # Проверка NaN
                    # if str(data['temperature']) == 'nan':
                    #     print("  ⚠️  Fault/ошибка датчика!")
            # print('Sleep')
            # time.sleep(1)  # Не нагружаем CPU

except KeyboardInterrupt:
    print("\nОстановлено пользователем")
except Exception as e:
    print(f"Ошибка: {e}")
finally:
    ser.close()
    print(f"Данные сохранены в {CSV_FILE}")
