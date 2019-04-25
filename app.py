from bot import PastebinBot
import misc


def main():
    bot = PastebinBot(misc.TGTOKEN, misc.PBTOKEN)
    bot.run_loop()


if __name__ == '__main__':
    main()
