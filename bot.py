import logging
import os
import aviapages_api
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode

logging.basicConfig(level=logging.INFO)


class TelegramBot:
    def __init__(self):
        logger = logging.getLogger('TELEGRAM BOT')

        # Main telegram UPDATER
        self.updater = Updater(token=os.environ.get('BOT_TOKEN'), use_context=True)
        self.dispatcher = self.updater.dispatcher

        # Handlers
        handler = TelegramHandler()
        self.dispatcher.add_handler(CommandHandler('start', handler.start))
        self.dispatcher.add_handler(MessageHandler(Filters.text, handler.user_message))
        self.dispatcher.add_handler(MessageHandler(Filters.command, handler.unknown))
        self.dispatcher.add_error_handler(handler.error)

        # Starting the bot
        self.updater.start_polling()

        logger.info('Flight time calculator BOT started')


class TelegramHandler:

    @classmethod
    def start(cls, update, context) -> None:
        user = update.effective_chat

        # Welcome message
        message = f'<b>Hi, {user.full_name}!</b>\n' \
                  f'With my help you can calculate flight time, route, fuel estimation, etc.\n'
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=message,
                                 parse_mode=ParseMode.HTML)
        cls.info_message(update, context)

    @classmethod
    def unknown(cls, update, context) -> None:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='⚠️ <i>Unknown command</i> ⚠️',
                                 parse_mode=ParseMode.HTML)
        cls.info_message(update, context)

    @classmethod
    def error(cls, update, context) -> None:
        error_message = context.error.args[0]
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'<i>{error_message}</i>',
                                 parse_mode=ParseMode.HTML)
        cls.info_message(update, context)

    @classmethod
    def user_message(cls, update, context) -> None:
        query = get_query_structure(update.message.text)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=aviapages_api.generate_calculator_message(query),
                                 parse_mode=ParseMode.HTML)
        cls.info_message(update, context)

    @staticmethod
    def info_message(update, context) -> None:
        message = f'<i>Enter query in the format</i>:\n' \
                  f'[<b>DEPARTURE AIRPORT</b> ICAO/IATA/NAME] <b>-</b> [<b>ARRIVAL AIRPORT</b> ICAO/IATA/NAME] [<b>PASSENGER COUNT(PAX)</b>] [<b>AIRCRAFT</b>] [<b>no COUNTRIES, FIRs</b>]*\n\n' \
                  f'🟢 <b>*</b> - optional\n' \
                  f'🟢 <b>Use multilines to add leg(s)</b>\n\n' \
                  f'<i>Examples</i>:\n' \
                  f' 🔘 UUWW - EVRA 2Pax Challenger 300\n' \
                  f' 🔘 KIV-RIX 3 E35L\n' \
                  f' 🔘 Heathrow - Geneva 3 pax Global 5000 (IASA regulations)\n' \
                  f' 🔘 KIV - VKO 2 pax Global 5000 no UHMM, Belarus\n' \
                  f' 🔘 EVRA - UUWW 5 Challenger 300 no ULAA, Ukraine\n' \
                  f' 🔘 KIV-RIX 3 E35L\n' \
                  f'       RIX-VKO 3 Challenger 300'
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=message,
                                 parse_mode=ParseMode.HTML)


def get_query_structure(text: str) -> list:
    query_structures = []
    query_parts = text.split('\n')
    for query in query_parts:
        if len(query.strip()) > 0:
            query_structures.append(get_query_part_structure(query))

    return query_structures


def get_query_part_structure(text: str) -> dict:
    invalid_query = '⚠️ Invalid query ⚠️'

    # Text preparation for processing
    text = text.strip()
    # Removing duplicated "-"
    text = text.replace('—', '--')
    for i in range(4, 1, -1):
        text = text.replace('-' * i, '-')

    text_parts = text.split('-', 1)

    if len(text_parts) < 2:
        raise ValueError(invalid_query)

    # DEPARTURE
    departure_airport = text_parts[0].strip()
    if len(departure_airport) < 3:
        raise ValueError(invalid_query)

    # Current processing text update
    text = text_parts[1].strip()

    # ARRIVAL
    arrival_airport = ''
    for i in range(len(text)):
        if text[i].isnumeric():
            arrival_airport = text[:i].strip()
            # Current processing text update
            text = text[i:].strip()
            break

    if len(arrival_airport) < 3 or len(text) == 0:
        raise ValueError(invalid_query)

    # PASSENGER COUNT
    text_len = len(text)
    pax = ''
    for i in range(text_len):
        if i == text_len - 1:
            raise ValueError(invalid_query)
        elif text[i].isnumeric():
            pax += text[i]
        else:
            # Current processing text update
            text = text[i:].strip()
            break

    if len(pax) == 0:
        raise ValueError(invalid_query)

    # Current processing text update
    if text[:3].upper() == 'PAX':
        text = text[3:].strip()
    else:
        text = text.strip()
    text_len = len(text)

    # AIRCRAFT
    aircraft = ''
    for i in range(text_len):
        if text[i:i+3] == 'no ':
            break
        else:
            aircraft += text[i]

    if len(aircraft) < 3:
        raise ValueError(invalid_query)

    # Current processing text update
    text = text[i+3:].strip()
    text_len = len(text)

    # AVOID
    avoid = set()
    current_avoid = ''
    for i in range(text_len):
        if text[i] == ',' or text[i] == ';':
            avoid.add(current_avoid.strip())
            current_avoid = ''
        else:
            current_avoid += text[i]
            if i == text_len - 1:
                avoid.add(current_avoid.strip())

    return {
        'departure_airport': departure_airport,
        'arrival_airport': arrival_airport,
        'pax': int(pax),
        'aircraft': aircraft.strip(),
        'avoid': avoid
    }


if __name__ == '__main__':
    print('Only for import!')
