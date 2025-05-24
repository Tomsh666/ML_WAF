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
        return []

    all_payloads = []

    payload_files = [
        ("xxe-injection-payload-list.txt", "xxe"),
        ("xss-payload-list.txt", "xss"),
        ("command_inj_payload_list.txt", "command_inj"),
        ("path_traversal_payload_list.txt", "path_traversal")
    ]

    print(f"[*] Загрузка пейлоадов из {payload_dir}...")
    for payload_file, attack_type in payload_files:
        file_path = os.path.join(payload_dir, payload_file)
        try:
            if attack_type == "xxe":
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    payloads = []
                    current_payload = []
                    for line in content.splitlines():
                        line = line.strip()
                        if not line or line.startswith('*'):
                            if current_payload:
                                payloads.append(' '.join(current_payload))
                                current_payload = []
                        else:
                            current_payload.append(line)
                    if current_payload:
                        payloads.append(' '.join(current_payload))
                    payloads = [p for p in payloads if p.strip()]
                    all_payloads.extend([(payload, attack_type) for payload in payloads])
                    print(f"[*] Загружено {len(payloads)} пейлоадов ({attack_type}) из {file_path}")
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    payloads = [line.strip() for line in f if line.strip()]
                    all_payloads.extend([(payload, attack_type) for payload in payloads])
                    print(f"[*] Загружено {len(payloads)} пейлоадов ({attack_type}) из {file_path}")
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
                            all_payloads.extend([(payload, "sql_inj") for payload in payloads])
                            print(f"[*] Загружено {len(payloads)} пейлоадов (sql_inj) из {file_path}")
                    except Exception as e:
                        print(f"[!] Ошибка при загрузке {file_path}: {e}")
    else:
        print(f"[!] Ошибка: Папка {intruder_dir} не найдена")

    if not all_payloads:
        print("[!] Ошибка: Не удалось загрузить пейлоады.")
        exit(1)
    return all_payloads


def generate_malicious_requests(num_requests, payload_dir, output_file):
    malicious_payloads = load_payloads(payload_dir)

    domains = ["localhost:8080"]

    data = []

    for _ in range(num_requests):
        payload, attack_type = random.choice(malicious_payloads)
        # XXE-пейлоады отправляются только через POST с application/xml
        if attack_type == "xxe":
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
            content_type = ""
            length = "Content-Length: 0"
        else:  # POST
            url = f"http://{domain}{path}"
            if attack_type == "xxe":
                body = payload
                content_type = "application/xml"
                length = f"Content-Length: {len(body.encode('utf-8'))}"
            else:
                param_key = random.choice(["query", "id", "name", "search", "input"])
                params = {param_key: payload}
                body = urllib.parse.urlencode(params)
                content_type = "application/x-www-form-urlencoded"
                length = f"Content-Length: {len(body)}"

        request = {
            "Method": method,
            "cookie": generate_jsessionid(),
            "content-type": content_type,
            "Content-Length": length,
            "content": body,
            "URL": url,
            "classification": attack_type
        }
        data.append(request)

    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"[*] Сгенерировано {num_requests} вредоносных HTTP-запросов и сохранено в {output_file}")

    return df


if __name__ == "__main__":
    malicious_data = generate_malicious_requests(num_requests=36000, payload_dir="payloads",
                                                 output_file="malicious_traffic.csv")
    print(malicious_data.head())