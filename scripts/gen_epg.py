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

# Ottiene l'orario attuale italiano con fuso orario consapevole (aware)
now_rome = datetime.now(ZoneInfo("Europe/Rome"))

epg_dict = {}

for programme in root.findall("programme"):
  channel_id = programme.get("channel")
  start_str = programme.get("start")
  stop_str = programme.get("stop")
  title_elem = programme.find("title")

  if channel_id and start_str and stop_str and title_elem is not None:
    try:
      # Legge l'orario completo includendo il fuso orario dell'XML (es. "+0100")
      start_time = datetime.strptime(start_str.strip(), "%Y%m%d%H%M%S %z")
      stop_time = datetime.strptime(stop_str.strip(), "%Y%m%d%H%M%S %z")

      # Confronto temporale preciso al millisecondo
      if start_time <= now_rome <= stop_time:
        # Converte nell'orario locale italiano per la visualizzazione
        start_local = start_time.astimezone(ZoneInfo("Europe/Rome"))
        stop_local = stop_time.astimezone(ZoneInfo("Europe/Rome"))

        start_formatted = start_local.strftime("%H:%M")
        stop_formatted = stop_local.strftime("%H:%M")

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
