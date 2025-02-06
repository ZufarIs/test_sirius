from openai import OpenAI
import os
import requests
from datetime import datetime
import tiktoken  # Добавляем импорт библиотеки для подсчёта токенов

client = OpenAI()

class AI_Model:
    def __init__(self, user_prompt: str = None):
        self.temperature = 0.3
        self.user_prompt = user_prompt
        self.system_prompt = None
        
    def token_count(self) -> int:
        """
        Подсчитывает количество токенов в переданном тексте с использованием токенизатора, 
        соответствующего текущей модели.
        """
        try:
            if self.system_prompt:
                system_prompt = self.system_prompt
            else:
                system_prompt = ''
            
            encoder = tiktoken.encoding_for_model(self.model)
            return len(encoder.encode(self.user_prompt + system_prompt))
        except KeyError:
            # Если модель не найдена, используем cl100k_base как fallback
            encoder = tiktoken.get_encoding("cl100k_base")
            return len(encoder.encode(self.user_prompt + system_prompt))
        
    def adjust_token_length(self, length: int):
        """
        Урезает user message для модели до заданной длины, удаляя последние символы.
        """
        if self.token_count() > length:
            while self.token_count() > length:
                self.user_prompt = self.user_prompt[:-(int(0.1*len(self.user_prompt)))]
            print(f"Текст урезан до {self.token_count()} токенов")
            
    def get_answer(self, prompt: str = None) -> str | None:
        """
        Отправляет запрос к модели и возвращает ответ.
        """
        if prompt:
            self.user_prompt = prompt
        elif not self.user_prompt:
            raise ValueError("User prompt is not set")
        self.model = "gpt-4o-mini"
        self.adjust_token_length(128000)
        
        timestamp = 'Today is:' + datetime.now().strftime("%Y-%m-%d") + '\n'
        messages = [
            {
                "role": "user",
                "content": timestamp + self.user_prompt
            }
        ]
        if self.system_prompt:
            messages.append({
                "role": "system",
                "content": self.system_prompt
            })
        attempts = 0
        while attempts < 3:
            try:
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=self.temperature,
                )

                return completion.choices[0].message.content
            except Exception as e:
                attempts +=1
                print(f'Attempt {attempts} error:\n{e}')
        return None
    
    def image_generation(self, prompt: str = None) -> str | None:
        """
        Генерирует изображение на основе заданного текстового описания.
        """
        if prompt:
            self.user_prompt = prompt
        elif not self.user_prompt:
            raise ValueError("User prompt is not set")
        self.model = "dall-e-3"
        self.adjust_token_length(32000)
        completion = client.images.generate(
            model=self.model,
            prompt=prompt,
            n=1,
            size="1024x1024",
            style="vivid"
        )
        
        if completion.data[0].url:
            try:
                # Создаем директорию для сохранения
                save_dir = "media/"
                os.makedirs(save_dir, exist_ok=True)
                
                # Формируем имя файла
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"dalle3_{timestamp}.png"
                file_path = os.path.join(save_dir, filename)
                
                # Скачиваем и сохраняем изображение
                response = requests.get(completion.data[0].url)
                response.raise_for_status()
                
                with open(file_path, "wb") as f:
                    f.write(response.content)
                    
                return file_path
                
            except Exception as e:
                print(f"Ошибка при сохранении изображения: {e}")
                return None
        return None

if __name__ == "__main__":
    ai_model = AI_Model()
    ai_model.image_generation("A beautiful sunset over a calm ocean")
