import socket
import random
import time
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor

HOST = '127.0.0.1'  # Адрес балансировщика
PORT = 80           # Порт балансировщика

client_types = ['mobile', 'desktop']
network_qualities = ['low', 'high']
content_types = ['video', 'audio']

def send_request(client_type, network_quality, content_type):
    """Отправка одного запроса и измерение времени ответа."""
    request = f"{client_type},{network_quality},{content_type}"
    start_time = time.time()  # Засекаем время начала
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Разрешить повторное использование порта
        s.connect((HOST, PORT))
        s.sendall(request.encode())
        response = s.recv(1024).decode()
    end_time = time.time()  # Засекаем время конца
    return response, end_time - start_time

def parallel_test(num_clients):
    """Параллельное выполнение теста для заданного числа клиентов."""
    # Ограничение количества потоков, чтобы не перегрузить сервер
    max_workers = min(num_clients, 100)  # Ограничим до 100 параллельных потоков
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(send_request, random.choice(client_types), random.choice(network_qualities), random.choice(content_types)) for _ in range(num_clients)]
        return [future.result()[1] for future in futures]

def run_test(num_clients):
    """Выполнение теста для заданного числа клиентов."""
    response_times = parallel_test(num_clients)
    return response_times

def main():
    client_counts = range(1, 3001, 250)  # Число клиентов от 10 до 100 с шагом 10
    average_times = []  # Средние времена ответа

    for num_clients in client_counts:
        print(f"Тест для {num_clients} клиентов...")
        response_times = run_test(num_clients)
        average_time = sum(response_times) / len(response_times)
        average_times.append(average_time)
        print(f"Среднее время ответа: {average_time:.4f} секунд")

    # Построение графика
    plt.figure(figsize=(10, 6))
    plt.plot(client_counts, average_times, marker='o', color='b', label="Среднее время ответа")
    plt.title("Зависимость времени ответа от количества клиентов")
    plt.xlabel("Количество клиентов")
    plt.ylabel("Среднее время ответа (сек)")
    plt.grid(True)
    plt.legend()
    plt.show()

    # Запись результатов в файл
    with open("results.csv", "w") as f:
        f.write("clients,response_time\n")
        for count, avg_time in zip(client_counts, average_times):
            f.write(f"{count},{avg_time:.4f}\n")

if __name__ == "__main__":
    main()
