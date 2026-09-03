import socket, ssl, json, requests, whois, dns.resolver, re, ipaddress
from pystyle import Colorate, Colors, Center

#функция с баннером для меню
def banner():
    art = r'''
 ▄█     █▄     ▄████████ ▀█████████▄        ▄█  ███▄▄▄▄      ▄████████  ▄██████▄
███     ███   ███    ███   ███    ███      ███  ███▀▀▀██▄   ███    ███ ███    ███
███     ███   ███    █▀    ███    ███      ███▌ ███   ███   ███    █▀  ███    ███
███     ███  ▄███▄▄▄      ▄███▄▄▄██▀       ███▌ ███   ███  ▄███▄▄▄     ███    ███
███     ███ ▀▀███▀▀▀     ▀▀███▀▀▀██▄       ███▌ ███   ███ ▀▀███▀▀▀     ███    ███
███     ███   ███    █▄    ███    ██▄      ███  ███   ███   ███        ███    ███
███ ▄█▄ ███   ███    ███   ███    ███      ███  ███   ███   ███        ███    ███
 ▀███▀███▀    ██████████ ▄█████████▀       █▀    ▀█   █▀    ███         ▀██████▀
'''
    print(Center.XCenter(Colorate.Horizontal(Colors.red_to_white, art)))
    print(Center.XCenter(Colorate.Horizontal(Colors.red_to_white, "\n[ by @DreamDolphin ]")))
    print(Center.XCenter(Colorate.Horizontal(Colors.red_to_white, "\n[ ! ] внимание перед использованием выключайте vpn или результат будет неправильным")))

#проверка на ipv4 адрес
def isip(value):
    try:
        ipaddress.IPv4Address(value)
        return True
    except ValueError:
        return False

#получение ip-адресса сайта
def getip(domain):
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return "Ошибка получения IP"

#информация через whois.
def get_whois(domain):
    try:
        w = whois.whois(domain)

        return {
            "Домен": w.domain_name or "Нет данных",
            "Регистратор": w.registrar or "Нет данных",
            "Дата создания": str(w.creation_date or "Нет данных"),
            "Истекает": str(w.expiration_date or "Нет данных"),
            "Страна": w.country or "Нет данных",
            "Email": w.emails or "Нет данных",
            "Организация": w.org or "Нет данных"
        }

    except Exception as e:
        return {
            "WHOIS": "Ошибка",
            "Описание": str(e)
        }

#получение dns имен
def get_dns(domain):
    dns_data = {}

    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [
        "1.1.1.1",
        "8.8.8.8"
    ]
    resolver.timeout = 3
    resolver.lifetime = 5

    try:
        dns_data["A"] = [
            str(ip)
            for ip in resolver.resolve(domain, "A")
        ]
    except dns.resolver.NoAnswer:
        dns_data["A"] = "Записей нет"
    except dns.resolver.NXDOMAIN:
        dns_data["A"] = "Домен не существует"
    except Exception as e:
        dns_data["A"] = f"Ошибка: {e}"

    try:
        dns_data["AAAA"] = [
            str(ip)
            for ip in resolver.resolve(domain, "AAAA")
        ]
    except dns.resolver.NoAnswer:
        dns_data["AAAA"] = "Записей нет"
    except dns.resolver.NXDOMAIN:
        dns_data["AAAA"] = "Домен не существует"
    except Exception as e:
        dns_data["AAAA"] = f"Ошибка: {e}"

    try:
        dns_data["MX"] = [
            str(r.exchange).rstrip(".")
            for r in resolver.resolve(domain, "MX")
        ]
    except dns.resolver.NoAnswer:
        dns_data["MX"] = "Записей нет"
    except dns.resolver.NXDOMAIN:
        dns_data["MX"] = "Домен не существует"
    except Exception as e:
        dns_data["MX"] = f"Ошибка: {e}"

    try:
        dns_data["NS"] = [
            str(r).rstrip(".")
            for r in resolver.resolve(domain, "NS")
        ]
    except dns.resolver.NoAnswer:
        dns_data["NS"] = "Записей нет"
    except dns.resolver.NXDOMAIN:
        dns_data["NS"] = "Домен не существует"
    except Exception as e:
        dns_data["NS"] = f"Ошибка: {e}"

    try:
        txt_records = []

        for r in resolver.resolve(domain, "TXT"):
            txt_records.append(
                "".join(
                    part.decode("utf-8", errors="replace")
                    for part in r.strings
                )
            )

        dns_data["TXT"] = txt_records

    except dns.resolver.NoAnswer:
        dns_data["TXT"] = "Записей нет"
    except dns.resolver.NXDOMAIN:
        dns_data["TXT"] = "Домен не существует"
    except Exception as e:
        dns_data["TXT"] = f"Ошибка: {e}"

    try:
        dns_data["CNAME"] = [
            str(r).rstrip(".")
            for r in resolver.resolve(domain, "CNAME")
        ]
    except dns.resolver.NoAnswer:
        dns_data["CNAME"] = "Записей нет"
    except dns.resolver.NXDOMAIN:
        dns_data["CNAME"] = "Домен не существует"
    except Exception as e:
        dns_data["CNAME"] = f"Ошибка: {e}"

    return dns_data

#информация о ssl:
def get_ssl(domain):
    try:
        context = ssl.create_default_context()

        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()

                issuer = {}

                for part in cert.get("issuer", ()):
                    for key, value in part:
                        issuer[key] = value

                subject = {}

                for part in cert.get("subject", ()):
                    for key, value in part:
                        subject[key] = value

                return {
                    "Версия TLS": ssock.version(),
                    "Шифрование": str(ssock.cipher()[0]),
                    "Выдан": issuer.get(
                        "commonName",
                        issuer.get("organizationName", "Нет данных")
                    ),
                    "Истекает": cert.get(
                        "notAfter",
                        "Нет данных"
                    ),
                    "Субъект": subject.get(
                        "commonName",
                        "Нет данных"
                    ),
                    "Серийный номер": cert.get(
                        "serialNumber",
                        "Нет данных"
                    )
                }

    except socket.timeout:
        return {"SSL": "Время ожидания истекло"}

    except ssl.SSLCertVerificationError:
        return {"SSL": "Ошибка проверки сертификата"}

    except ssl.SSLError as e:
        return {
            "SSL": "Ошибка SSL/TLS",
            "Описание": str(e)
        }

    except socket.error:
        return {"SSL": "Ошибка подключения"}

    except Exception as e:
        return {
            "SSL": "Ошибка",
            "Описание": str(e)
        }

#подключение к сайту и ворачиванние HTTP-HTTPS заголовка
def site(domain):
    try:
        r = requests.get(
            f"https://{domain}",
            timeout=5,
            allow_redirects=True
        )

        return {
            "URL": r.url,
            "Статус": r.status_code,
            "Заголовки": dict(r.headers)
        }

    except requests.Timeout:
        return {"HTTP": "Время ожидания истекло"}

    except requests.ConnectionError:
        return {"HTTP": "Ошибка подключения"}

    except requests.RequestException:
        return {"HTTP": "Ошибка запроса"}

#поиск геолокации DataCentr
def geo(ip):
    try:
        r = requests.get(
            f"https://ipinfo.io/{ip}/json",
            timeout=5
        )

        if r.status_code != 200:
            return {
                "GeoIP": "Ошибка API",
                "Статус": r.status_code
            }

        return r.json()

    except requests.Timeout:
        return {"GeoIP": "Время ожидания истекло"}

    except requests.RequestException:
        return {"GeoIP": "Ошибка подключения"}

    except ValueError:
        return {"GeoIP": "Некорректный ответ API"}

#скан портов
def scan(ip):
    ports = [21, 22, 23, 25, 53, 80, 110, 139, 143, 443, 445, 3306, 3389, 8080]
    result = {}

    for port in ports:
        try:
            s = socket.socket()
            s.settimeout(0.5)
            s.connect((ip, port))
            result[port] = 'Открыт'
            s.close()
        except:
            result[port] = 'Закрыт'

    return result

#проверка веб-разделов
def hidden_paths(domain):
    paths = [
        "/robots.txt",
        "/sitemap.xml",
        "/admin",
        "/login",
        "/dashboard",
        "/panel",
        "/api",
        "/docs"
    ]

    result = {}

    for path in paths:
        try:
            r = requests.get(
                f"https://{domain}{path}",
                timeout=5,
                allow_redirects=False
            )

            if r.status_code == 200:
                status = "Доступен"
            elif r.status_code == 301 or r.status_code == 302:
                status = "Перенаправление"
            elif r.status_code == 401:
                status = "Требуется авторизация"
            elif r.status_code == 403:
                status = "Доступ запрещён"
            elif r.status_code == 404:
                status = "Не найден"
            else:
                status = f"HTTP {r.status_code}"

            result[path] = {
                "Статус": status,
                "HTTP": r.status_code,
                "Перенаправление": r.headers.get("Location", "Нет")
            }

        except requests.Timeout:
            result[path] = {
                "Статус": "Время ожидания истекло"
            }

        except requests.ConnectionError:
            result[path] = {
                "Статус": "Ошибка подключения"
            }

        except requests.RequestException:
            result[path] = {
                "Статус": "Ошибка запроса"
            }

    return result

#проверка серверов на cloudflare
def cloudflare(domain, ip):
    try:
        target_ip = ipaddress.ip_address(ip)

        r = requests.get(
            "https://api.cloudflare.com/client/v4/ips",
            timeout=5
        )

        if r.status_code != 200:
            return f"Ошибка Cloudflare API: HTTP {r.status_code}"

        data = r.json()

        if not data.get("success"):
            return "Cloudflare API вернул ошибку"

        networks = []

        networks.extend(
            data.get("result", {}).get("ipv4_cidrs", [])
        )

        networks.extend(
            data.get("result", {}).get("ipv6_cidrs", [])
        )

        for network in networks:
            try:
                if target_ip in ipaddress.ip_network(network):
                    return f"IP принадлежит Cloudflare ({network})"
            except ValueError:
                continue

    except requests.Timeout:
        return "Ошибка: Timeout Cloudflare API"

    except requests.RequestException:
        return "Ошибка подключения к Cloudflare API"

    except ValueError:
        return "Некорректный IP"

    if domain:
        try:
            resolver = dns.resolver.Resolver(configure=False)
            resolver.nameservers = [
                "1.1.1.1",
                "8.8.8.8"
            ]

            dns_cname = resolver.resolve(domain, "CNAME")

            for r in dns_cname:
                cname = str(r).lower()

                if "cloudflare" in cname:
                    return "CNAME через Cloudflare"

        except Exception:
            pass

        try:
            r = requests.get(
                f"https://{domain}",
                timeout=5
            )

            server = r.headers.get("Server", "").lower()

            if "cloudflare" in server:
                return "Server содержит Cloudflare"

            if "cf-ray" in r.headers:
                return "Обнаружен CF-Ray → Cloudflare"

        except requests.RequestException:
            pass

    return "Cloudflare не обнаружен"

#вывод словаря через градиент
def print_dict(title, d):
    print(Colorate.Horizontal(
        Colors.red_to_white,
        f"\n[=] {title}"
    ))

    for k, v in d.items():
        print(Colorate.Horizontal(
            Colors.red_to_white,
            f"{k}: {v}"
        ))

while True:
    banner()

    target = input(
        Colorate.Horizontal(
            Colors.red_to_white,
            "\nВведите IP или домен: "
        )
    ).strip()

    if isip(target):
        domain = None
        ip = target
    else:
        domain = target
        ip = getip(domain)

    print(
        Colorate.Horizontal(
            Colors.red_to_white,
            f"\n[+] IP-адрес цели: {ip}"
        )
    )

    if ip == "Ошибка получения IP":
        input(
            Colorate.Horizontal(
                Colors.red_to_white,
                "\nНажмите Enter для возврата в меню..."
            )
        )
        continue

    if domain:
        print_dict("WHOIS", get_whois(domain))
        print_dict("DNS", get_dns(domain))
        print_dict("SSL-сертификат", get_ssl(domain))
        print_dict("HTTP-заголовки", site(domain))
        print_dict("Веб-разделы", hidden_paths(domain))

    print_dict("Геолокация IP", geo(ip))
    print_dict("Скан портов", scan(ip))

    print(
        Colorate.Horizontal(
            Colors.red_to_white,
            f"\n[=] Cloudflare: {cloudflare(domain, ip)}"
        )
    )

    input(
        Colorate.Horizontal(
            Colors.red_to_white,
            "\nНажмите Enter для возврата в меню..."
        )
    )
