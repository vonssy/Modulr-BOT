from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout,
    BasicAuth
)
from aiohttp_socks import ProxyConnector
from nacl.bindings import crypto_sign
from nacl.signing import SigningKey
from base64 import b64encode, b64decode
from base58 import b58encode
from blake3 import blake3
from dotenv import load_dotenv
from datetime import datetime
from colorama import *
import asyncio, random, json, sys, re, os

load_dotenv()

class Modulr:
    def __init__(self) -> None:
        self.API_URL = {
            "node": "http://rpc1.testnet.modulr.cloud:5332",
            "explorer": "https://testnet.explorer.modulr.cloud/tx/"
        }

        self.SEND_COUNT = int(os.getenv("SEND_COUNT") or "10")
        self.SEND_AMOUNT = int(os.getenv("SEND_AMOUNT") or "10")
        self.TX_FEE = 1

        self.MIN_DELAY = int(os.getenv("MIN_DELAY") or "5")
        self.MAX_DELAY = int(os.getenv("MAX_DELAY") or "10")

        self.USE_PROXY = False
        self.ROTATE_PROXY = False

        self.HEADERS = {}
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        
        self.USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/117.0.0.0"
        ]

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def now_str(self):
        return datetime.now().strftime('%x %X')

    def log(self, address: str, tx_idx: int, total: int, message: str):
        print(
            f"{Fore.CYAN+Style.BRIGHT}[ {self.now_str()} ]{Style.RESET_ALL} "
            f"{Fore.GREEN+Style.BRIGHT}[ {self.mask_account(address)} ]{Style.RESET_ALL} "
            f"{Fore.BLUE+Style.BRIGHT}[ {tx_idx}/{total} ]{Style.RESET_ALL} "
            f"{message}",
            flush=True
        )

    def log_info(self, message: str):
        print(
            f"{Fore.CYAN+Style.BRIGHT}[ {self.now_str()} ]{Style.RESET_ALL} "
            f"{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Modulr {Fore.BLUE + Style.BRIGHT}Auto BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "accounts.txt"
        try:
            with open(filename, 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            return accounts
        except Exception as e:
            print(f"{Fore.RED+Style.BRIGHT}Failed To Load Accounts: {e}{Style.RESET_ALL}")
            return None
        
    def load_proxies(self):
        filename = "proxy.txt"
        try:
            if not os.path.exists(filename):
                self.log_info(f"{Fore.RED+Style.BRIGHT}File proxy.txt Not Found.{Style.RESET_ALL}")
                return
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            if not self.proxies:
                self.log_info(f"{Fore.RED+Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return
            self.log_info(
                f"{Fore.GREEN+Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        except Exception as e:
            self.log_info(f"{Fore.RED+Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"
    
    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def build_proxy_config(self, proxy=None):
        if not proxy:
            return None, None, None
        if proxy.startswith("socks"):
            connector = ProxyConnector.from_url(proxy)
            return connector, None, None
        elif proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", proxy)
            if match:
                username, password, host_port = match.groups()
                clean_url = f"http://{host_port}"
                auth = BasicAuth(username, password)
                return None, clean_url, auth
            else:
                return None, proxy, None
    
    def display_proxy(self, proxy_url=None):
        if not proxy_url: return "No Proxy"
        proxy_url = re.sub(r"^(http|https|socks4|socks5)://", "", proxy_url)
        if "@" in proxy_url:
            proxy_url = proxy_url.split("@", 1)[1]
        return proxy_url
    
    def initialize_headers(self, address: str):
        if address not in self.HEADERS:
            self.HEADERS[address] = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Host": "rpc1.testnet.modulr.cloud:5332",
                "Pragma": "no-cache",
                "User-Agent": random.choice(self.USER_AGENTS)
            }
        return self.HEADERS[address].copy()
    
    def derive_keys(self, seed_b64: str):
        try:
            seed = b64decode(seed_b64)
            signing_key = SigningKey(seed)
            public_key = signing_key.verify_key.encode()
            secret_key = seed + public_key
            address = b58encode(public_key).decode()
            return {"address": address, "secretKey": secret_key}
        except Exception as e:
            self.log_info(f"{Fore.RED+Style.BRIGHT}Failed to Derive Keys: {e}{Style.RESET_ALL}")
            return None
    
    def canonicalizer(self, value) -> str:
        if value is None:
            return "null"
        if isinstance(value, (str, int, float, bool)):
            return json.dumps(value)
        if isinstance(value, list):
            return "[" + ",".join(self.canonicalizer(v) for v in value) + "]"
        if isinstance(value, dict):
            return "{" + ",".join(
                f"{json.dumps(k)}:{self.canonicalizer(value[k])}"
                for k in sorted(value.keys())
            ) + "}"
        return json.dumps(value)

    def build_preimage(self, payload: dict) -> str:
        return ":".join([
            str(payload["v"]),
            payload["from"],
            payload["to"],
            str(payload["amount"]),
            str(payload["fee"]),
            str(payload["nonce"]),
            self.canonicalizer(payload.get("payload", {}))
        ])
        
    def build_tx_id(self, payload: dict):
        preimage = self.build_preimage(payload)
        hash_bytes = blake3(preimage.encode()).digest()
        return hash_bytes.hex()
    
    def build_signature(self, secret_key: bytes, tx_id: str) -> str:
        message = tx_id.encode()
        signed = crypto_sign(message, secret_key)
        return b64encode(signed[:64]).decode()
    
    def build_sign_tx(self, secret_key: str, address: str, recipient: str, nonce: int):
        try:
            payload = {
                "v": 1,
                "type": "transfer",
                "from": address,
                "to": recipient,
                "amount": self.SEND_AMOUNT,
                "fee": self.TX_FEE,
                "nonce": nonce,
                "payload": {}
            }
            tx_id = self.build_tx_id(payload)
            signature = self.build_signature(secret_key, tx_id)
            payload["sig"] = signature
            return {"txId": tx_id, "signature": signature, "payload": payload}
        except Exception as e:
            self.log_info(f"{Fore.RED+Style.BRIGHT}Build Sign Transaction Failed: {e}{Style.RESET_ALL}")
            return None
        
    def generate_random_recipient(self):
        signing_key = SigningKey.generate()
        verify_key = signing_key.verify_key
        public_key = verify_key.encode()
        return b58encode(public_key).decode()
        
    def mask_account(self, account):
        try:
            return account[:6] + '*' * 6 + account[-6:]
        except Exception:
            return None

    async def print_timer(self, min_delay: int, max_delay: int):
        delay = random.randint(min_delay, max_delay)
        for remaining in range(delay, 0, -1):
            print(
                f"{Fore.CYAN+Style.BRIGHT}[ {self.now_str()} ]{Style.RESET_ALL} "
                f"{Fore.BLUE+Style.BRIGHT}Next tx in {remaining}s...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)

    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE+Style.BRIGHT}1. Run With Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE+Style.BRIGHT}2. Run Without Proxy{Style.RESET_ALL}")
                proxy_choice = int(input(f"{Fore.BLUE+Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())
                if proxy_choice in [1, 2]:
                    proxy_type = "With" if proxy_choice == 1 else "Without"
                    print(f"{Fore.GREEN+Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    self.USE_PROXY = True if proxy_choice == 1 else False
                    break
                else:
                    print(f"{Fore.RED+Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED+Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")

        if self.USE_PROXY:
            while True:
                rotate_proxy = input(f"{Fore.BLUE+Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()
                if rotate_proxy in ["y", "n"]:
                    self.ROTATE_PROXY = True if rotate_proxy == "y" else False
                    break
                else:
                    print(f"{Fore.RED+Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

    async def ensure_ok(self, response):
        if response.status >= 400:
            error_text = await response.text()
            raise Exception(f"HTTP {response.status}: {error_text}")
    
    async def check_connection(self, address: str, proxy_url=None):
        url = "https://api.ipify.org?format=json"
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get(url=url, proxy=proxy, proxy_auth=proxy_auth) as response:
                    await self.ensure_ok(response)
                    return True
        except (Exception, ClientResponseError) as e:
            self.log_info(
                f"{Fore.GREEN+Style.BRIGHT}[{self.mask_account(address)}]{Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT} Status: {Style.RESET_ALL} "
                f"{Fore.RED+Style.BRIGHT}Connection failed: {e}{Style.RESET_ALL}"
            )
        return None
    
    async def account_data(self, address: str, proxy_url=None, retries=5):
        url = f"{self.API_URL['node']}/account/{address}"
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(address)
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.ensure_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError):
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
        return None
    
    async def send_transaction(self, address: str, payload: dict, proxy_url=None, retries=5):
        url = f"{self.API_URL['node']}/transaction"
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(address)
                headers["Content-Type"] = "application/json"
                headers["Origin"] = "chrome-extension://cdmhpjjhnamicehbdojmlnnodfcgnehn"
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, json=payload, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.ensure_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError):
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
        return None
    
    async def get_transaction(self, address: str, tx_id: str, proxy_url=None, retries=5):
        url = f"{self.API_URL['node']}/transaction/{tx_id}"
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(address)
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.ensure_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError):
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
        return None

    async def process_check_connection(self, address: str, proxy_url=None):
        while True:
            if self.USE_PROXY:
                proxy_url = self.get_next_proxy_for_account(address)

            self.log_info(
                f"{Fore.GREEN+Style.BRIGHT}[ {self.mask_account(address)} ]{Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT} Proxy : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{self.display_proxy(proxy_url)}{Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy_url)
            if is_valid: return True

            if self.ROTATE_PROXY:
                proxy_url = self.rotate_proxy_for_account(address)
                await asyncio.sleep(1)
                continue

            return False

    async def process_transaction(self, secret_key: bytes, address: str, tx_idx: int, total: int, proxy_url=None):
        account = await self.account_data(address, proxy_url)
        if not account:
            self.log(address, tx_idx, total,
                f"{Fore.RED+Style.BRIGHT}Failed to fetch account data{Style.RESET_ALL}"
            )
            return True

        recipient = self.generate_random_recipient()
        balance   = account["balance"]
        nonce     = account["nonce"] + 1

        self.log(address, tx_idx, total,
            f"{Fore.WHITE+Style.BRIGHT}Balance  : {balance}  |  "
            f"Amount : {self.SEND_AMOUNT}  |  Fee : {self.TX_FEE}{Style.RESET_ALL}"
        )
        self.log(address, tx_idx, total,
            f"{Fore.WHITE+Style.BRIGHT}Recipient: {recipient}{Style.RESET_ALL}"
        )

        if balance < self.SEND_AMOUNT + self.TX_FEE:
            self.log(address, tx_idx, total,
                f"{Fore.YELLOW+Style.BRIGHT}Insufficient balance — account will be skipped{Style.RESET_ALL}"
            )
            return False

        txn = self.build_sign_tx(secret_key, address, recipient, nonce)
        if not txn:
            self.log(address, tx_idx, total,
                f"{Fore.RED+Style.BRIGHT}Failed to build transaction{Style.RESET_ALL}"
            )
            return True

        tx_id     = txn["txId"]
        signature = txn["signature"]
        payload   = txn["payload"]
        explorer  = self.API_URL["explorer"]

        self.log(address, tx_idx, total,
            f"{Fore.WHITE+Style.BRIGHT}Tx ID    : {tx_id}{Style.RESET_ALL}"
        )
        self.log(address, tx_idx, total,
            f"{Fore.WHITE+Style.BRIGHT}Signature: {signature}{Style.RESET_ALL}"
        )

        send_tx = await self.send_transaction(address, payload, proxy_url)
        if not send_tx:
            self.log(address, tx_idx, total,
                f"{Fore.RED+Style.BRIGHT}Failed to send transaction{Style.RESET_ALL}"
            )
            return True

        tx_msg        = send_tx.get("status")
        receipt_found = False
        tx_success    = False
        block         = None

        for attempt in range(5):
            await asyncio.sleep(2)
            receipt = await self.get_transaction(address, tx_id, proxy_url)
            if not receipt: break

            receipt_found = True
            block         = receipt.get("receipt", {}).get("block")
            tx_success    = receipt.get("receipt", {}).get("success")

            if not tx_success:
                self.log(address, tx_idx, total,
                    f"{Fore.YELLOW+Style.BRIGHT}Not confirmed yet, retrying... ({attempt+1}/5){Style.RESET_ALL}"
                )
                send_tx = await self.send_transaction(address, payload, proxy_url)
                if send_tx:
                    tx_msg = send_tx.get("status")
                continue
            break

        if receipt_found:
            self.log(address, tx_idx, total,
                f"{Fore.WHITE+Style.BRIGHT}Block    : {block}{Style.RESET_ALL}"
            )
            if tx_success:
                self.log(address, tx_idx, total,
                    f"{Fore.GREEN+Style.BRIGHT}Status   : {tx_msg}{Style.RESET_ALL}"
                )
            else:
                self.log(address, tx_idx, total,
                    f"{Fore.RED+Style.BRIGHT}Status   : Failed{Style.RESET_ALL}"
                )
            self.log(address, tx_idx, total,
                f"{Fore.WHITE+Style.BRIGHT}Explorer : {explorer}{tx_id}{Style.RESET_ALL}"
            )
        else:
            self.log(address, tx_idx, total,
                f"{Fore.RED+Style.BRIGHT}Status   : Failed (receipt not found){Style.RESET_ALL}"
            )

        return True

    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                print(f"{Fore.RED+Style.BRIGHT}No Accounts Loaded.{Style.RESET_ALL}")
                return False
            
            self.print_question()
            self.clear_terminal()
            self.welcome()
            self.log_info(
                f"{Fore.GREEN+Style.BRIGHT}Accounts Total : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )

            if self.USE_PROXY:
                self.load_proxies()

            self.log_info(f"{Fore.CYAN+Style.BRIGHT}{'─'*55}{Style.RESET_ALL}")

            account_list = []
            for seed_b64 in accounts:
                keys = self.derive_keys(seed_b64)
                if keys:
                    account_list.append((keys["secretKey"], keys["address"]))

            if not account_list:
                self.log_info(f"{Fore.RED+Style.BRIGHT}No valid accounts.{Style.RESET_ALL}")
                return False

            valid_accounts = []
            for secret_key, address in account_list:
                ok = await self.process_check_connection(address)
                if ok:
                    valid_accounts.append((secret_key, address))

            if not valid_accounts:
                self.log_info(f"{Fore.RED+Style.BRIGHT}No accounts with valid connection.{Style.RESET_ALL}")
                return False

            total_accs = len(valid_accounts)
            skip_flags = {address: False for _, address in valid_accounts}

            for tx_idx in range(1, self.SEND_COUNT + 1):
                self.log_info(
                    f"{Fore.CYAN+Style.BRIGHT}{'─'*18} Round {tx_idx}/{self.SEND_COUNT} {'─'*18}{Style.RESET_ALL}"
                )

                for acc_idx, (secret_key, address) in enumerate(valid_accounts, start=1):
                    self.log(address, tx_idx, self.SEND_COUNT,
                        f"{Fore.MAGENTA+Style.BRIGHT}Account  :{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {acc_idx}/{total_accs} {Style.RESET_ALL}"
                    )

                    if skip_flags[address]:
                        self.log(address, tx_idx, self.SEND_COUNT,
                            f"{Fore.YELLOW+Style.BRIGHT}Skipped (insufficient balance){Style.RESET_ALL}"
                        )
                    else:
                        proxy_url = self.get_next_proxy_for_account(address) if self.USE_PROXY else None
                        can_continue = await self.process_transaction(
                            secret_key, address, tx_idx, self.SEND_COUNT, proxy_url
                        )
                        if not can_continue:
                            skip_flags[address] = True

                    is_last = (acc_idx == total_accs) and (tx_idx == self.SEND_COUNT)
                    if not is_last:
                        await self.print_timer(self.MIN_DELAY, self.MAX_DELAY)

            self.log_info(f"{Fore.CYAN+Style.BRIGHT}{'─'*55}{Style.RESET_ALL}")
            self.log_info(
                f"{Fore.GREEN+Style.BRIGHT}All accounts processed.{Style.RESET_ALL}"
            )

        except Exception as e:
            raise e
        except asyncio.CancelledError:
            raise

if __name__ == "__main__":
    bot = Modulr()
    try:
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN+Style.BRIGHT}[{datetime.now().strftime('%x %X')}]{Style.RESET_ALL}"
            f" {Fore.RED+Style.BRIGHT}[ EXIT ] Modulr - BOT{Style.RESET_ALL}                                       "
        )
    finally:
        sys.exit(0)