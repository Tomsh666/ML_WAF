import re


def process_xml_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    documents = content.strip().split('\n\n')
    processed_documents = []
    for i in documents:
        processed_documents.append(i.replace('\n', ' '))

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(processed_documents))

input_file = 'payloads/xxe-injection-payload-list.txt'
output_file = 'payloads/processed_xxe_payloads.txt'
process_xml_file(input_file, output_file)
print(f"Обработанный файл сохранен как {output_file}")