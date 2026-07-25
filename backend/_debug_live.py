import asyncio
import os
from dotenv import load_dotenv
load_dotenv(".env")
import requests

from auth_utils import create_access_token


def main():
    token = create_access_token("6fc7eaf8-61cf-405b-9010-0a9131bbdeea", "sgtkmogadala@gmail.com")
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get("http://127.0.0.1:8000/api/roadmap", headers=headers, timeout=15)
    print("status:", r.status_code)
    data = r.json()

    def find(nodes, target_id):
        for n in nodes:
            if n["id"] == target_id:
                return n
            found = find(n.get("children", []), target_id)
            if found:
                return found
        return None

    for track in data.get("tracks", []):
        if track["id"] == "dsa":
            arrays = find(track.get("children", []), "dsa.foundations.arrays")
            hashing = find(track.get("children", []), "dsa.foundations.hashing")
            print("LIVE dsa track status:", track["progress"]["status"], track["progress"]["completion_pct"])
            print("LIVE arrays status:", arrays["progress"]["status"] if arrays else None, arrays["progress"]["completion_pct"] if arrays else None)
            print("LIVE hashing status:", hashing["progress"]["status"] if hashing else None, hashing["progress"]["completion_pct"] if hashing else None)


main()
