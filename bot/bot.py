import telebot

bot = telebot.TeleBot('6470937115:AAGpQLFJe3_zXyfpHaLIlinibs0i60uVX8M')
photo_path = 'statistics_graph/stat.jpg'
users_id = [1010612567] #, 900721585 464436154,

@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.from_user.id, 'Здравствуйте, уважаемый босс РЖД!')

def send_stat_to_users(user_id, photo_path):
    for user_id in users_id:
        with open(photo_path, 'rb') as photo:
            bot.send_message(user_id, 'Обновлена статистика.')
            bot.send_photo(user_id, photo)


def send_report(file_path):
    for user_id in users_id:
        with open(file_path, 'rb') as file:
            bot.send_document(user_id, file)

send_stat_to_users(users_id, photo_path)
bot.polling(none_stop=True)

