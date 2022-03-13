import logging
import os
import aviapages_api
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode

logging.basicConfig(level=logging.INFO)


class TelegramBot:
    def __init__(self):
        logger = logging.getLogger('TELEGRAM BOT')

        bot_token = os.environ.get('BOT_TOKEN')

        # Main telegram UPDATER
        self.updater = Updater(token=bot_token, use_context=True)
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
    def __init__(self):
        pass

    def start(self, update, context) -> None:
        user = update.effective_chat

        # Welcome message
        message = f'<b>Hi, {user.full_name}!</b>\n' \
                  f'With my help you can calculate flight time, route, fuel estimation, etc.\n'
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=message,
                                 parse_mode=ParseMode.HTML)
        self.info_message(update, context)

    def unknown(self, update, context) -> None:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='⚠️ <i>Unknown command</i> ⚠️',
                                 parse_mode=ParseMode.HTML)
        self.info_message(update, context)

    def error(self, update, context) -> None:
        error_message = context.error.args[0]
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'<i>{error_message}</i>',
                                 parse_mode=ParseMode.HTML)
        self.info_message(update, context)

    def info_message(self, update, context) -> None:
        message = f'<i>Enter query in the format</i>:\n' \
                  f'[<b>DEPARTURE AIRPORT</b> ICAO/IATA/NAME] <b>-</b> [<b>ARRIVAL AIRPORT</b> ICAO/IATA/NAME] [<b>PASSENGER COUNT(PAX)</b>] [<b>AIRCRAFT</b>]\n\n' \
                  f'<i>Examples</i>:\n' \
                  f' 🔘 UUWW - EVRA 2Pax Challenger 300\n' \
                  f' 🔘 KIV-RIX 3 E35L\n' \
                  f' 🔘 Heathrow - Geneva 3 pax Global 5000 (IASA regulations)'
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=message,
                                 parse_mode=ParseMode.HTML)

    def user_message(self, update, context) -> None:
        query = get_query_structure(update.message.text)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=aviapages_api.generate_calculator_message(query),
                                 parse_mode=ParseMode.HTML)
        self.info_message(update, context)


def get_query_structure(text: str) -> dict:
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

    # AIRCRAFT
    if text[:3].upper() == 'PAX':
        aircraft = text[3:].strip()
    else:
        aircraft = text.strip()

    if len(aircraft) < 3:
        raise ValueError(invalid_query)

    return {
        'departure_airport': departure_airport,
        'arrival_airport': arrival_airport,
        'pax': int(pax),
        'aircraft': aircraft
    }


if __name__ == '__main__':
    print('Only for import!')
