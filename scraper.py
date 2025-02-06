from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from smolagents import DuckDuckGoSearchTool
from threading import Thread
from typing import Dict, List

from ai_model import AI_Model

# Параметры Chrome
options = Options()
options.add_argument("--headless")

class Scraper:
    def __init__(self, query: str):
        self.query: str = query
        self.pages_content: Dict[str, str] = {}
        self.pages_summary: Dict[str, str] = {}
        links_search_tool = DuckDuckGoSearchTool()
        links: str = links_search_tool.forward('Польза раннего развития для будущего ребенка')        
        urls: List[str] = []
        for link in links.split('\n\n'):
            url = link.split('\n')[0].split((']('))[-1][:-1]
            if url.startswith('http'):
                urls.append(url)     
        self.urls: List[str] = urls
        self.scrape_pages()

        
    
    def get_page_content(self, url: str):
        '''
        Get the content of the page
        '''
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        text = driver.page_source
        driver.quit()
        ai_model = AI_Model()
        ai_model.system_prompt = "Ты профессиональный журналист, который собирает информацию посвященную теме: \n{self.querry}."
        ai_model.user_prompt = f'Найди полезную статью  на данной http странице: \n{text}. Верни полный текст статьи, удалив все ссылки на источник. Если содержание извлечь невозможно, то верни значение None'
        ai_model.temperature = 0.1
        answer = ai_model.get_answer()
        if answer:
            ai_model.user_prompt = f'Составь краткое содержание  статьи: \n{answer}'
            answer_summary = ai_model.get_answer()
            if answer_summary:
                self.pages_summary[url] = answer_summary
                self.pages_content[url] = answer

    
    def scrape_pages(self):
        '''
        Scrape the pages
        '''
        threads: List[Thread] = []
        for url in self.urls:
            thread = Thread(target=self.get_page_content, args=(url,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join(timeout=20)

if __name__ == "__main__":
    scraper = Scraper("Как правильно заниматься ранней подготовкой ребенка к школе")
    for url, content in scraper.pages_summary.items():
        print(f"URL: {url}\n{content}\n\n")
