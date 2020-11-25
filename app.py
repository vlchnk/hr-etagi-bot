import logging
from bot import hr_data
import os
from req import insert_chat_data, insert_chatid, select_chatid, delete_chatid, ries_oauth, auth_handle, candidate_tickets, create_comment, ries_api

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

PORT = int(os.environ.get('PORT', 5000))

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# dialogue /start
RIES_TOKEN, REPLY_TOKEN, PHONE, DIALOGUE = range(4)

# dialogue /sobes
NUMBER_ROUTE, REPLY_ROUTE, DIALOGUE_SOBES, NUMBER_ID = range(4)


# dialogue /start
# Start dialogue /start
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Привет, я HRbot. Укажи свой код пользователя РИЕС.'
    )
    user = update.message
    logger.info("Start dialogue - %s, %s, %s, %s, %s", user.from_user, user.from_user.id, user.from_user.username,
                user.chat.id, user.date)
    return RIES_TOKEN


def reply_token(update: Update, context: CallbackContext) -> int:
    logger.info("Answer %s", update.message.text)
    if update.message.text == 'Да':
        text = 'Укажи номер телефона кандидата, с которым будет идти перпеписка. \n' \
               'В формате: 79998887766'
        update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardRemove(),
        )
        return PHONE
    else:
        logger.info("Reply ries token %s: ", update.message.text)
        text = 'Укажите свой код пользователя'
        update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardRemove(),
        )
        return RIES_TOKEN


def ries_token(update: Update, context: CallbackContext) -> int:
    response = ries_api(update.message.text).json()
    logger.info(response)

    reply_keyboard = [['Да', 'Нет']]

    if response['data']:
        user = response['data'][0]['fio']
        logger.info("Ries - fio: %s, id: %s", response['data'][0]['fio'], update.message.text)
        text = f'Это вы {user}?'
        context.user_data['ries'] = update.message.text
        update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        return REPLY_TOKEN
    else:
        logger.info("Reply ries token %s: ", update.message.text)
        text = 'Укажите свой код пользователя'
        update.message.reply_text(text)
        return RIES_TOKEN


def phone(update: Update, context: CallbackContext) -> int:
    logger.info("Phone - %s: ", update.message.text)
    context.user_data['phone'] = update.message.text
    data = update.message
    insert_chatid(data)
    text = 'Отлично! Теперь нужно очистить историю переписки и можно приглашать кандидата'
    update.message.reply_text(
        text
    )

    return DIALOGUE


def dialogue(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    text = update.message.text
    data = update.message
    ries = context.user_data['ries']
    phone = context.user_data['phone']
    insert_chat_data(data, phone, ries)
    logger.info("Chatting in group chat. User %s. Text - %s", user.first_name, text)
    return DIALOGUE


# End dialogue /start
def end(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    data = update.message
    logger.info("User %s canceled the conversation.", user.first_name)
    type = update.message.chat.type
    if type == 'group':
        delete_chatid(data)

    update.message.reply_text(
        'Пока! Чат завершен', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


# Handler group message
def group_message(update: Update, context: CallbackContext):
    user = update.message.from_user
    text = update.message.text
    data = update.message
    type = update.message.chat.type
    if type == 'group':
        ans = select_chatid(data)
        if ans:
            insert_chat_data(data)
        logger.info("Chatting in group chat. User %s. Text - %s", user.first_name, text)
    elif type == 'private':
        logger.info("Chatting in private chat. User %s. Text - %s", user.first_name, text)


# dialogue /sobes
# Start dialogue /sobes
def sobes(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Укажи свой код пользователя РИЕС'
    )
    user = update.message
    logger.info("Start dialogue - %s, %s, %s, %s, %s", user.from_user, user.from_user.id, user.from_user.username,
                user.chat.id, user.date)
    logger.info(context)
    return NUMBER_ROUTE


# Get number phone
def number_route(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['ries_code'] = text
    print('ries code: ', context.user_data['ries_code'])
    update.message.reply_text(
        'Укажи номер телефона кандидата в формате: 79998887766'
    )
    user = update.message
    logger.info("Start dialogue - %s, %s, %s, %s, %s", user.from_user, user.from_user.id, user.from_user.username,
                user.chat.id, user.date)
    logger.info(context)
    return REPLY_ROUTE


# Get number route
def number_id(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    try:
        id = context.user_data[str(text)]
        context.user_data['id'] = id
        message = f'Отлично! Все сообщения будут записаны в комментарии маршрута: {id}\n' \
                  f'По окончанию напишите команду /end для завершения диалога'
        update.message.reply_text(
            message
        )
        user = update.message
        logger.info("Start dialogue - %s, %s, %s, %s, %s", user.from_user, user.from_user.id, user.from_user.username,
                    user.chat.id, user.date)
        logger.info(context)
        return DIALOGUE_SOBES
    except:
        message = 'Введите id из вышеуказанного списка'
        update.message.reply_text(
            message
        )
        user = update.message
        logger.info("Start dialogue - %s, %s, %s, %s, %s", user.from_user, user.from_user.id, user.from_user.username,
                    user.chat.id, user.date)
        logger.info(context)
        return NUMBER_ID


# Get number id
def reply_route(update: Update, context: CallbackContext) -> int:
    print('ries code: ', context.user_data['ries_code'])
    ries = context.user_data['ries_code']
    text = update.message.text
    print('phone: ', text)
    oauth_token = ries_oauth()
    session_id = auth_handle(oauth_token)
    json = session_id.json()
    context.user_data['session_id'] = json['sessionId']
    tickets = candidate_tickets(session_id, ries, text)
    if tickets:
        tickets_json = tickets.json()
        count = tickets_json['count']
        if count > 1:
            message = ''
            update.message.reply_text(
                'Введите id нужного маршрута'
            )
            for el in tickets_json['list']:
                id = el['id']
                context.user_data[str(id)] = id
                candidate_fio = el['candidate']['fullName']
                message += 'id: ' + str(id) + ' - ' + candidate_fio + '\n'
            update.message.reply_text(
                message
            )
            return NUMBER_ID
        elif count == 1:
            id = tickets_json['list'][0]['id']
            candidate_fio = tickets_json['list'][0]['candidate'][
                'fullName']
            id_fio = 'id: ' + str(id) + ' - ' + candidate_fio + '\n'
            message = f'Отлично! Все сообщения будут записаны в комментарии маршрута:\n' \
                      f'{id_fio}' \
                      f'По окончанию напишите команду /end для завершения диалога'
            context.user_data['id'] = id
            update.message.reply_text(
                message
            )
            user = update.message
            logger.info("Start dialogue - %s, %s, %s, %s, %s", user.from_user, user.from_user.id, user.from_user.username,
                        user.chat.id, user.date)
            logger.info(context)
            return DIALOGUE_SOBES
        else:
            message = 'Маршрут не найден, попробуйте еще раз. \n'
            update.message.reply_text(
                message
            )
            update.message.reply_text(
                'Укажи свой код пользователя РИЕС'
            )
            return NUMBER_ROUTE
    else:
        message = 'Что-то пошло не так, попробуйте еще раз. \n'
        update.message.reply_text(
            message
        )
        update.message.reply_text(
            'Укажи свой код пользователя РИЕС'
        )
        return NUMBER_ROUTE


# Get number route
def dialogue_sobes(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    user = update.message
    session = context.user_data['session_id']
    id = context.user_data['id']
    response = create_comment(session, str(id), text)
    if response:
        json = response.json()
        logger.info("Comment added - id: %s,fullname: %s", json['id'], json['user']['fullName'])
    logger.info("Start dialogue - %s, %s, %s, %s, %s", user.from_user, user.from_user.id, user.from_user.username,
                user.chat.id, user.date)
    logger.info(context)
    return DIALOGUE_SOBES


def main() -> None:
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token=hr_data.bot['token'], use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    group_mess = MessageHandler(Filters.text & ~Filters.command, group_message)

    # Add conversation handler /start
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            RIES_TOKEN: [MessageHandler(Filters.text & ~Filters.command, ries_token)],
            REPLY_TOKEN: [MessageHandler(Filters.regex('^(Да|Нет)$') & ~Filters.command, reply_token)],
            PHONE: [MessageHandler(Filters.text & ~Filters.command, phone)],
            DIALOGUE: [MessageHandler(Filters.text & ~Filters.command, dialogue)],
        },
        fallbacks=[CommandHandler('end', end)],
    )

    # Add conversation handler /sobes
    conv_sobes = ConversationHandler(
        entry_points=[CommandHandler('sobes', sobes)],
        states={
            NUMBER_ROUTE: [MessageHandler(Filters.text & ~Filters.command, number_route)],
            REPLY_ROUTE: [MessageHandler(Filters.text & ~Filters.command, reply_route)],
            DIALOGUE_SOBES: [MessageHandler(Filters.text & ~Filters.command, dialogue_sobes)],
            NUMBER_ID: [MessageHandler(Filters.text & ~Filters.command, number_id)],
        },
        fallbacks=[CommandHandler('end', end)],
    )

    dispatcher.add_handler(conv_sobes)
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(group_mess)

    # # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT))
    updater.bot.setWebhook(hr_data.bot['url'])

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()