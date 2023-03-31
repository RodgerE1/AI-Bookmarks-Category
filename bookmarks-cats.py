import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from bs4 import BeautifulSoup
import openai
import requests
import json

openai.api_key = "###"
API_URL = "https://api.openai.com/v1/engines/davinci/completions"
engine="davinci"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openai.api_key}",
}

def categorize_bookmarks(bookmarks_file):
    with open(bookmarks_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')
        links = soup.find_all('a')
        categorized_bookmarks = {}
        progress_bar['maximum'] = len(links)
        for i, link in enumerate(links):
            url = link.get('href')
            title = link.string
            category = get_category(url)
            if category not in categorized_bookmarks:
                categorized_bookmarks[category] = []
            categorized_bookmarks[category].append((title, url))
            progress_bar['value'] = i + 1
            progress_text.set(f'Processing: {url} - {category}')
            root.update()
    return categorized_bookmarks

def get_category(url):
    data = {
        "prompt": f"Please categorize this URL: {url}",
        "max_tokens": 1,
        "n": 1,
        "stop": ["\n"],
        "temperature": 0.5,
    }
    response = requests.post(API_URL, headers=headers, data=json.dumps(data))
    response_json = response.json()
    category = response_json['choices'][0]['text']
    return category

def save_categorized_bookmarks(categorized_bookmarks):
    with open('new_bookmarks.html', 'w') as file:
        for category, bookmarks in categorized_bookmarks.items():
            file.write(f'<h1>{category}</h1>\n')
            for title, url in bookmarks:
                file.write(f'<a href="{url}">{title}</a><br>\n')

root = tk.Tk()
root.withdraw()
bookmarks_file = filedialog.askopenfilename()

root.deiconify()
root.title('Categorizing Bookmarks')

progress_text = tk.StringVar()
progress_label = tk.Label(root, textvariable=progress_text)
progress_label.pack()

progress_bar = ttk.Progressbar(root, orient='horizontal', mode='determinate')
progress_bar.pack(fill='x')

categorized_bookmarks = categorize_bookmarks(bookmarks_file)
save_categorized_bookmarks(categorized_bookmarks)

progress_text.set('Done!')
root.mainloop()
