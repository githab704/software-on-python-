import requests
import random
import string
import time
import threading
from pystyle import Colorate, Colors, Center

#баннер

baner = r"""
 ▄▀▀▄ ▄▀▄  ▄▀▀█▄   ▄▀▀█▀▄   ▄▀▀▀▀▄     ▄▀▀▀█▀▀▄  ▄▀▀▄ ▄▀▄
█  █ ▀  █ ▐ ▄▀ ▀▄ █   █  █ █    █     █    █  ▐ █  █ ▀  █
▐  █    █   █▄▄▄█ ▐   █  ▐ ▐    █     ▐   █     ▐  █    █
  █    █   ▄▀   █     █        █         █        █
▄▀    ▄   █   ▀   ▄▀▀▀▀▀▄   ▄▀▄▄▄▄▄▄▀ ▄▀       ▄▀   ▄▀
█    █    ▐   ▐   █       █  █        █         █    █
▐    ▐            ▐       ▐  ▐        ▐         ▐    ▐
  [ by: @DreamDolpin ]
"""

#функция для окрашивания текста в градиент
def color(text):
    return Colorate.Horizontal(
        Colors.yellow_to_green,
        text
    )

#функция для вывода баннера
def banner():
    print(
        Center.XCenter(
            Colorate.Horizontal(
                Colors.yellow_to_green,
                baner
            )
        )
    )

#функция для получения доступного домена Mail.tm
def get_domain():
    res = requests.get(
        "https://api.mail.tm/domains",
        timeout=10
    )

    res.raise_for_status()

    domains = res.json().get(
        "hydra:member",
        []
    )

    if not domains:
        raise Exception(
            "Доступные домены не найдены"
        )

    return domains[0]["domain"]

#функция для генерации случайного адреса и пароля
def generate_random(domain):
    username = ''.join(
        random.choices(
            string.ascii_lowercase + string.digits,
            k=10
        )
    )

    password = ''.join(
        random.choices(
            string.ascii_letters + string.digits,
            k=12
        )
    )

    email = f"{username}@{domain}"

    return email, password

#функция для создания аккаунта Mail.tm и получения токена
def mailtm_account():
    try:
        domain = get_domain()

        email, password = generate_random(
            domain
        )

        res = requests.post(
            "https://api.mail.tm/accounts",
            json={
                "address": email,
                "password": password
            },
            timeout=10
        )

        if res.status_code != 201:
            try:
                error = res.json()
            except:
                error = res.text

            print(
                color(
                    f"\nОшибка регистрации: {error}"
                )
            )

            return None, None

        token_res = requests.post(
            "https://api.mail.tm/token",
            json={
                "address": email,
                "password": password
            },
            timeout=10
        )

        if token_res.status_code != 200:
            try:
                error = token_res.json()
            except:
                error = token_res.text

            print(
                color(
                    f"\nОшибка получения токена: {error}"
                )
            )

            return None, None

        token = token_res.json()["token"]

        return email, token

    except requests.RequestException as e:
        print(
            color(
                f"\nОшибка соединения: {e}"
            )
        )

        return None, None

    except Exception as e:
        print(
            color(
                f"\nОшибка: {e}"
            )
        )

        return None, None

#лог получения списка входящих сообщений
def get_list(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    res = requests.get(
        "https://api.mail.tm/messages",
        headers=headers,
        timeout=10
    )

    res.raise_for_status()

    return res.json().get(
        "hydra:member",
        []
    )

#функция для получения текста письма
def get_message(msg_id, token):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    res = requests.get(
        f"https://api.mail.tm/messages/{msg_id}",
        headers=headers,
        timeout=10
    )

    res.raise_for_status()

    data = res.json()

    return data.get(
        "text",
        "[нет текста]"
    )

#лог полученного письма
def message(msg, token):
    try:
        body = get_message(
            msg["id"],
            token
        )

        sender = msg.get(
            "from",
            {}
        ).get(
            "address",
            "Неизвестно"
        )

        subject = msg.get(
            "subject",
            "[Без темы]"
        )

        text = (
            "\n"
            "[+] Новое письмо!\n"
            f"От: {sender}\n"
            f"Тема: {subject}\n"
            f"ID: {msg['id']}\n"
            f"Содержимое:\n{body}\n"
            f"{'=' * 40}"
        )

        print(color(text))

    except Exception as e:
        print(
            color(
                f"\nОшибка чтения письма: {e}"
            )
        )

#постоянная проверка новых писем
def mail_watcher():
    global email
    global token
    global seen_ids
    global watcher_running

    while watcher_running:
        if token:
            try:
                inbox = get_list(token)

                for msg in inbox:
                    if msg["id"] not in seen_ids:
                        seen_ids.add(
                            msg["id"]
                        )

                        message(
                            msg,
                            token
                        )

            except requests.RequestException:
                pass

            except Exception:
                pass

        time.sleep(3)

#функция для создания первого акка
def create_account():
    global email
    global token
    global seen_ids

    print(
        color(
            "\n[+] Создание временной почты..."
        )
    )

    new_email, new_token = mailtm_account()

    if new_email and new_token:
        email = new_email
        token = new_token
        seen_ids.clear()

        print(
            color(
                f"\n[+] Почта создана: {email}"
            )
        )

#функция для смены акка
def remove_account():
    global email
    global token
    global seen_ids

    print(
        color(
            "\n[+] Создание нового аккаунта..."
        )
    )

    new_email, new_token = mailtm_account()

    if new_email and new_token:
        old_email = email

        email = new_email
        token = new_token
        seen_ids.clear()

        print(
            color(
                f"\n[+] Старый аккаунт: {old_email}"
            )
        )

        print(
            color(
                f"[+] Новый аккаунт: {email}"
            )
        )

#функция лог информации о текущем аккаунте
def log_account():
    if email:
        print(
            color(
                f"\n[=] Текущая почта: {email}"
            )
        )

        print(
            color(
                "[=] Статус: активна"
            )
        )

    else:
        print(
            color(
                "\n[-] Аккаунт ещё не создан."
            )
        )

#функция для меню
def menu():
    global watcher_running

    while watcher_running:
        print(
            color(
                "\n[  1  ] Создать временную почту"
            )
        )

        print(
            color(
                "[  2  ] Показать текущую почту"
            )
        )

        print(
            color(
                "[  3  ] Обновить аккаунт"
            )
        )

        print(
            color(
                "[  4  ] Выход"
            )
        )

        choice = input(
            color(
                "\nВыберите действие: "
            )
        ).strip()

        if choice == "1":
            if email:
                print(
                    color(
                        "\n[-] Аккаунт уже существует."
                    )
                )

                print(
                    color(
                        f"[=] Текущая почта: {email}"
                    )
                )

                print(
                    color(
                        "[!] Для создания новой используйте пункт [  3 ]."
                    )
                )

            else:
                create_account()

        elif choice == "2":
            log_account()

        elif choice == "3":
            remove_account()

        elif choice == "4":
            watcher_running = False

            print(
                color(
                    "\n[+] Завершение работы..."
                )
            )

            break

        else:
            print(
                color(
                    "\n[-] Неизвестный пункт."
                )
            )

#запуск основной части
if __name__ == "__main__":
    email = None
    token = None
    seen_ids = set()
    watcher_running = True

    banner()

    watcher = threading.Thread(
        target=mail_watcher,
        daemon=True
    )

    watcher.start()

    menu()
