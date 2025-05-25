import random
import pandas as pd
import urllib.parse
import string
import os


def generate_random_path():
    path_words = [
        "api", "v1", "v2", "product", "view", "add", "cart", "login", "register",
        "search", "category", "list", "user", "profile", "edit", "checkout", "submit",
        "auth", "comment", "post", "admin", "data"
    ]
    num_segments = random.randint(1, 3)
    segments = random.sample(path_words, min(num_segments, len(path_words)))
    path = "/tienda1/" + "/".join(segments)
    return path


def generate_jsessionid():
    characters = string.ascii_uppercase + string.digits
    session_id = ''.join(random.choice(characters) for _ in range(32))
    return f"JSESSIONID={session_id}"


def load_payloads(payload_dir):
    if not os.path.exists(payload_dir):
        print(f"[!] Ошибка: Директория {payload_dir} не найдена")
        return {}

    payloads_by_class = {1: [], 2: [], 3: [], 4: [], 5: []}

    payload_files = [
        ("xxe-injection-payload-list.txt", 1),
        ("xss-payload-list.txt", 2),
        ("command_inj_payload_list.txt", 3),
        ("path_traversal_payload_list.txt", 4),
        #("ssti_payload_list.txt", 5),
    ]

    print(f"[*] Загрузка пейлоадов из {payload_dir}...")
    for payload_file, attack_type in payload_files:
        file_path = os.path.join(payload_dir, payload_file)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                payloads = [line.strip() for line in f if line.strip()]
                payloads_by_class[attack_type].extend(payloads)
                print(f"[*] Загружено {len(payloads)} пейлоадов (attack_type={attack_type}) из {file_path}")
        except FileNotFoundError:
            print(f"[!] Ошибка: Файл {file_path} не найден")

    intruder_dir = os.path.join(payload_dir, "sql_inj_payload")
    if os.path.exists(intruder_dir):
        print(f"[*] Обход папки {intruder_dir}...")
        for root, dirs, files in os.walk(intruder_dir):
            print(f"[*] Папка: {root}")
            print(f"  Файлы: {files}")
            for filename in files:
                if filename.endswith(".txt"):
                    file_path = os.path.join(root, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            payloads = [line.strip() for line in f if line.strip()]
                            payloads_by_class[5].extend(payloads)
                            print(f"[*] Загружено {len(payloads)} пейлоадов (sql_inj) из {file_path}")
                    except Exception as e:
                        print(f"[!] Ошибка при загрузке {file_path}: {e}")
    else:
        print(f"[!] Ошибка: Папка {intruder_dir} не найдена")
        exit(1)

    for attack_type in payloads_by_class:
        if not payloads_by_class[attack_type]:
            print(f"[!] Нет пейлоадов для класса {attack_type}. Используются встроенные пейлоады.")
            exit(1)

    return payloads_by_class


def generate_malicious_requests(samples_per_class, payload_dir, output_file):
    payloads_by_class = load_payloads(payload_dir)
    domains = ["localhost:8080"]
    data = []

    for attack_type in range(1, 6):
        payloads = payloads_by_class[attack_type]
        if len(payloads) < samples_per_class:
            payloads = (payloads * (samples_per_class // len(payloads) + 1))[:samples_per_class]
        else:
            payloads = random.sample(payloads, samples_per_class)

        for payload in payloads:
            if attack_type == 1:
                method = "POST"
            else:
                method = random.choice(["GET", "POST"])

            domain = random.choice(domains)
            path = generate_random_path()

            if method == "GET":
                param_key = random.choice(["query", "id", "name", "search", "input"])
                params = {param_key: payload}
                query_string = urllib.parse.urlencode(params)
                url = f"http://{domain}{path}?{query_string}"
                body = ""
            else:  # POST
                url = f"http://{domain}{path}"
                if attack_type == 1:  # XXE
                    body = payload
                else:
                    param_key = random.choice(["query", "id", "name", "search", "input"])
                    params = {param_key: payload}
                    body = urllib.parse.urlencode(params)

            request = {
                "Method": method,
                "content": body,
                "URL": url,
                "classification": attack_type
            }
            data.append(request)

    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"[*] Сгенерировано {len(data)} вредоносных HTTP-запросов и сохранено в {output_file}")

    return df


def generate_normal_requests(samples_per_class, output_file):
    domains = ["localhost:8080"]
    first_names = ["John", "Jane", "Alex", "Emma", "Michael", "Sarah", "David", "Laura"]
    categories = ["electronics", "clothing", "books", "home", "sports"]
    search_terms = ["best laptop", "cheap phone", "fiction books", "running shoes", "wireless headphones"]

    data = []

    for _ in range(samples_per_class):
        method = random.choice(["GET", "POST"])
        domain = random.choice(domains)
        path = generate_random_path()
        action = random.choice(["login", "search", "view_product", "add_to_cart", "register", "checkout"])

        if action == "login":
            username = f"{random.choice(first_names).lower()}{random.randint(1, 99)}"
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            params = {"username": username, "password": password}
        elif action == "search":
            params = {"query": random.choice(search_terms)}
        elif action == "view_product":
            params = {"product_id": random.randint(1, 1000), "category": random.choice(categories)}
        elif action == "add_to_cart":
            params = {"product_id": random.randint(1, 1000), "quantity": random.randint(1, 5)}
        elif action == "register":
            username = f"{random.choice(first_names).lower()}{random.randint(1, 99)}"
            email = f"{username}@example.com"
            params = {"username": username, "email": email,
                      "password": ''.join(random.choices(string.ascii_letters + string.digits, k=8))}
        else:  # checkout
            params = {"cart_id": random.randint(1000, 9999), "payment_method": random.choice(["credit_card", "paypal"])}

        if method == "GET":
            query_string = urllib.parse.urlencode(params)
            url = f"http://{domain}{path}?{query_string}"
            body = ""
        else:  # POST
            url = f"http://{domain}{path}"
            body = urllib.parse.urlencode(params)

        request = {
            "Method": method,
            "content": body,
            "URL": url,
            "classification": 0
        }
        data.append(request)

    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"[*] Сгенерировано {len(data)} нормальных HTTP-запросов и сохранено в {output_file}")

    return df


def generate_combined_traffic(samples_per_class, payload_dir, malicious_file, normal_file, combined_file):
    malicious_df = generate_malicious_requests(samples_per_class, payload_dir, malicious_file)

    normal_df = generate_normal_requests(samples_per_class, normal_file)

    combined_df = pd.concat([normal_df, malicious_df], ignore_index=True)
    combined_df.to_csv(combined_file, index=False)
    print(f"[*] Объединенный датасет сохранен в {combined_file} с {len(combined_df)} записями")

    return combined_df


if __name__ == "__main__":
    samples_per_class = 50000
    combined_data = generate_combined_traffic(
        samples_per_class=samples_per_class,
        payload_dir="payloads",
        malicious_file="malicious_traffic.csv",
        normal_file="normal_traffic.csv",
        combined_file="combined_traffic.csv"
    )
    print("\n[*] Распределение классов:")
    print(combined_data['classification'].value_counts().sort_index())
    print(combined_data.head())