from telegram.ext import Updater, CommandHandler, MessageHandler, filters
import traceback
import sqlite3
from paste import paste
import os
from database_manager import DBManager, db_exception_keeper
from misc import MAX_MESSAGE_LENGTH, MAX_COMMENT_LENGTH, PASTE_FORMATS,\
    EXPIRE_DATES


class PastebinBot:
    def __init__(self, tg_token, pb_token):
        self.tg_token = tg_token
        self.pb_token = pb_token
        self.db_manager = DBManager()
        
        self.updater = Updater(token=self.tg_token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        
        add_paste_handler = MessageHandler(filters.Filters.document,
                                           self._add_paste)
        self.dispatcher.add_handler(add_paste_handler)
        
        start_handler = CommandHandler('start', self._start)
        self.dispatcher.add_handler(start_handler)

        help_handler = CommandHandler('help', self._help)
        self.dispatcher.add_handler(help_handler)
        
        get_handler = CommandHandler('get', self._get)
        self.dispatcher.add_handler(get_handler)
        
        get_settings_handler = CommandHandler('settings', self._get_settings)
        self.dispatcher.add_handler(get_settings_handler)
        
        delete_link_handler = CommandHandler('deletelink', self._delete_link)
        self.dispatcher.add_handler(delete_link_handler)

        delete_by_tag_handler = CommandHandler('deletebytag', self.
                                               _delete_by_tag)
        self.dispatcher.add_handler(delete_by_tag_handler)

        set_tag_handler = CommandHandler('settag', self._set_tag)
        self.dispatcher.add_handler(set_tag_handler)

        set_private_handler = CommandHandler('setprivate', self._set_private)
        self.dispatcher.add_handler(set_private_handler)

        set_paste_format_handler = CommandHandler('setpasteformat',
                                                  self._set_paste_format)
        self.dispatcher.add_handler(set_paste_format_handler)
        
        set_expire_date_handler = CommandHandler('setexpiredate',
                                                 self._set_expire_date)
        self.dispatcher.add_handler(set_expire_date_handler)
        
        self.paste_formats = PASTE_FORMATS
        
        self.expire_dates = EXPIRE_DATES
        
    @db_exception_keeper
    def _get_settings(self, update, context):
        user_info = self.db_manager.get_user_info(update.message.chat_id)[0]
        user_info = list(user_info)
        user_info[1] = ': ' + user_info[1] if user_info[1] != '' else\
            'а нет'
        user_info[2] = self.expire_dates[user_info[2]]
        user_info[4] = 'public' if user_info[4] == 0 else 'unlisted'
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text='Текущие настройки:\n'
                                      'Тэг{1}\n'
                                      'Время жизни ссылки: {2}\n'
                                      'Формат: {3}\n'
                                      'Режим приватности: {4}'.
                                      format(*user_info))

    @db_exception_keeper
    def _set_expire_date(self, update, context):
        flag = False
        if len(update.message.text.split()) == 2 and (
                update.message.text.split()[1] == self.expire_dates['N']):
            flag = True
            
        if not flag and (len(update.message.text.split()) != 3 or not (
               ' '.join(update.message.text.split()[1:2]) in self.
                expire_dates.values())):
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text='Введите корректное время жизни '
                                          'для ссылки  после /setexpiredate '
                                          'из следующих:\n' +
                                          '\n'.join(self.expire_dates.values()))
            return
        self.db_manager.update_expire_date(update.message.chat_id,
                                           {v: k for k, v in self.expire_dates.
                                            items()}[update.message.
                                                     text.split()[1]])
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text='Время жизни ссылки установлено')

    @db_exception_keeper
    def _delete_link(self, update, context):
        if len(update.message.text.split()) == 1:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text='Введите ссылку для удаления')
            return
        
        if len(update.message.text.split()) != 2 or not (
                update.message.text.split()[1].
                startswith('https://pastebin.com/')) or (
                len(update.message.text.split()[1]) !=
                len('https://pastebin.com/12345678')):
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text='Ссылка некорректна')
            return
        
        if len(self.db_manager.get_link(update.message.chat_id,
                                        update.message.text.split()[1])) == 0:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text='Ссылка не найдена')
            return
        
        self.db_manager.delete_link(update.message.chat_id,
                                    update.message.text.split()[1])
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text='Ссылка удалена')
    
    @db_exception_keeper
    def _delete_by_tag(self, update, context):
        if len(update.message.text.split()) < 2:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text='Введите тэг')
            return
        
        links = self.db_manager.get_links_by_tag(update.message.chat_id,
                                                 ''.join(update.message.text.
                                                         split()[1:]))
        if len(links) == 0:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text='Ссылок не найдено')
            return
        
        for link in links:
            self.db_manager.delete_link(update.message.chat_id, link[5])
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text='Ссылки удалены')

    @db_exception_keeper
    def _set_private(self, update, context):
        if len(update.message.text.split()) == 2 and (
                update.message.text.split()[1] in ('public', 'unlisted')):
            self.db_manager.update_private(update.message.chat_id, 0 if update.
                                           message.text.
                                           split()[1] == 'public' else 1)
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text='Режим приватности установлен')
        elif len(update.message.text) == 1:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text='Укажите режим приватности: '
                                          'public или unlisted')
        else:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text='Режим приватности должен состоять из'
                                          ' одного слова: public или unlisted')
    
    @db_exception_keeper
    def _set_paste_format(self, update, context):
        if len(update.message.text.split()) == 2:
            self.db_manager.update_paste_format(update.message.chat_id, update.
                                                message.text.split()[1])
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text='Формат установлен')
        elif len(update.message.text) == 1:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text='Укажите формат')
        else:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text='Формат должен состоять из одного '
                                          'слова')
    
    @db_exception_keeper
    def _set_tag(self, update, context):
        if len(update.message.text.split()) > 1:
            self.db_manager.update_tag(update.message.chat_id, ''.join(update.
                                       message.text.split()[1:]) if update.
                                       message.text.split()[1] != '-e' else '')
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text='Тэг установлен')
        else:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text='Укажите тэг')
    
    @db_exception_keeper
    def _get(self, update, context):
        if len(update.message.text.split()) == 1:
            pastes = self.db_manager.get_links(update.message.chat_id)
            if len(pastes) == 0:
                context.bot.send_message(chat_id=update.message.chat_id,
                                         text='Ссылок не найдено')
                return
        else:
            pastes = self.db_manager.get_links_by_tag(update.message.chat_id,
                                                      ' '.join(
                                                          update.message.text.
                                                          split()[1:]))
        if len(pastes) == 0:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text='Ссылок по этому тегу '
                                          'не найдено')
            return
        response_message = ''
        for line in pastes:
            next_link = ' '.join(
                (line[4], '[' + line[2] + ']' if line[2] != '' else '',
                 line[1], line[5], line[3])) + '\n'
            if len(response_message) + len(next_link) > MAX_MESSAGE_LENGTH:
                context.bot.send_message(chat_id=update.message.chat_id,
                                         text=response_message)
                response_message = ''
            response_message += next_link
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=response_message)

    @db_exception_keeper
    def _start(self, update, context):
        if len(self.db_manager.get_user_info(update.message.chat_id)) == 0:
            self.db_manager.insert_user(update.message.chat_id)
        self._help(update, context)

    @staticmethod
    @db_exception_keeper
    def _help(update, context):
        with open('help') as help_text:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text=help_text.read())

    @db_exception_keeper
    def _add_paste(self, update, context):
        try:
            if len(update.message.caption) > MAX_COMMENT_LENGTH:
                context.bot.send_message(chat_id=update.message.chat_id,
                                         text='Слишком длинный комментарий')
                return
        except TypeError:
            pass
        user_info = self.db_manager.get_user_info(update.message.chat_id)[0]
        downloaded_file_name = update.message.document.get_file().download()
        with open(downloaded_file_name) as file:
            try:
                link = paste(code=file.read(),
                             name=update.message.document.file_name,
                             expire_date=user_info[2],
                             paste_format=self.paste_formats[
                                 downloaded_file_name.split('.')[-1]] if (
                                     len(downloaded_file_name.split('.')) > 1
                                     and downloaded_file_name.split('.')[-1]
                                     in self.paste_formats.keys()) else
                             user_info[3],
                             private=user_info[4])
            except UnicodeDecodeError as unicode_error:
                context.bot.send_message(chat_id=update.message.chat_id,
                                         text='Неподдерживаемый формат файла')
                os.unlink(downloaded_file_name)
                traceback.print_exc()
                raise unicode_error
            
            try:
                self.db_manager.insert_link(update.message.chat_id,
                                            update.message.document.file_name,
                                            user_info[1],
                                            update.message.caption if update.
                                            message.
                                            caption is not None else '',
                                            str(update.message.date),
                                            link)
                context.bot.send_message(chat_id=update.message.chat_id,
                                         text=link)
            except sqlite3.Error:
                traceback.print_exc()
            os.unlink(downloaded_file_name)

    def run_loop(self):
        self.updater.start_polling(poll_interval=0.01)
