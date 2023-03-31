import tkinter as tk
from tkinter import filedialog, ttk
from bs4 import BeautifulSoup
import openai
import requests
import json

def main():
    with open('openai_key.txt', 'r') as file:
        openai.api_key = file.read().strip()

    API_URL = "https://api.openai.com/v1/engines/davinci/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}",
    }

    root = tk.Tk()

    def categorize_bookmarks(bookmarks_file):
        with open(bookmarks_file, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            links = soup.find_all('a')
            categorized_bookmarks = {}
            progress_bar['maximum'] = len(links)
            for i, link in enumerate(links):
                url, title = link.get('href'), link.string
                category = get_category(url)
                categorized_bookmarks.setdefault(category, []).append((title, url))
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
        response = requests.post(API_URL, headers=headers, json=data)
        try:
            category = response.json()['choices'][0]['text']
        except KeyError:
            print(f"Error: {response.text}")
            category = "Uncategorized"
        return category

    def save_categorized_bookmarks(categorized_bookmarks):
        with open('new_bookmarks.html', 'w') as file:
            for category, bookmarks in categorized_bookmarks.items():
                file.write(f'<h1>{category}</h1>\n')
                for title, url in bookmarks:
                    file.write(f'<a href="{url}">{title}</a><br>\n')

    root.withdraw()
    bookmarks_file = filedialog.askopenfilename(filetypes=[('HTML Files', '*.html')])

    root.deiconify()
    root.title('Categorizing Bookmarks')

    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate desired window size (quarter of the screen)
    window_width = screen_width // 4
    window_height = screen_height // 4

    # Set initial window size and position (centered)
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    progress_text = tk.StringVar()
    progress_label = tk.Label(root, textvariable=progress_text)
    progress_label.pack()

    progress_bar = ttk.Progressbar(root, orient='horizontal', mode='determinate')
    progress_bar.pack(fill='x')

    categorized_bookmarks = categorize_bookmarks(bookmarks_file)
    save_categorized_bookmarks(categorized_bookmarks)

    progress_text.set('Done!')
    root.mainloop()

if __name__ == "__main__":
    main()
