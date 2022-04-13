import requests
import os
import time

from telegram import Chat

HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Token {os.environ.get("API_TOKEN")}'
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


def get_avoid_parameters(avoid: set) -> dict:
    avoid_countries = []
    avoid_firs = []
    for query in avoid:
        request_url = f'https://dir.aviapages.com:443/api/countries/?search={query}'
        request = requests.get(url=request_url, headers=HEADERS)
        if request.status_code == 200:
            request_json = request.json()
            if request_json.get('count') > 0:
                avoid_countries.append(query)
            else:
                avoid_firs.append(query)

    return {
        'countries': avoid_countries,
        'firs': avoid_firs
    }


def generate_calculator_message(userdata: Chat, query: list) -> str:
    airway_total_time = 0
    airway_total_distance = 0
    all_warnings = ''

    flight_info = ''

    single_line = len(query) == 1

    for query_params in query:
        departure_airport = get_airport_parameters(query_params.get('departure_airport'), 'Departure')
        arrival_airport = get_airport_parameters(query_params.get('arrival_airport'), 'Arrival')
        passengers_count = query_params.get('pax')
        aircraft = query_params.get('aircraft')
        avoid = get_avoid_parameters(query_params.get('avoid'))

        calculated_parameters = calculate_flight_parameters(get_user_info(userdata), departure_airport, arrival_airport, aircraft, passengers_count, avoid)
        airway_total_time += calculated_parameters.get("airway_time")
        airway_total_distance += calculated_parameters.get("airway_distance")
        for warning in calculated_parameters.get('warnings'):
            if warning not in all_warnings:
                all_warnings += f'{warning}\n'

        if not single_line:
            if len(flight_info) == 0:
                flight_info += ' ┌ '
            else:
                flight_info += ' ├ '
        flight_info += generate_flight_info_message(departure_airport, arrival_airport, passengers_count, aircraft, avoid, single_line)

    airway_time = time.strftime("%H:%M", time.gmtime(airway_total_time * 60)) if airway_total_time > 0 else '00:00'

    return f'✅ <b>FLIGHT INFO</b> ✅\n' \
           f'<b>{all_warnings}</b>\n' \
           f'{flight_info}' \
           f' ├ <b>Flight time</b>: {airway_time}\n' \
           f' └ <b>Flight distance</b>: {int(airway_total_distance)}km'


def get_user_info(userdata: Chat) -> str:
    username = userdata.full_name
    return f'{username} ({userdata.username if userdata.username else userdata.id})'
    

def generate_flight_info_message(departure_airport: dict, arrival_airport: dict, passengers_count: int, aircraft: str, avoid: dict, single_line: bool) -> str:
    departure = f'{departure_airport.get("airport_icao")} ({departure_airport.get("airport_iata")}), {departure_airport.get("airport_name")}'
    arrival = f'{arrival_airport.get("airport_icao")} ({arrival_airport.get("airport_iata")}), {arrival_airport.get("airport_name")}'
    avoid_message = generate_avoid_message(avoid)
    if len(avoid_message) > 0:
        avoid_message = f' ├ {generate_avoid_message(avoid)}\n'

    if single_line:
        flight_info = f' ┌ {departure} ➡️ {arrival}\n' \
                      f' ├ <b>Passengers</b>: {passengers_count}\n' \
                      f' ├ <b>Aircraft</b>: {aircraft}\n'
    else:
        flight_info = f'{departure} ➡️ {arrival} (Passengers: {passengers_count}, Aircraft: {aircraft})\n'

    return flight_info + avoid_message


def generate_avoid_message(avoid: dict) -> str:
    avoid_message = ''
    if len(avoid.get('countries')) > 0:
        avoid_message += '🛑 <b>Avoided countries</b>: '
        for country in avoid.get('countries'):
            avoid_message += country + '; '
    if len(avoid.get('firs')) > 0:
        avoid_message += '🛑 <b>Avoided FIRs</b>: '
        for fir in avoid.get('firs'):
            avoid_message += fir + '; '

    return avoid_message


def calculate_flight_parameters(username: str, departure: dict, arrival: dict, aircraft: str, pax: int, avoid: dict) -> dict:

    query = {
        'departure_airport': get_airport_find_parameter(departure),
        'arrival_airport': get_airport_find_parameter(arrival),
        'aircraft': aircraft,
        'pax': pax,
        'avoid_countries': avoid.get('countries'),
        'avoid_firs': avoid.get('firs'),
        'username': username
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
            return {
                'airway_time': request_json.get('time').get('airway'),
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
