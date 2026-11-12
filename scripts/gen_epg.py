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

# Ottiene l'ora attuale in Italia (gestisce automaticamente solare/legale)
now_rome = datetime.now(ZoneInfo("Europe/Rome"))

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

      # Converte i tempi XML (presunti in UTC) nel fuso orario italiano corretto
      start_utc = datetime.strptime(start_clean, "%Y%m%d%H%M%S").replace(
          tzinfo=ZoneInfo("UTC")
      )
      stop_utc = datetime.strptime(stop_clean, "%Y%m%d%H%M%S").replace(
          tzinfo=ZoneInfo("UTC")
      )

      start_rome = start_utc.astimezone(ZoneInfo("Europe/Rome"))
      stop_rome = stop_utc.astimezone(ZoneInfo("Europe/Rome"))

      if start_rome <= now_rome <= stop_rome:
        start_formatted = start_rome.strftime("%H:%M")
        stop_formatted = stop_rome.strftime("%H:%M")

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
