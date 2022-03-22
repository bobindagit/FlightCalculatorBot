import unittest
import bot
import aviapages_api

INVALID_QUERY = '⚠️ Invalid query ⚠️'
INVALID_QUERY_COUNT = '⚠️ Each line should be started with count number ⚠️'


class QueryTest(unittest.TestCase):

    def test_correct_query(self):
        query = 'UUWW - EVRA 2Pax Challenger 300'
        answer = [{
            'count': '',
            'departure_airport': 'UUWW',
            'arrival_airport': 'EVRA',
            'pax': 2,
            'aircraft': 'Challenger 300',
            'avoid': set()
        }]
        self.assertEqual(bot.get_query_structure(query), answer)
        query = 'KIV-RIX 3 E35L'
        answer = [{
            'count': '',
            'departure_airport': 'KIV',
            'arrival_airport': 'RIX',
            'pax': 3,
            'aircraft': 'E35L',
            'avoid': set()
        }]
        self.assertEqual(bot.get_query_structure(query), answer)
        query = 'Heathrow - Geneva 3 pax Global 5000 (IASA regulations)'
        answer = [{
            'count': '',
            'departure_airport': 'Heathrow',
            'arrival_airport': 'Geneva',
            'pax': 3,
            'aircraft': 'Global 5000 (IASA regulations)',
            'avoid': set()
        }]
        self.assertEqual(bot.get_query_structure(query), answer)
        query = 'KIV-- RIX 3 PAX E35L'
        answer = [{
            'count': '',
            'departure_airport': 'KIV',
            'arrival_airport': 'RIX',
            'pax': 3,
            'aircraft': 'E35L',
            'avoid': set()
        }]
        self.assertEqual(bot.get_query_structure(query), answer)
        query = 'KIV -  RIX  35  PAX   E35L'
        answer = [{
            'count': '',
            'departure_airport': 'KIV',
            'arrival_airport': 'RIX',
            'pax': 35,
            'aircraft': 'E35L',
            'avoid': set()
        }]
        self.assertEqual(bot.get_query_structure(query), answer)
        query = 'UUWW - EVRA 2 pax Global 5000 no Ukraine, Belarus'
        answer = [{
            'count': '',
            'departure_airport': 'UUWW',
            'arrival_airport': 'EVRA',
            'pax': 2,
            'aircraft': 'Global 5000',
            'avoid': {'Ukraine', 'Belarus'}
        }]
        self.assertEqual(bot.get_query_structure(query), answer)
        query = 'UUWW - EVRA 2 pax Global 5000 no ULAA; UHMM'
        answer = [{
            'count': '',
            'departure_airport': 'UUWW',
            'arrival_airport': 'EVRA',
            'pax': 2,
            'aircraft': 'Global 5000',
            'avoid': {'ULAA', 'UHMM'}
        }]
        self.assertEqual(bot.get_query_structure(query), answer)
        query = 'UUWW - EVRA 6 Global 5000 no   ULAA  ;   UHMM'
        answer = [{
            'count': '',
            'departure_airport': 'UUWW',
            'arrival_airport': 'EVRA',
            'pax': 6,
            'aircraft': 'Global 5000',
            'avoid': {'ULAA', 'UHMM'}
        }]
        self.assertEqual(bot.get_query_structure(query), answer)

    def test_correct_query_multiline(self):
        query = 'KIV - RIX 1 Global 5000\n' \
                ''
        answer = [{
            'count': '',
            'departure_airport': 'KIV',
            'arrival_airport': 'RIX',
            'pax': 1,
            'aircraft': 'Global 5000',
            'avoid': set()
        }]
        self.assertEqual(bot.get_query_structure(query), answer)
        query = 'KIV - RIX 1 Global 5000\n' \
                'RIX-VKO 1 Global 5000'
        answer = [
            {
                'count': '',
                'departure_airport': 'KIV',
                'arrival_airport': 'RIX',
                'pax': 1,
                'aircraft': 'Global 5000',
                'avoid': set()
            },
            {
                'count': '',
                'departure_airport': 'RIX',
                'arrival_airport': 'VKO',
                'pax': 1,
                'aircraft': 'Global 5000',
                'avoid': set()
            }
        ]
        self.assertEqual(bot.get_query_structure(query), answer)
        query = '1. KIV - RIX 1 Global 5000\n' \
                '2 RIX-VKO 1 Global 5000'
        answer = [
            {
                'count': '1',
                'departure_airport': 'KIV',
                'arrival_airport': 'RIX',
                'pax': 1,
                'aircraft': 'Global 5000',
                'avoid': set()
            },
            {
                'count': '2',
                'departure_airport': 'RIX',
                'arrival_airport': 'VKO',
                'pax': 1,
                'aircraft': 'Global 5000',
                'avoid': set()
            }
        ]
        self.assertEqual(bot.get_query_structure(query), answer)
        query = '1) KIV - RIX 1 Global 5000\n' \
                '2. RIX-VKO 1 Global 5000'
        answer = [
            {
                'count': '1',
                'departure_airport': 'KIV',
                'arrival_airport': 'RIX',
                'pax': 1,
                'aircraft': 'Global 5000',
                'avoid': set()
            },
            {
                'count': '2',
                'departure_airport': 'RIX',
                'arrival_airport': 'VKO',
                'pax': 1,
                'aircraft': 'Global 5000',
                'avoid': set()
            }
        ]
        self.assertEqual(bot.get_query_structure(query), answer)
        query = '2 KIV - RIX 1 Global 5000\n' \
                '1 RIX-VKO 1 Global 5000'
        answer = [
            {
                'count': '2',
                'departure_airport': 'RIX',
                'arrival_airport': 'VKO',
                'pax': 1,
                'aircraft': 'Global 5000',
                'avoid': set()
            },
            {
                'count': '1',
                'departure_airport': 'KIV',
                'arrival_airport': 'RIX',
                'pax': 1,
                'aircraft': 'Global 5000',
                'avoid': set()
            }
        ]
        query = ' KIV - RIX 1 Global 5000\n' \
                '2. RIX-VKO 1 Global 5000'
        with self.assertRaises(ValueError) as e:
            bot.get_query_structure(query)
        self.assertEqual(INVALID_QUERY_COUNT, e.exception.args[0])

    def test_incorrect_query(self):
        query = 'KIV'
        with self.assertRaises(ValueError) as e:
            bot.get_query_structure(query)
        self.assertEqual(INVALID_QUERY, e.exception.args[0])
        query = 'KIV-RIX'
        with self.assertRaises(ValueError) as e:
            bot.get_query_structure(query)
        self.assertEqual(INVALID_QUERY, e.exception.args[0])
        query = 'KIV-RIX 10'
        with self.assertRaises(ValueError) as e:
            bot.get_query_structure(query)
        self.assertEqual(INVALID_QUERY, e.exception.args[0])
        query = 'KI-RIX 1 Global 5000 (IASA regulations)'
        with self.assertRaises(ValueError) as e:
            bot.get_query_structure(query)
        self.assertEqual(INVALID_QUERY, e.exception.args[0])
        query = 'KIV-RI 1 Global 5000 (IASA regulations)'
        with self.assertRaises(ValueError) as e:
            bot.get_query_structure(query)
        self.assertEqual(INVALID_QUERY, e.exception.args[0])
        query = 'KIV-RI 1 Gl'
        with self.assertRaises(ValueError) as e:
            bot.get_query_structure(query)
        self.assertEqual(INVALID_QUERY, e.exception.args[0])


class APIRequestTest(unittest.TestCase):
    def test_airport_correct_request(self):
        query = 'UUWW'
        answer = {
            'airport_icao': 'UUWW',
            'airport_iata': 'VKO',
            'airport_name': 'Vnukovo'
        }
        self.assertEqual(aviapages_api.get_airport_parameters(query, ''), answer)
        query = 'HIR'
        answer = {
            'airport_icao': 'AGGH',
            'airport_iata': 'HIR',
            'airport_name': 'Honiara Intl Henderson Field'
        }
        self.assertEqual(aviapages_api.get_airport_parameters(query, ''), answer)
        query = 'Geneva'
        answer = {
            'airport_icao': 'LSGG',
            'airport_iata': 'GVA',
            'airport_name': 'Geneva'
        }
        self.assertEqual(aviapages_api.get_airport_parameters(query, ''), answer)

    def test_airport_incorrect_request(self):
        query = 'QQXX'
        with self.assertRaises(RuntimeError) as e:
            aviapages_api.get_airport_parameters(query, 'Departure')
        self.assertEqual('⚠️ Departure airport not found ⚠️', e.exception.args[0])
        query = 'hdggfd gfdgfd'
        with self.assertRaises(RuntimeError) as e:
            aviapages_api.get_airport_parameters(query, 'Arrival')
        self.assertEqual('⚠️ Arrival airport not found ⚠️', e.exception.args[0])

    def test_calculator_correct(self):
        departure = {
            'airport_icao': 'UUWW',
            'airport_iata': 'VKO',
            'airport_name': 'Vnukovo'
        }
        arrival = {
            'airport_icao': 'LSGG',
            'airport_iata': 'GVA',
            'airport_name': 'Geneva'
        }
        aircraft = 'Challenger 300'
        pax = 3
        avoid = {'countries': [], 'firs': []}
        answer = {
            'airway_time': '03:05',
            'airway_distance': 2426.934,
            'warnings': []
        }
        self.assertEqual(aviapages_api.calculate_flight_parameters(departure, arrival, aircraft, pax, avoid), answer)
        departure = {
            'airport_icao': 'LSGG',
            'airport_iata': 'GVA',
            'airport_name': 'Geneva'
        }
        arrival = {
            'airport_icao': 'UUWW',
            'airport_iata': 'VKO',
            'airport_name': 'Vnukovo'
        }
        aircraft = 'Challenger 300'
        pax = 2
        avoid = {'countries': [], 'firs': []}
        answer = {
            'airway_time': '03:05',
            'airway_distance': 2426.934,
            'warnings': []
        }
        self.assertEqual(aviapages_api.calculate_flight_parameters(departure, arrival, aircraft, pax, avoid), answer)
        departure = {
            'airport_icao': 'LSGG',
            'airport_iata': '',
            'airport_name': ''
        }
        arrival = {
            'airport_icao': '',
            'airport_iata': 'VKO',
            'airport_name': ''
        }
        aircraft = 'Challenger 300'
        pax = 2
        avoid = {'countries': [], 'firs': []}
        answer = {
            'airway_time': '03:05',
            'airway_distance': 2426.934,
            'warnings': []
        }
        self.assertEqual(aviapages_api.calculate_flight_parameters(departure, arrival, aircraft, pax, avoid), answer)
        departure = {
            'airport_icao': 'LSGG',
            'airport_iata': '',
            'airport_name': ''
        }
        arrival = {
            'airport_icao': '',
            'airport_iata': 'VKO',
            'airport_name': ''
        }
        aircraft = 'Challenger 300'
        pax = 2
        avoid = {'countries': [], 'firs': []}
        answer = {
            'airway_time': '03:05',
            'airway_distance': 2426.934,
            'warnings': []
        }
        self.assertEqual(aviapages_api.calculate_flight_parameters(departure, arrival, aircraft, pax, avoid), answer)

    def test_calculator_correct_avoid(self):
        departure = {
            'airport_icao': '',
            'airport_iata': 'KIV',
            'airport_name': ''
        }
        arrival = {
            'airport_icao': '',
            'airport_iata': 'VKO',
            'airport_name': ''
        }
        aircraft = 'Challenger 300'
        pax = 1
        avoid = {'countries': ['Ukraine', 'Belarus'], 'firs': []}
        answer = {
            'airway_time': '02:58',
            'airway_distance': 2322.858,
            'warnings': []
        }
        self.assertEqual(aviapages_api.calculate_flight_parameters(departure, arrival, aircraft, pax, avoid), answer)
        departure = {
            'airport_icao': '',
            'airport_iata': 'KIV',
            'airport_name': ''
        }
        arrival = {
            'airport_icao': '',
            'airport_iata': 'VKO',
            'airport_name': ''
        }
        aircraft = 'Challenger 300'
        pax = 1
        avoid = {'countries': ['Ukraine', 'Belarus'], 'firs': []}
        answer = {
            'airway_time': '02:58',
            'airway_distance': 2322.858,
            'warnings': []
        }
        self.assertEqual(aviapages_api.calculate_flight_parameters(departure, arrival, aircraft, pax, avoid), answer)
        departure = {
            'airport_icao': '',
            'airport_iata': 'KIV',
            'airport_name': ''
        }
        arrival = {
            'airport_icao': '',
            'airport_iata': 'VKO',
            'airport_name': ''
        }
        aircraft = 'Challenger 300'
        pax = 5
        avoid = {'countries': [], 'firs': ['ULAA', 'UHMM']}
        answer = {
            'airway_time': '01:35',
            'airway_distance': 1134.879,
            'warnings': []
        }
        self.assertEqual(aviapages_api.calculate_flight_parameters(departure, arrival, aircraft, pax, avoid), answer)

    def test_calculator_incorrect(self):
        with self.assertRaises(RuntimeError) as e:
            departure = {
                'airport_icao': 'ANYN',
                'airport_iata': '',
                'airport_name': ''
            }
            arrival = {
                'airport_icao': '',
                'airport_iata': 'VKO',
                'airport_name': ''
            }
            aircraft = 'Challenger 300'
            pax = 2
            avoid = {'countries': [], 'firs': []}
            aviapages_api.calculate_flight_parameters(departure, arrival, aircraft, pax, avoid)
        self.assertEqual('⚠️\nWeight exceeded, please reduce payload or choose a techstop\n⚠️', e.exception.args[0])

    def test_avoid_parser(self):
        query = {'Ukraine', 'Belarus'}
        answer = {'countries': {'Ukraine', 'Belarus'}, 'firs': set()}
        self.assertEqual(aviapages_api.get_avoid_parameters(query), answer)
        query = {'Ukraine', 'UHMM'}
        answer = {'countries': {'Ukraine'}, 'firs': {'UHMM'}}
        self.assertEqual(aviapages_api.get_avoid_parameters(query), answer)
        query = {'USA', 'ULAA'}
        answer = {'countries': {'USA'}, 'firs': {'ULAA'}}
        self.assertEqual(aviapages_api.get_avoid_parameters(query), answer)

    # def test_aircraft_correct_request(self):
    #     query = 'Challenger 300'
    #     answer = {
    #         'aircraft_profile_name': 'Challenger 300'
    #     }
    #     self.assertEqual(aviapages_api.get_aircraft_parameters(query), answer)
    #     query = 'GL5T'
    #     answer = {
    #         'aircraft_profile_name': 'Global 5000 M085'
    #     }
    #     self.assertEqual(aviapages_api.get_aircraft_parameters(query), answer)
    #
    # def test_aircraft_incorrect_request(self):
    #     query = 'UUYY'
    #     with self.assertRaises(RuntimeError) as e:
    #         aviapages_api.get_aircraft_parameters(query)
    #     self.assertEqual('Aircraft not found', e.exception.args[0])
    #     query = 'jghjhg ewrerew'
    #     with self.assertRaises(RuntimeError) as e:
    #         aviapages_api.get_aircraft_parameters(query)
    #     self.assertEqual('Aircraft not found', e.exception.args[0])


if __name__ == '__main__':
    unittest.main()
