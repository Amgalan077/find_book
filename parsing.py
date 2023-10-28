from bs4 import BeautifulSoup
import requests
import json
import pandas as pd

booklist = requests.get('https://www.biblio-globus.ru/catalog/categories')
main_path = 'https://www.biblio-globus.ru'

soup = BeautifulSoup(booklist.text, 'lxml')
categories = soup.find_all('li', attrs = {'class' : 'list-group-item'})

df = []
columns = ['page_url', 'image_url', 'author', 'title', 'annotation']
n = 1
for categorie in categories:

    categorie_url = main_path + categorie.find('a').get('href')
    categorie_page = requests.get(categorie_url)
    categorie_soup = BeautifulSoup(categorie_page.text, 'lxml')
    product_preview = categorie_soup.find_all('a', attrs = {'class' : 'product-preview-title'})
    for product in product_preview:
        idd = product.get('href').split('/')[-1]
        page = 1

        while True:
            book_list_url =  f'https://www.biblio-globus.ru/catalog/category?id={idd}&page={page}&sort=0'
            book_list_page = requests.get(book_list_url)
            book_list_soup = BeautifulSoup(book_list_page.text, 'lxml')
            book_list_link = book_list_soup.find_all('div', attrs = {'class' : 'text'})
            if not book_list_link:
                break

            for book in book_list_link:
                book_url = main_path + book.find('a').get('href')
                book_page = requests.get(book_url)
                book_soup = BeautifulSoup(book_page.text, 'lxml')
                book_anotation = book_soup.find('div', id='collapseExample')

                if book_anotation:
                    annotation = ''.join([symbol for symbol in book_anotation.text if symbol not in ['\n', '\r', '\t', 'm', '\xa0']])
                    annotation = annotation.split('Характеристики', 1)[0]
                    annotation = annotation.strip()
                else:
                    annotation = None
                
                try:
                    book_json = book_soup.find('script', attrs={'type' : 'application/ld+json'})
                    dict_json = json.loads(book_json.text)
                except (AttributeError, json.JSONDecodeError):
                    continue

                author = dict_json['author']['name']
                title = dict_json['name']
                image = dict_json['image']
                
                df.append([book_url, image, author, title, annotation])
            
            page += 1

    data = pd.DataFrame(df, columns=columns)
    data.to_csv(f'data{n}.csv', index=False)
    n += 1

