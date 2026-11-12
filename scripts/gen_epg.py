import gzip
import json
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
import urllib.request

# Nuovo link del file EPG compresso in .gz
xml_url = "https://www.free-epg.de/api/epg/m3u/f1745819.xml.gz"

print("Scaricamento EPG .gz in corso...")
req = urllib.request.urlopen(xml_url)
compressed_data = req.read()

print("Decompressione del file XML...")
xml_data = gzip.decompress(compressed_data)

print("Analisi del file XML...")
root = ET.fromstring(xml_data)
now = datetime.now(timezone.utc).replace(tzinfo=None)

epg_dict = {}

for programme in root.findall("programme"):
    channel_id = programme.get("channel")
    start_str = programme.get("start")
    stop_str = programme.get("stop")
    title_elem = programme.find("title")

    if channel_id and start_str and stop_str and title_elem is not None:
        try:
            start_clean = start_str.split(" ")[0]
            stop_clean = stop_str.split(" ")[0]

            start_time = datetime.strptime(start_clean, "%Y%m%d%H%M%S")
            stop_time = datetime.strptime(stop_clean, "%Y%m%d%H%M%S")

            if start_time <= now <= stop_time:
                epg_dict[channel_id.strip()] = title_elem.text
        except Exception:
            continue

with open("epg.json", "w", encoding="utf-8") as f:
    json.dump(epg_dict, f, ensure_ascii=False, indent=2)

print(f"File epg.json generato con successo! {len(epg_dict)} canali aggiornati.")
