from datetime import datetime, timezone, timedelta
import gzip
import json
import urllib.request
import xml.etree.ElementTree as ET

xml_url = "https://www.free-epg.de/api/epg/m3u/f1745819.xml.gz"

print("Scaricamento EPG .gz in corso...")
req = urllib.request.urlopen(xml_url)
compressed_data = req.read()

print("Decompressione del file XML...")
xml_data = gzip.decompress(compressed_data)

print("Analisi del file XML...")
root = ET.fromstring(xml_data)
now = datetime.now(timezone.utc)

epg_dict = {}


def parse_xml_date(date_str):
  # Gestisce date in formato "YYYYMMDDHHMMSS +HHMM" o simili
  parts = date_str.strip().split()
  dt_naive = datetime.strptime(parts[0], "%Y%m%d%H%M%S")
  if len(parts) > 1 and (
      parts[1].startswith("+") or parts[1].startswith("-")
  ):
    sign = 1 if parts[1][0] == "+" else -1
    hours = int(parts[1][1:3])
    minutes = int(parts[1][3:5])
    offset = timedelta(hours=hours, minutes=minutes) * sign
    return dt_naive.replace(tzinfo=timezone(offset))
  return dt_naive.replace(tzinfo=timezone.utc)


for programme in root.findall("programme"):
  channel_id = programme.get("channel")
  start_str = programme.get("start")
  stop_str = programme.get("stop")
  title_elem = programme.find("title")

  if channel_id and start_str and stop_str and title_elem is not None:
    try:
      start_time = parse_xml_date(start_str)
      stop_time = parse_xml_date(stop_str)

      if start_time <= now <= stop_time:
        # Converte nell'orario locale (es. ora italiana) per la visualizzazione
        local_start = start_time.astimezone()
        local_stop = stop_time.astimezone()

        start_formatted = local_start.strftime("%H:%M")
        stop_formatted = local_stop.strftime("%H:%M")

        epg_dict[channel_id.strip()] = (
            f"{start_formatted} - {stop_formatted}: {title_elem.text}"
        )
    except Exception:
      continue

with open("epg.json", "w", encoding="utf-8") as f:
  json.dump(epg_dict, f, ensure_ascii=False, indent=2)

print(
    f"File epg.json generato con successo! {len(epg_dict)} canali aggiornati."
)
