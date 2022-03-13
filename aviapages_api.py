import requests
import os
import time

HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': os.environ.get('API_TOKEN')
}
CALCULATOR_PARAMETERS = {
    "airway_time": True,
    "airway_distance": True
}


def get_airport_parameters(query: str, airport_type: str) -> dict:

    request_urls = (
        f'https://dir.aviapages.com:443/api/airports/?search_iata={query}',
        f'https://dir.aviapages.com:443/api/airports/?search_icao={query}',
        f'https://dir.aviapages.com:443/api/airports/?search_name={query}'
    )

    result = {}

    for request_url in request_urls:
        request = requests.get(url=request_url, headers=HEADERS)
        if request.status_code == 200:
            request_json = request.json()
            for request_result in request_json.get('results'):
                if query in (request_result.get('icao'), request_result.get('iata'), request_result.get('name')):
                    result.update(request_result)
                    break

    if len(result.keys()) == 0:
        raise RuntimeError(f'⚠️ {airport_type} airport not found ⚠️')
    else:
        return {
            'airport_icao': result.get('icao'),
            'airport_iata': result.get('iata'),
            'airport_name': result.get('name')
        }


def get_aircraft_parameters(query: str) -> dict:

    request_urls = (
        f'https://dir.aviapages.com:443/api/aircraft_profiles/?search_name={query}',
        f'https://dir.aviapages.com:443/api/aircraft_profiles/?search_aircraft_type_name={query}',
        f'https://dir.aviapages.com:443/api/aircraft_profiles/?search_aircraft_type_icao={query}'
    )

    result = {}

    for request_url in request_urls:
        request = requests.get(url=request_url, headers=HEADERS)
        if request.status_code == 200:
            request_json = request.json()
            if request_json.get('count') > 0:
                result.update(request_json.get('results')[0])
                break

    if len(result.keys()) == 0:
        raise RuntimeError('⚠️ Aircraft not found ⚠️')
    else:
        return {
            'aircraft_profile_name': result.get('name')
        }


def generate_calculator_message(query: dict) -> str:
    departure_airport = get_airport_parameters(query.get('departure_airport'), 'Departure')
    arrival_airport = get_airport_parameters(query.get('arrival_airport'), 'Arrival')
    passengers_count = query.get('pax')
    aircraft = query.get('aircraft')

    # Answer message
    departure = f'{departure_airport.get("airport_icao")} ({departure_airport.get("airport_iata")}), {departure_airport.get("airport_name")}'
    arrival = f'{arrival_airport.get("airport_icao")} ({arrival_airport.get("airport_iata")}), {arrival_airport.get("airport_name")}'

    calculated_parameters = calculate_flight_parameters(departure_airport, arrival_airport, aircraft, passengers_count)
    warnings = ''
    for warning in calculated_parameters.get('warnings'):
        warnings += f'{warning}\n'

    return f'✅ <b>FLIGHT INFO</b> ✅\n' \
           f'<b>{warnings}</b>' \
           f' ┌ {departure} ➡️ {arrival}\n' \
           f' ├ <b>Passengers</b>: {passengers_count}\n' \
           f' ├ <b>Aircraft</b>: {aircraft}\n' \
           f' ├ <b>Flight time</b>: {calculated_parameters.get("airway_time")}\n' \
           f' └ <b>Flight distance</b>: {int(calculated_parameters.get("airway_distance"))}km'


def calculate_flight_parameters(departure: dict, arrival: dict, aircraft: str, pax: int) -> dict:

    query = {
        'departure_airport': get_airport_find_parameter(departure),
        'arrival_airport': get_airport_find_parameter(arrival),
        'aircraft': aircraft,
        'pax': pax
    }

    # Additional parameters for query
    query.update(CALCULATOR_PARAMETERS)

    request_url = f'https://frc.aviapages.com:443/flight_calculator/'
    request = requests.post(url=request_url, headers=HEADERS, json=query)
    if request.status_code == 200:
        request_json = request.json()
        if 'errors' in request_json.keys():
            error_message = ''
            for error in request_json.get('errors'):
                error_message += f'{error.get("message")}\n'
            raise RuntimeError(f'⚠️\n{error_message}⚠️')
        else:
            request_airway = request_json.get('time').get('airway')
            airway_time = time.strftime("%H:%M", time.gmtime(request_airway * 60)) if request_airway else '00:00'
            return {
                'airway_time': airway_time,
                'airway_distance': request_json.get('distance').get('airway'),
                'warnings': request_json.get('warnings') if 'warnings' in request_json.keys() else []
            }
    else:
        raise RuntimeError('❗️ Connection failure ❗️')


def get_airport_find_parameter(airport: dict) -> str:
    if airport.get('airport_icao'):
        return airport.get('airport_icao')
    elif airport.get('airport_iata'):
        return airport.get('airport_iata')
    else:
        return airport.get('airport_name')
