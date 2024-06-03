class File:
    key = ""        # Путь к файлу, полученный в результате загрузки файла (каждый файл в каждом сообщении должен иметь свой уникальный key, не допускается использование одного и того же key в разных сообщениях)
    name = ""       # Название файла, которое вы хотите отображать пользователю (рекомендуется писать вместе с расширением)
    file_type = ""  # Тип файла: файл (file), изображение (image)
    size:int = 0    # Размер файла в байтах, отображаемый пользователю

    def __init__(self, json = {}):
        if json:
            self.parse_json(json)

    def parse_json(self, json):
        self.key = json["key"]
        self.name = json["name"]
        self.file_type = json["file_type"]
        self.size = json["size"]

    def _is_valid_operand(self, other):
        return (hasattr(other, "key") and
                hasattr(other, "name") and
                hasattr(other, "file_type") and
                hasattr(other, "size"))
    
    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return (self.key == other.key and
                self.name == other.name and
                self.file_type == other.file_type and
                self.size == other.size)