from apscheduler.schedulers.background import BackgroundScheduler


def start(bot, chat_id):
    scheduler = BackgroundScheduler()

    scheduler.start()
