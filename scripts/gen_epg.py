from datetime import datetime
import json
import urllib.request
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

DTT_XML_URL = "https://www.open-epg.com/files/italy8.xml"
DTT_OUTPUT_FILE = "epg_dtt.json"

ROME_TZ = ZoneInfo("Europe/Rome")


def fetch_xml_root(url: str) -> ET.Element:
    print(f"Scaricamento EPG da: {url}")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        xml_bytes = resp.read()

    print("Analisi del file XML...")
    return ET.fromstring(xml_bytes)


def build_epg_dict(root: ET.Element, now_rome: datetime) -> dict:
    epg_dict = {}

    for programme in root.findall("programme"):
        channel_id = programme.get("channel")
        start_str = programme.get("start")
        stop_str = programme.get("stop")
        title_elem = programme.find("title")

        if not (channel_id and start_str and stop_str and title_elem is not None):
            continue

        title_text = "".join(title_elem.itertext()).strip()
        if not title_text:
            continue

        try:
            start_time = datetime.strptime(start_str.strip(), "%Y%m%d%H%M%S %z")
            stop_time = datetime.strptime(stop_str.strip(), "%Y%m%d%H%M%S %z")

            if stop_time >= now_rome:
                ch_id = channel_id.strip()
                epg_dict.setdefault(ch_id, []).append({
                    "start": start_time.astimezone(ROME_TZ).isoformat(),
                    "stop": stop_time.astimezone(ROME_TZ).isoformat(),
                    "title": title_text
                })
        except Exception:
            continue

    for ch_id, progs in epg_dict.items():
        progs.sort(key=lambda p: p["start"])

    epg_dict["_ultimo_aggiornamento"] = now_rome.strftime("%Y-%m-%d %H:%M:%S")
    return epg_dict


def save_json(data: dict, filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    channel_count = max(0, len(data) - 1)
    print(f"File '{filename}' generato con successo ({channel_count} canali).")


def main() -> None:
    now_rome = datetime.now(ROME_TZ)
    dtt_root = fetch_xml_root(DTT_XML_URL)
    dtt_epg = build_epg_dict(dtt_root, now_rome)
    save_json(dtt_epg, DTT_OUTPUT_FILE)


if __name__ == "__main__":
    main()
