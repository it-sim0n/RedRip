# RedRip - Open Redirect Tester

RedRip is a fast and reliable tool designed to detect Open Redirect vulnerabilities in web applications. By sending crafted payloads to a target URL parameter, it helps security researchers identify if a site improperly redirects users to attacker-controlled domains.

---

## Features

- Generates a wide variety of common and edge-case open redirect payloads  
- Supports custom payload wordlists for tailored testing  
- Detects redirects specifically to your specified target domain  
- Color-coded console output for quick identification of findings  
- Option to display full tested URLs for detailed review  
- Ability to save scan results to a file for documentation  

---

## Requirements

- Python 3.6 or higher  
- Install dependencies with pip:

```bash
pip install requests colorama
```

---

## Usage
Run the tool from the command line as follows:
```bash
python3 redrip.py TARGET_URL [OPTIONS]
```

---


## Arguments
The base URL of the vulnerable redirect parameter (e.g. https://site.com/?url=)

---

## Options

-w/--wordlist : Path to a custom payload wordlist file
-s/--save : Save results to a specified file
-f/--full : Show full URLs being tested	
-d/--domain : Target domain to detect redirects to	(e.g. evil.com)

---

## Examples

Test a URL with default payloads and show full URLs:
```bash
python3 redrip.py "https://example.com/?url=" -f
```

Use a custom payload list and save results:
```bash
python3 redrip.py "https://example.com/?redirect=" -w payloads.txt -s results.txt
```

Change the target domain for redirection detection:
```bash
python3 redrip.py "https://example.com/?next=" -d malicious.com
```

---

## How it works

The tool generates or loads payloads designed to trigger open redirect vulnerabilities.
It appends each payload to the target URL and sends an HTTP GET request without following redirects.
If the server responds with a redirect (Location header) pointing to the specified target domain, it marks the payload as successful.
Output is color-coded:
Green: Redirect to target domain detected
Yellow: Redirect to other domains (potentially suspicious)
Red: No redirect or error
Optionally, results can be saved to a file for later analysis.

---

## Disclaimer

This tool is intended solely for authorized penetration testing and educational purposes. Unauthorized use on websites without permission is illegal and unethical.

---

## Author
Simon – Stay sharp. Hack the redirectors.

