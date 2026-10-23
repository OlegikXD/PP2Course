import os

class TemplateLoader:
    def __init__(self, template_dir="templates"):
        self.template_dir = template_dir
        self.cache = {}

    def load(self, template_name):
        if template_name in self.cache:
            return self.cache[template_name]

        file_path = os.path.join(self.template_dir, template_name)
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                self.cache[template_name] = content
                return content
        except FileNotFoundError:
            print(f"⚠️ Шаблон {template_name} не найден!")
            return ""

    def render(self, template_name, **kwargs):
        template = self.load(template_name)
        if not template:
            return ""

        for key, value in kwargs.items():
            template = template.replace("{" + key + "}", str(value))

        return template