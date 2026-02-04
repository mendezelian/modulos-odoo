import requests
import logging

_logger = logging.getLogger("Simulation")

def simulate():
    url = "http://3.233.57.10:8080/api/v1/partidas"
    try:
        response = requests.get(url, timeout=10)
        # response.raise_for_status()
        matches = response.json()
    except Exception as e:
        print(f"Error fetching: {e}")
        return

    print("Fetched matches:", len(matches))
    
    count_created = 0
    for match_data in matches:
        partida = match_data.get('partida', {})
        jugadores = match_data.get('jugadores', [])
        
        spring_match_id = partida.get('id')
        if not spring_match_id:
            continue
            
        print(f"Checking Match {spring_match_id}: with {len(jugadores)} players")
        
        for jug in jugadores:
             print(f"  - Player ID: {jug.get('id')} Name: {jug.get('nombre')}")
             # In Odoo we would:
             # player = env['res.partner'].search(...)
             # if not player: create...
             # existing = search(...)
             # if existing: continue
             # create session...

simulate()
