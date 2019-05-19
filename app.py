from bot import PastebinBot
import tokens


def main():
    bot = PastebinBot(tokens.TG_TOKEN, tokens.PB_TOKEN)
    bot.run_loop()


if __name__ == '__main__':
    main()
