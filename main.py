from qbittorrent import Client
import requests
from bs4 import BeautifulSoup
import re
from colorama import init
from colorama import Fore
import inquirer
from dotenv import load_dotenv
import os
import subprocess

load_dotenv()


init()

def getMagnetLink(link):
    
    print(f'Link: {link}')        
    torrent_page = requests.get(link).content
    soup = BeautifulSoup(torrent_page, 'html.parser')
    magnet_link = soup.find_all(href=re.compile("magnet:"))        
    print('Magnet Link:',magnet_link[0].get('href'))
    return magnet_link[0].get('href')



def getLinks(search_term):
    print('Buscando links...')
   
    links_dict = {}
    html = requests.get(f"https://www.1377x.to/sort-search/{search_term}/seeders/desc/1/").content
    soup = BeautifulSoup(html, 'html.parser')
    name_column_torrent = soup.find_all('td', class_='coll-1 name')    
    if name_column_torrent:
        for name in name_column_torrent:
            page_link = name.find_all('a')[1].get('href')
            link_text = name.find_all('a')[1].text
            links_dict[link_text] = "https://1377x.to" +  page_link           
        return links_dict
          
    print('No links found')
    return False
   

def downloadTorrent(magnet_link):
    print('Iniciando torrent download...')
    qb = Client("http://127.0.0.1:8081/")
    qb.login(os.getenv('QB_LOGIN'),os.getenv('QB_PASSWORD'))
    download = qb.download_from_link(magnet_link,savepath=os.getenv('DOWNLOAD_PATH'))
    if download == 'Fails.':
        print('Download falhou')
    if download == 'Ok.':
        print('Download iniciado!')   
    if download != 'Fails.' and download != 'Ok.':
        print('Download não iniciado')


def main():
    continue_download = True
    try:
        while(continue_download):
            search_query = input(Fore.GREEN + 'Buscar torrent: ')
            formated_query = search_query.replace(' ', '%20')
            links_list = getLinks(formated_query)
            if links_list:
                links_list_keys =  list(links_list.keys())
                questions = [
                inquirer.List('links',
                    message="Torrents encontrados:",
                    choices=links_list_keys,
                ),
                ]
                answers = inquirer.prompt(questions)
                magnet_link = getMagnetLink(links_list[answers['links']])
                
                subprocess.Popen(os.getenv('QB_PATH'))
                downloadTorrent(magnet_link)
                continue_question = [
                inquirer.List('links',
                    message="Deseja realizar outra busca ?",
                    choices=['Sim', 'Não'],
                ),
                ]
                answers = inquirer.prompt(continue_question)
                
                if(answers['links'] == 'Não'):
                    continue_download = False
                if(answers['links'] == 'Sim'):
                    continue_download = True
            else:
                print('Magnet link inválido')
        else:
            print('Finalizando...')  
    except Exception as e:
        print(f'Error: {e}')
        
        
main()