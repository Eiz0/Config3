import re
import sys
import xml.etree.ElementTree as ET

class ConfigParser:
    def __init__(self):
        self.constants = {}  # Словарь для хранения констант

    def remove_comments(self, text):
        """Удаляет однострочные и многострочные комментарии из текста."""
        text = re.sub(r'\\.*', '', text)  # Удаляет однострочные комментарии
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)  # Удаляет многострочные комментарии
        return text

    def parse_value(self, value):
        """Определяет тип значения и возвращает его."""
        value = value.strip()
        if value.startswith('@"') and value.endswith('"'):  # Строки
            return {"type": "string", "value": value[2:-1]}
        elif re.match(r'^\d+$', value):  # Числа
            return {"type": "number", "value": int(value)}
        elif value.startswith("<<") and value.endswith(">>"):  # Массивы
            items = re.findall(r'@"[^"]*"|\S+', value[2:-2])
            return {"type": "array", "value": [self.parse_value(item) for item in items]}
        elif value.startswith("struct"):  # Словари (struct)
            return {"type": "struct", "value": self.parse_struct(value)}
        elif value.startswith("[") and value.endswith("]"):  # Константы
            const_name = value[1:-1].strip()
            if const_name in self.constants:
                return self.constants[const_name]
            else:
                raise ValueError(f"Undefined constant: {const_name}")
        else:
            raise ValueError(f"Unknown value: {value}")

    def parse_struct(self, text):
        """Парсит содержимое структуры (struct)."""
        struct_content = text[text.index("{") + 1:text.rindex("}")].strip()
        items = [line.strip() for line in struct_content.split(",") if line.strip()]
        result = {}
        for item in items:
            if "=" in item:
                key, value = item.split("=", 1)
                result[key.strip()] = self.parse_value(value.strip())
            else:
                raise ValueError(f"Invalid struct item: {item}")
        return result

    def parse(self, text):
        """Парсит весь конфигурационный файл."""
        text = self.remove_comments(text)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        root = ET.Element("config")

        for line in lines:
            if line.startswith("set"):  # Объявление константы
                _, rest = line.split("set", 1)
                name, value = rest.split("=", 1)
                self.constants[name.strip()] = self.parse_value(value.strip())
            elif "=" in line:  # Ключ-значение
                key, value = line.split("=", 1)
                value_data = self.parse_value(value.strip())
                self.add_to_xml(root, key.strip(), value_data)
            else:
                raise ValueError(f"Syntax error: {line}")
        return root

    def add_to_xml(self, parent, key, value_data):
        """Добавляет элементы в XML."""
        if value_data["type"] == "array":
            array_element = ET.SubElement(parent, key, type="array")
            for item in value_data["value"]:
                self.add_to_xml(array_element, "item", item)
        elif value_data["type"] == "struct":
            struct_element = ET.SubElement(parent, key, type="struct")
            for sub_key, sub_value in value_data["value"].items():
                self.add_to_xml(struct_element, sub_key, sub_value)
        else:
            element = ET.SubElement(parent, key, type=value_data["type"])
            element.text = str(value_data["value"])

    def to_xml(self, root):
        """Преобразует XML-дерево в строку."""
        return ET.tostring(root, encoding="utf-8").decode("utf-8")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 config_parser.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        with open(input_file, "r", encoding="utf-8") as file:
            text = file.read()
        parser = ConfigParser()
        xml_root = parser.parse(text)
        xml_output = parser.to_xml(xml_root)
        print(xml_output)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
