from datetime import datetime
import json
import urllib.request
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

xml_url = "https://www.open-epg.com/files/italy8.xml"

print("Scaricamento EPG in corso...")
req = urllib.request.urlopen(xml_url)
xml_data = req.read()

print("Analisi del file XML...")
root = ET.fromstring(xml_data)

now_rome = datetime.now(ZoneInfo("Europe/Rome"))
epg_dict = {}

for programme in root.findall("programme"):
    channel_id = programme.get("channel")
    start_str = programme.get("start")
    stop_str = programme.get("stop")
    title_elem = programme.find("title")

    if channel_id and start_str and stop_str and title_elem is not None:
        try:
            start_time = datetime.strptime(start_str.strip(), "%Y%m%d%H%M%S %z")
            stop_time = datetime.strptime(stop_str.strip(), "%Y%m%d%H%M%S %z")

            # Consideriamo i programmi da adesso in poi (o che sono appena iniziati)
            if stop_time >= now_rome:
                ch_id = channel_id.strip()
                if ch_id not in epg_dict:
                    epg_dict[ch_id] = []

                # Salviamo start, stop in formato ISO/stringa e il titolo
                epg_dict[ch_id].append({
                    "start": start_time.astimezone(ZoneInfo("Europe/Rome")).isoformat(),
                    "stop": stop_time.astimezone(ZoneInfo("Europe/Rome")).isoformat(),
                    "title": title_elem.text
                })
        except Exception:
            continue

# Timestamp dell'ultimo aggiornamento
epg_dict["_ultimo_aggiornamento"] = now_rome.strftime("%Y-%m-%d %H:%M:%S")

with open("epg.json", "w", encoding="utf-8") as f:
    json.dump(epg_dict, f, ensure_ascii=False, indent=2)

print(f"File epg.json generato con successo!")
