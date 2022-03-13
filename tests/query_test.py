import unittest
import bot
import aviapages_api

INVALID_QUERY = '⚠️ Invalid query ⚠️'


class QueryTest(unittest.TestCase):

    def test_correct_query(self):
        query = 'UUWW - EVRA 2Pax Challenger 300'
        answer = {
            'departure_airport': 'UUWW',
            'arrival_airport': 'EVRA',
            'pax': 2,
            'aircraft': 'Challenger 300'
        }
        self.assertEqual(bot.get_query_structure(query), answer)
        query = 'KIV-RIX 3 E35L'
        answer = {
            'departure_airport': 'KIV',
            'arrival_airport': 'RIX',
            'pax': 3,
            'aircraft': 'E35L'
        }
        self.assertEqual(bot.get_query_structure(query), answer)
        query = 'Heathrow - Geneva 3 pax Global 5000 (IASA regulations)'
        answer = {
            'departure_airport': 'Heathrow',
            'arrival_airport': 'Geneva',
            'pax': 3,
            'aircraft': 'Global 5000 (IASA regulations)'
        }
        self.assertEqual(bot.get_query_structure(query), answer)
        query = 'KIV-- RIX 3 PAX E35L'
        answer = {
            'departure_airport': 'KIV',
            'arrival_airport': 'RIX',
            'pax': 3,
            'aircraft': 'E35L'
        }
        self.assertEqual(bot.get_query_structure(query), answer)
        query = 'KIV -  RIX  35  PAX   E35L'
        answer = {
            'departure_airport': 'KIV',
            'arrival_airport': 'RIX',
            'pax': 35,
            'aircraft': 'E35L'
        }
        self.assertEqual(bot.get_query_structure(query), answer)

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
        query = 'KIV-RIX 0000 Global 5000 (IASA regulations)'
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
        answer = {
            'airway_time': '03:05',
            'airway_distance': 2426.934,
            'warnings': []
        }
        self.assertEqual(aviapages_api.calculate_flight_parameters(departure, arrival, aircraft, pax), answer)
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
        answer = {
            'airway_time': '03:05',
            'airway_distance': 2426.934,
            'warnings': []
        }
        self.assertEqual(aviapages_api.calculate_flight_parameters(departure, arrival, aircraft, pax), answer)
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
        answer = {
            'airway_time': '03:05',
            'airway_distance': 2426.934,
            'warnings': []
        }
        self.assertEqual(aviapages_api.calculate_flight_parameters(departure, arrival, aircraft, pax), answer)

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
            answer = {
                'airway_time': '03:05',
                'airway_distance': 2426.934,
                'warnings': []
            }
            aviapages_api.calculate_flight_parameters(departure, arrival, aircraft, pax)
        self.assertEqual('⚠️\nWeight exceeded, please reduce payload or choose a techstop\n⚠️', e.exception.args[0])

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
