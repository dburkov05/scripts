import requests
from bs4 import BeautifulSoup
import json
import argparse
import time

def get_data(html):
    page = BeautifulSoup(html, 'lxml')
    try:
        elems = page.form.find_all('input')
        data = {}
        for el in elems:
            data[el['name']] = el['value']
        return data
    except:
        return None

def login():
    ses = requests.Session()
    html1 = ses.get('http://172.20.16.1/login').content
    data = get_data(html1)
    if data == None:
        print('Error: вы уже авторизованы')
        return
    html2 = ses.post('https://radius.wifizone.me/preauth/', data=data).content
    data2 = get_data(html2)
    url2 = BeautifulSoup(html2, 'lxml').form['action']
    
    html3 = ses.post(url2, data=data2).content.decode()
    soup1 = BeautifulSoup(html3, 'lxml')
    data3 = soup1.head.find_all('script')[-1].text
    find_str = "session_id: '"
    data4 = data3[data3.index(find_str):].split('\n')[0]
    session_id = data4[len(find_str):-2]
    print(session_id)

    url3 = 'https://auth.wifizone.me/v1/auth/autosubmit/' + session_id

    req = ses.get(url3)
    data5 = get_data(req.content)
    url4 = 'https://radius.wifizone.me/postpostauth/'
    
    req2 = ses.post(url4, data=data5)
    data6 = req2.content.decode()
    find_str2 = 'window.location.href="'
    url5 = data6[data6.index(find_str2)+len(find_str2):].split('\n')[0][:-2]

    req3 = ses.get(url5)
    print('Success: вход выполнен успешно')


def logout():
    req = requests.get('http://172.20.16.1/logout')
    if req:
        return True
    else:
        return False

def print_status():
    req = requests.get('http://172.20.16.1/status')
    soup = BeautifulSoup(req.content, 'lxml')
    try:
        elems = soup.table.find_all('td')[1:]
        for i in range(0, len(elems), 2):
            print(elems[i].text, elems[i + 1].text)
    except:
        print('Error: вы еще не авторизованы')


def check_login():
    req = requests.get('http://172.20.16.1/status')
    soup = BeautifulSoup(req.content, 'lxml')
    try:
        elems = soup.table.find_all('td')[1:]
        return True
    except:
        return False

def autologin():
    while True:
        if not check_login():
            print('Вход')
            login()
        time.sleep(60)

#login()
#logout()
#print_status()

def bind_login(root):
    def tmp_login(args):
        login()
    parser = root.add_parser('login')
    parser.set_defaults(_func=tmp_login)
    subparsers = parser.add_subparsers()
    
    return parser

def bind_logout(root):
    def tmp_logout(args):
        resp = logout()
        if resp:
            print('Success: выход выполнен успешно')
    parser = root.add_parser('logout')
    parser.set_defaults(_func=tmp_logout)
    subparsers = parser.add_subparsers()
    
    return parser

def bind_status(root):
    def tmp_status(args):
        print_status()
    parser = root.add_parser('status')
    parser.set_defaults(_func=tmp_status)
    subparsers = parser.add_subparsers()
    
    return parser


def bind_autologin(root):
    def tmp(args):
        autologin()
    parser = root.add_parser('autologin')
    parser.set_defaults(_func=tmp)
    subparsers = parser.add_subparsers()
    
    return parser

def get_main_parser():
    parser = argparse.ArgumentParser(prog='hrust-cli', description='Утилита для управления подключением к открытой сети БО "Хрустальная". Автор: dburkov05')
    parser.set_defaults(_func=lambda args: parser.print_help())
    subparsers = parser.add_subparsers()
    
    bind_login(subparsers)
    bind_logout(subparsers)
    bind_status(subparsers)
    bind_autologin(subparsers)

    return parser

def main():
    """
    The main entry point of the application
    """

    parser = get_main_parser()
    args = parser.parse_args()
    args._func(args)

if __name__ == '__main__':
    main()
