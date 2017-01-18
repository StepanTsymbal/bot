# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSlot,SIGNAL,SLOT
from PyQt4.QtGui import *

import sys
import requests
import random
import time
import datetime
import logging
import json
import atexit
import signal
import itertools
import thread
from time import sleep
import re

from configobj import ConfigObj

from functools import partial

class UserInfo:
    '''
    This class try to take some user info (following, followers, etc.)
    '''
    user_agent = ("Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36")

    url_user_info = "https://www.instagram.com/%s/?__a=1"
    url_list = {
                "ink361":
                     {
                      "main": "http://ink361.com/",
                      "user": "http://ink361.com/app/users/%s",
                      "search_name": "https://data.ink361.com/v1/users/search?q=%s",
                      "search_id": "https://data.ink361.com/v1/users/ig-%s",
                      "followers": "https://data.ink361.com/v1/users/ig-%s/followed-by",
                      "following": "https://data.ink361.com/v1/users/ig-%s/follows",
                      "stat": "http://ink361.com/app/users/ig-%s/%s/stats"
                     }
               }

    def __init__(self, info_aggregator="ink361"):
        self.i_a = info_aggregator
        self.hello()

    def hello(self):
        self.s = requests.Session()
        self.s.headers.update({'User-Agent' : self.user_agent})
        main = self.s.get(self.url_list[self.i_a]["main"])
        if main.status_code == 200:
            return True
        return False

    def get_user_id_by_login(self, user_name):
        url_info= self.url_user_info % (user_name)
        info = self.s.get(url_info)
        all_data = json.loads(info.text)
        id_user = all_data['user']['id']
        return id_user


def loadData():
    
    global checkBoxLike
    global checkBoxFollow
    global checkBoxComment
    global checkBoxUnfollow

    try:
        config = ConfigObj(str(QFileDialog.getOpenFileName(None, "OpenFile", "", "Text files (*.txt)")),  encoding='utf8')
    
        checkBoxLike.setChecked(bool(config['Actions']['like']))
        checkBoxFollow.setChecked(bool(config['Actions']['follow']))
        checkBoxComment.setChecked(bool(config['Actions']['comment']))
        checkBoxUnfollow.setChecked(bool(config['Actions']['unfollow']))
        
        tagOutput.setText(config['Data']['tags'])
        blackTagOutput.setText(config['Data']['blackTags'])
        blackUserOutput.setText(config['Data']['blackUsers'])
        tagUsers.setText(config['Data']['users'])
        
        textboxLikesPerDay.setText(config['ActionsAmmount']['likesPerDay'])
        textboxCommentsPerDay.setText(config['ActionsAmmount']['commentsPerDay'])
        textboxMaxLikesFromOneTag.setText(config['ActionsAmmount']['likesOnOneTag'])
        textboxFollowsPerDay.setText(config['ActionsAmmount']['followsPerDay'])
        textboxUnfollowsPerDay.setText(config['ActionsAmmount']['unfollowsPerDay'])
        
        preparedComment.setText(config['Data']['preparedComments'])
        firstPartComment.setText(config['Data']['constructedComments']['firstPartComment'])
        secondPartComment.setText(config['Data']['constructedComments']['secondPartComment'])
        thirdPartComment.setText(config['Data']['constructedComments']['thirdPartComment'])
        fourthPartComment.setText(config['Data']['constructedComments']['fourthPartComment'])
    except(KeyError):
        None
    except:
        QtGui.QMessageBox.warning(None, "Warning!", 'Please choose valid Data file!' if normLang else u'Пожалуйста, выберите корректный файл с данными!')

    
def saveData():
    
    global checkBoxLike
    global checkBoxFollow
    global checkBoxComment
    global checkBoxUnfollow

    config = ConfigObj('config.ini', encoding='utf8')
    
    try:
        config.filename = QFileDialog.getSaveFileName(None, "OpenFile", "", "Text files (*.txt)")
    
        config['Actions'] = {}
        config['Actions']['like'] = 1 if checkBoxLike.isChecked() else ''
        config['Actions']['follow'] = True if checkBoxFollow.isChecked() else ''
        config['Actions']['comment'] = True if checkBoxComment.isChecked() else ''
        config['Actions']['unfollow'] = True if checkBoxUnfollow.isChecked() else ''
        
        config['ActionsAmmount'] = {}
        config['ActionsAmmount']['likesPerDay'] = textboxLikesPerDay.text()
        config['ActionsAmmount']['commentsPerDay'] = textboxCommentsPerDay.text()
        config['ActionsAmmount']['likesOnOneTag'] = textboxMaxLikesFromOneTag.text()
        config['ActionsAmmount']['followsPerDay'] = textboxFollowsPerDay.text()
        config['ActionsAmmount']['unfollowsPerDay'] = textboxUnfollowsPerDay.text()
        
        #
        section2 = {
            'tags': (unicode(tagOutput.toPlainText().toUtf8(), encoding="UTF-8")),
            'blackTags': (unicode(blackTagOutput.toPlainText().toUtf8(), encoding="UTF-8")),
            'blackUsers': (unicode(blackUserOutput.toPlainText().toUtf8(), encoding="UTF-8")),
            'users': (unicode(tagUsers.toPlainText().toUtf8(), encoding="UTF-8")),
            'preparedComments': (unicode(preparedComment.toPlainText().toUtf8(), encoding="UTF-8")),
            'constructedComments': {
                'firstPartComment': (unicode(firstPartComment.toPlainText().toUtf8(), encoding="UTF-8")),
                'secondPartComment': (unicode(secondPartComment.toPlainText().toUtf8(), encoding="UTF-8")),
                'thirdPartComment': (unicode(thirdPartComment.toPlainText().toUtf8(), encoding="UTF-8")),
                'fourthPartComment': (unicode(fourthPartComment.toPlainText().toUtf8(), encoding="UTF-8"))}
        }
        config['Data'] = section2
    
        config.write()
    except:
        None


def setEng():
    
    global normLang
    normLang = True
    
    buttonRus.setStyleSheet("QPushButton{font-size:11px}")
    buttonEng.setStyleSheet("QPushButton{font-size:11px; font:bold}")
    
    global tabs
    tabs.setTabText(0, 'Main Settings')
    tabs.setTabText(1, 'Users')
    tabs.setTabText(2, 'Comments')
    tabs.setTabText(3, 'Log and Statistics')
    
    global buttonClearStatistic
    buttonClearStatistic.setText('Clear statistic')
    
    global buttonClearLog
    buttonClearLog.setText('Clear log')
    
    global labelDescribeUser
    labelDescribeUser.setText('(one set login:password per row)')
        
    global labelDescribeTag
    labelDescribeTag.setText('(one hashtag per row)   ')

    global labelDescribeBlackTag
    labelDescribeBlackTag.setText('(one hashtag per row)   ')
        
    global labelDescribeBlackUser
    labelDescribeBlackUser.setText('(one black user per row)')
        
    global labelDescribeComment
    labelDescribeComment.setText('(one comment per row)')

    global constructRadioButton
    constructRadioButton.setText('Constructed')
    
    global preparedRadioButton
    preparedRadioButton.setText('Prepared')
    
    global buttonLoadComment
    buttonLoadComment.setText('Comments')

    global buttonLoadUser
    buttonLoadUser.setText('Users')
    
    global groupBoxActions
    groupBoxActions.setTitle('Actions')
    
    global groupBoxStatistic
    groupBoxStatistic.setTitle('Statistics')
    
    global label1
    label1.setText('likes:')
    
    global label2
    label2.setText('follows:')
    
    global label4
    label4.setText('unfollows:')
    
    global label3
    label3.setText('comments:')

    global checkBoxLike
    checkBoxLike.setText('Like')
    
    global checkBoxFollow
    checkBoxFollow.setText('Follow')

    global checkBoxComment
    checkBoxComment.setText('Comment')

    global checkBoxUnfollow
    checkBoxUnfollow.setText('Unfollow')
    
    global label5
    label5.setText('Likes per day')

    global label6
    label6.setText('Comments per day')

    global label7
    label7.setText('Max likes from one tag')

    global label8
    label8.setText('Follows per day')

    global label9
    label9.setText('Unfollows per day')
    
    global buttonStart
    buttonStart.setText('Start')
    
    global buttonStop
    buttonStop.setText('Stop')
    
    global buttonLoadTag
    buttonLoadTag.setText('Tags')

    global buttonLoadBlackTag
    buttonLoadBlackTag.setText('BlackTags')

    global buttonLoadBlackUser
    buttonLoadBlackUser.setText('BlackUsers')
    
    global buttonSaveSettings
    buttonSaveSettings.setText('Save Data')
    
    global buttonLoadSettings
    buttonLoadSettings.setText('Load Data')


def setRus():
    
    global normLang
    normLang = False
    
    buttonRus.setStyleSheet("QPushButton{font-size:11px; font:bold}")
    buttonEng.setStyleSheet("QPushButton{font-size:11px}")
    
    global tabs
    tabs.setTabText(0, u'Осн. настройки')
    tabs.setTabText(1, u'Пользователи')
    tabs.setTabText(2, u'Комментарии')
    tabs.setTabText(3, u'Отчет и статистика')
    
    global buttonClearStatistic
    buttonClearStatistic.setText(u'Очистить статистику')
    
    global buttonClearLog
    buttonClearLog.setText(u'Очистить лог')
    
    global labelDescribeUser
    labelDescribeUser.setText(u'(каждый набор пароль:логин \n с новой строки)')
        
    global labelDescribeTag
    labelDescribeTag.setText(u'(каждый хештег с новой \n             строки)')

    global labelDescribeBlackTag
    labelDescribeBlackTag.setText(u'(каждый хештег с новой \n             строки)')
        
    global labelDescribeBlackUser
    labelDescribeBlackUser.setText(u'(каждый пользователь \n        с новой строки)        ')
        
    global labelDescribeComment
    labelDescribeComment.setText(u'(каждый готовый ком-\nментарий с новой строки)')

    global constructRadioButton
    constructRadioButton.setText(u'Конструктор')
    
    global preparedRadioButton
    preparedRadioButton.setText(u'Готовые')
    
    global buttonLoadComment
    buttonLoadComment.setText(u'Комментарии')

    global buttonLoadUser
    buttonLoadUser.setText(u'Пользователи')
    
    global groupBoxActions
    groupBoxActions.setTitle(u'Действия')
    
    global groupBoxStatistic
    groupBoxStatistic.setTitle(u'Статистика')
    
    global label1
    label1.setText(u'лайков:')
    
    global label2
    label2.setText(u'подписок:')
    
    global label4
    label4.setText(u'отписок:')
    
    global label3
    label3.setText(u'комментариев:')

    global checkBoxLike
    checkBoxLike.setText(u'Лайкать')
    
    global checkBoxFollow
    checkBoxFollow.setText(u'Подписаться')

    global checkBoxComment
    checkBoxComment.setText(u'Комментировать')

    global checkBoxUnfollow
    checkBoxUnfollow.setText(u'Отписаться')
    
    global label5
    label5.setText(u'Лайков в сутки')

    global label6
    label6.setText(u'Комментариев в сутки')

    global label7
    label7.setText(u'Макс. лайков на один хештег')

    global label8
    label8.setText(u'Подписок в сутки')

    global label9
    label9.setText(u'Отписок в сутки')
    
    global buttonStart
    buttonStart.setText(u'Старт')
    
    global buttonStop
    buttonStop.setText(u'Стоп')
    
    global buttonLoadTag
    buttonLoadTag.setText(u'Хештеги')

    global buttonLoadBlackTag
    buttonLoadBlackTag.setText(u'Нежелательные \n хештеги')

    global buttonLoadBlackUser
    buttonLoadBlackUser.setText(u'Нежелательные \n пользователи')
    
    global buttonSaveSettings
    buttonSaveSettings.setText(u'Сохранить данные')
    
    global buttonLoadSettings
    buttonLoadSettings.setText(u'Загрузить данные')


def callback():

    global looper
    looper = True

    k=0

    loginPasswordListCheck = []
    for xm in (unicode(tagUsers.toPlainText().toUtf8(), encoding="UTF-8").split('\n')):
        loginPasswordListCheck.append(xm)
    
    for loginPasswordCheck in loginPasswordListCheck:
        loginCheck=((loginPasswordListCheck[k]).split(':')[0]).encode("utf-8")
        if not re.match("^[\w-]*$", loginCheck):
            QtGui.QMessageBox.warning(None, "Warning!", 'Use allowed symbols for User\'s login' if normLang else u'Используйте разрешенные символы для логина!')
            stop()
            logOutput.clear()
            return
        k+=1

    if not checkBoxLike.isChecked() and not checkBoxComment.isChecked() and not checkBoxFollow.isChecked() and not checkBoxUnfollow.isChecked():
        QtGui.QMessageBox.warning(None, "Warning!", 'Choose at least one action!' if normLang else u'Выберите хотя бы одно действие!')
    if not checkBoxFollow.isChecked() and checkBoxUnfollow.isChecked():
        QtGui.QMessageBox.warning(None, "Warning!", 'In order to use Unfollow select Follow!' if normLang else u'Отписка используется только вместе с Подпиской!')
    elif tagOutput.toPlainText().trimmed().isEmpty() or tagUsers.toPlainText().trimmed().isEmpty():
        QtGui.QMessageBox.warning(None, "Warning!", 'Tags and Users are mandatory! Load them first!' if normLang else u'Хештеги и пользователи - обязательные параметры, укажите их!')
    elif preparedRadioButton.isChecked() and preparedComment.toPlainText().trimmed().isEmpty():
        QtGui.QMessageBox.warning(None, "Warning!", 'In order to use prepared comments load them first!' if normLang else u'Чтобы использовать готовые комментарии, укажите их!')
    elif constructRadioButton.isChecked() and (firstPartComment.toPlainText().trimmed().isEmpty() or secondPartComment.toPlainText().trimmed().isEmpty() or thirdPartComment.toPlainText().trimmed().isEmpty() or fourthPartComment.toPlainText().trimmed().isEmpty()):
        QtGui.QMessageBox.warning(None, "Warning!", 'In order to use constructor for comments its parts can not be empty!' if normLang else u'Чтобы использовать конструктор комментариев, заполните все его части!')
    elif not re.match("[^!@#$%^&*()+`~\"\'?\/,\.|;:{[\]}]*$", (unicode(tagOutput.toPlainText().toUtf8(), encoding="UTF-8"))):
        QtGui.QMessageBox.warning(None,  "Warning!", 'Please use allowed symbols for tags!' if normLang else u'Пожалуйста, используйте разрешенные символы для хештегов!')
    elif not re.match("[^!@#$%^&*()+`~\"\'?\/,\.|;:{[\]}]*$", (unicode(blackTagOutput.toPlainText().toUtf8(), encoding="UTF-8"))):
        QtGui.QMessageBox.warning(None, "Warning!", 'Please use allowed symbols for black tags!' if normLang else u'Пожалуйста, используйте разрешенные символы для нежелательных хештегов!')
    elif not re.match("[^!@#$%^&*()+`~\"\'?\/,\.|;:{[\]}]*$", (unicode(blackUserOutput.toPlainText().toUtf8(), encoding="UTF-8"))):
        QtGui.QMessageBox.warning(None, "Warning!", 'Please use allowed symbols for black users!'if normLang else u'Пожалуйста, используйте разрешенные символы для нежелательных пользователей!')
    else:
        buttonStop.setDisabled(False)
        buttonStart.setDisabled(True)
        buttonLoadBlackUser.setDisabled(True)
        buttonLoadBlackTag.setDisabled(True)
        buttonLoadTag.setDisabled(True)
        buttonLoadUser.setDisabled(True)
        
        blackTagOutput.setDisabled(True)
        tagOutput.setDisabled(True)
        blackUserOutput.setDisabled(True)
        tagUsers.setDisabled(True)
    
        textboxLikesPerDay.setDisabled(True)
        textboxCommentsPerDay.setDisabled(True)
        textboxMaxLikesFromOneTag.setDisabled(True)
        textboxFollowsPerDay.setDisabled(True)
        textboxUnfollowsPerDay.setDisabled(True)
        
        checkBoxLike.setDisabled(True)
        checkBoxFollow.setDisabled(True)
        checkBoxComment.setDisabled(True)
        checkBoxUnfollow.setDisabled(True)
        
        constructRadioButton.setDisabled(True)
        preparedRadioButton.setDisabled(True)
        firstPartComment.setDisabled(True)
        secondPartComment.setDisabled(True)
        thirdPartComment.setDisabled(True)
        fourthPartComment.setDisabled(True)
        preparedComment.setDisabled(True)
        buttonLoadComment.setDisabled(True)
        
        buttonRus.setDisabled(True)
        buttonEng.setDisabled(True)
        
        buttonClearStatistic.setDisabled(True)
        buttonClearLog.setDisabled(True)
        
        buttonSaveSettings.setDisabled(True)
        buttonLoadSettings.setDisabled(True)

        loginPasswordList = (unicode(tagUsers.toPlainText().toUtf8(), encoding="UTF-8").split('\n'))
        
        i=0
        
        stringBlackUser = {}
        for json_black_user in (unicode(blackUserOutput.toPlainText().toUtf8(), encoding="UTF-8").split('\n')):
            stringBlackUser[json_black_user] = ''
            
        stringUser = []
        for x in (unicode(tagOutput.toPlainText().toUtf8(), encoding="UTF-8").split('\n')):
            stringUser.append(x)
            
        stringBlackTag = []
        for xt in (unicode(blackTagOutput.toPlainText().toUtf8(), encoding="UTF-8").split('\n')):
            stringBlackTag.append(xt)
            
        global stringPreparedComment
        stringPreparedComment = []
        for com in (unicode(preparedComment.toPlainText().toUtf8(), encoding="UTF-8").split('\n')):
            stringPreparedComment.append(com)
        
        for loginPassword in loginPasswordList:
            
            """For concurrency correct work"""
            sleep(1)

            bot = InstaBot(login=((loginPasswordList[i]).split(':')[0]).encode("utf-8"), password=((loginPasswordList[i]).split(':')[1]).encode("utf-8"),
                           like_per_day=int(textboxLikesPerDay.text()) if checkBoxLike.isChecked() else 0,
                           comments_per_day=int(textboxCommentsPerDay.text()) if checkBoxComment.isChecked() else 0,
                           tag_list=stringUser,
                           tag_blacklist=stringBlackTag if stringBlackTag != [u''] else [],
                           user_blacklist=stringBlackUser if stringBlackUser != {'':''} else {},
                           max_like_for_one_tag=int(textboxMaxLikesFromOneTag.text()),
                           follow_per_day=int(textboxFollowsPerDay.text()) if checkBoxFollow.isChecked() else 0,
                           follow_time=5*60*60,
                           unfollow_per_day=int(textboxUnfollowsPerDay.text()) if checkBoxUnfollow.isChecked() else 0,
                           unfollow_break_min=15,
                           unfollow_break_max=30,
                           log_mod=1)

#             time.sleep(10)
            thread.start_new_thread(bot.new_auto_mod, ())
            i+=1
#         thread.start_new_thread(bot.new_auto_mod, ())


def clearLog():
    logOutput.clear()


def clearStatistic():
    labelComments.setText('0')
    labelLikes.setText('0')
    labelFollows.setText('0')
    labelUnfollows.setText('0')


def stop():
    
    global looper
    looper = False
    
    buttonStop.setDisabled(True)
    buttonStart.setDisabled(False)
    buttonLoadBlackUser.setDisabled(False)
    buttonLoadBlackTag.setDisabled(False)
    buttonLoadTag.setDisabled(False)
    buttonLoadUser.setDisabled(False)
    
    blackTagOutput.setDisabled(False)
    tagOutput.setDisabled(False)
    blackUserOutput.setDisabled(False)
    tagUsers.setDisabled(False)
    
    textboxLikesPerDay.setDisabled(False)
    textboxCommentsPerDay.setDisabled(False)
    textboxMaxLikesFromOneTag.setDisabled(False)
    textboxFollowsPerDay.setDisabled(False)
    textboxUnfollowsPerDay.setDisabled(False)
    
    checkBoxLike.setDisabled(False)
    checkBoxFollow.setDisabled(False)
    checkBoxComment.setDisabled(False)
    checkBoxUnfollow.setDisabled(False)
    
    constructRadioButton.setDisabled(False)
    preparedRadioButton.setDisabled(False)
    firstPartComment.setDisabled(False)
    secondPartComment.setDisabled(False)
    thirdPartComment.setDisabled(False)
    fourthPartComment.setDisabled(False)
    preparedComment.setDisabled(False)
    buttonLoadComment.setDisabled(False)
    
    buttonRus.setDisabled(False)
    buttonEng.setDisabled(False)
    
    buttonClearStatistic.setDisabled(False)
    buttonClearLog.setDisabled(False)

    buttonSaveSettings.setDisabled(False)
    buttonLoadSettings.setDisabled(False)
    
    logOutput.append("<span style=\" font-size:8pt; font-weight:600; color:#ff0000;\" >Bot has been stopped by the User</span>")
    QtGui.QApplication.processEvents()


class InstaBot:

    url = 'https://www.instagram.com/'
    url_tag = 'https://www.instagram.com/explore/tags/'
    url_likes = 'https://www.instagram.com/web/likes/%s/like/'
    url_unlike = 'https://www.instagram.com/web/likes/%s/unlike/'
    url_comment = 'https://www.instagram.com/web/comments/%s/add/'
    url_follow = 'https://www.instagram.com/web/friendships/%s/follow/'
    url_unfollow = 'https://www.instagram.com/web/friendships/%s/unfollow/'
    url_login = 'https://www.instagram.com/accounts/login/ajax/'
    url_logout = 'https://www.instagram.com/accounts/logout/'
    url_media_detail = 'https://www.instagram.com/p/%s/?__a=1'
    url_user_detail = 'https://www.instagram.com/%s/?__a=1'

    user_agent = ("Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36")
    accept_language = 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4'

    # If instagram ban you - query return 400 error.
    error_400 = 0
    # If you have 3 400 error in row - looks like you banned.
    error_400_to_ban = 3
    # If InstaBot think you are banned - going to sleep.
    ban_sleep_time = 2 * 60 * 60

    # All counter.
    like_counter = 0
    follow_counter = 0
    unfollow_counter = 0
    comments_counter = 0

    # List of user_id, that bot follow
    bot_follow_list = []

    # Log setting.
    log_file_path = ''
    log_file = 0

    # Other.
    user_id = 0
    media_by_tag = 0
    login_status = False

    # For new_auto_mod
    next_iteration = {"Like": 0, "Follow": 0, "Unfollow": 0, "Comments": 0}

    def __init__(self, login, password,
                 like_per_day=1000,
                 media_max_like=0,
                 media_min_like=0,
                 follow_per_day=0,
                 follow_time=5 * 60 * 60,
                 unfollow_per_day=0,
                 comments_per_day=0,
                 tag_list=['cat', 'car', 'dog'],
                 max_like_for_one_tag=5,
                 unfollow_break_min=15,
                 unfollow_break_max=30,
                 log_mod=0,
                 proxy="",
                 user_blacklist={},
                 tag_blacklist=[]):

        self.bot_start = datetime.datetime.now()
        self.unfollow_break_min = unfollow_break_min
        self.unfollow_break_max = unfollow_break_max
        self.user_blacklist = user_blacklist
        self.tag_blacklist = tag_blacklist

        self.time_in_day = 24 * 60 * 60
        # Like
        self.like_per_day = like_per_day
        if self.like_per_day != 0:
            self.like_delay = self.time_in_day / self.like_per_day

        # Follow
        self.follow_time = follow_time
        self.follow_per_day = follow_per_day
        if self.follow_per_day != 0:
            self.follow_delay = self.time_in_day / self.follow_per_day

        # Unfollow
        self.unfollow_per_day = unfollow_per_day
        if self.unfollow_per_day != 0:
            self.unfollow_delay = self.time_in_day / self.unfollow_per_day

        # Comment
        self.comments_per_day = comments_per_day
        if self.comments_per_day != 0:
            self.comments_delay = self.time_in_day / self.comments_per_day

        # Don't like if media have more than n likes.
        self.media_max_like = media_max_like
        # Don't like if media have less than n likes.
        self.media_min_like = media_min_like
        # Auto mod seting:
        # Default list of tag.
        self.tag_list = tag_list
        # Get random tag, from tag_list, and like (1 to n) times.
        self.max_like_for_one_tag = max_like_for_one_tag
        # log_mod 0 to console, 1 to file
        self.log_mod = log_mod
        self.s = requests.Session()
        # if you need proxy make something like this:
        # self.s.proxies = {"https" : "http://proxyip:proxyport"}
        # by @ageorgios
        if proxy!="":
            proxies = {
              'http': 'http://'+proxy,
              'https': 'http://'+proxy,
            }
            self.s.proxies.update(proxies)
        # convert login to lower
        self.user_login = login.lower()
        self.user_password = password

        self.media_by_tag = []

        now_time = datetime.datetime.now()
        log_string = '%s:\n' % \
                     (now_time.strftime("%d.%m.%Y %H:%M"))
        self.write_log(('styopik87bot v0.8 started at ' if normLang else u'styopik87bot v0.8 стартовал ') + log_string)
        self.login()
        self.populate_user_blacklist()
        signal.signal(signal.SIGTERM, self.cleanup)
        atexit.register(self.cleanup)

    def populate_user_blacklist(self):
        for user in self.user_blacklist:

            user_id_url= self.url_user_detail % (user)
            info = self.s.get(user_id_url)
            all_data = json.loads(info.text)
            id_user = all_data['user']['media']['nodes'][0]['owner']['id']
            #Update the user_name with the user_id
            self.user_blacklist[user]=id_user
#             self.user_blacklist[i]=id_user
#             i+=1
            log_string = "%s" % (id_user)
            self.write_log(("Blacklisted user " if normLang else u'Нежелательный пользователь ') + user + (" added with ID:" if normLang else u' добавлен с ID: ') + log_string)
            time.sleep(5 * random.random())

        log_string = "Completed populating user blacklist with IDs" if normLang else u'Список нежелательных пользователей заполнен'
        self.write_log(log_string)

    def login(self):
        log_string = '%s...\n' % (self.user_login)
        self.write_log(('Trying to login as ' if normLang else u'Попытка залогиниться как ') + log_string)
        self.s.cookies.update({'sessionid': '', 'mid': '', 'ig_pr': '1',
                               'ig_vw': '1920', 'csrftoken': '',
                               's_network': '', 'ds_user_id': ''})
        self.login_post = {'username': self.user_login,
                           'password': self.user_password}
        self.s.headers.update({'Accept-Encoding': 'gzip, deflate',
                               'Accept-Language': self.accept_language,
                               'Connection': 'keep-alive',
                               'Content-Length': '0',
                               'Host': 'www.instagram.com',
                               'Origin': 'https://www.instagram.com',
                               'Referer': 'https://www.instagram.com/',
                               'User-Agent': self.user_agent,
                               'X-Instagram-AJAX': '1',
                               'X-Requested-With': 'XMLHttpRequest'})
        r = self.s.get(self.url)
        self.s.headers.update({'X-CSRFToken': r.cookies['csrftoken']})
        # time.sleep(5 * random.random())
        login = self.s.post(self.url_login, data=self.login_post,
                            allow_redirects=True)
        self.s.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        self.csrftoken = login.cookies['csrftoken']
        # time.sleep(5 * random.random())

        if login.status_code == 200:
            r = self.s.get('https://www.instagram.com/')
            finder = r.text.find(self.user_login)
            if finder != -1:
                ui = UserInfo()
                self.user_id = ui.get_user_id_by_login(self.user_login)
                self.login_status = True
                log_string = '%s' % (self.user_login)
                self.write_log(log_string + (' login success!' if normLang else u' подключение успешно!'))
            else:
                self.login_status = False
                self.write_log('Login error! Check your login data!' if normLang else u'Ошибка подключения! проверьте логин и пароль!')
        else:
            self.write_log('Login error! Connection error!' if normLang else u'Ошибка подключения! Ошибка соединения!')

    def logout(self):
#         now_time = datetime.datetime.now()
#         log_string = '%i%i%i%i.' % \
#                      (, ,
#                       , )
        self.write_log(('Logout: likes - ' if normLang else u'Разлогинивиние: лайков -') + str(self.like_counter) +
                       (', follow - ' if normLang else u', подписок - ') + str(self.follow_counter) +
                       (', unfollow - ' if normLang else u', отписок - ') + str(self.unfollow_counter) +
                       (', comments - ' if normLang else u', комментариев - ') + str(self.comments_counter))
        work_time = datetime.datetime.now() - self.bot_start
        log_string = '%s' % (work_time)
        self.write_log(('Bot work time: ' if normLang else u'Бот работал: ') + log_string)

        try:
#             logout_post = {'csrfmiddlewaretoken': self.csrftoken}
#             logout = self.s.post(self.url_logout, data=logout_post)
            self.write_log("Logout success!" if normLang else u'Отключение успешно!')
            self.login_status = False
        except:
            self.write_log("Logout error!" if normLang else u'Ошибка отключения!')

    def cleanup(self, *_):
        # Unfollow all bot follow
#         if self.follow_counter >= self.unfollow_counter:
#             for f in self.bot_follow_list:
#                 log_string = "%s" % (f[0])
#                 self.write_log(('Trying to unfollow: ' if normLang else u'Попытка отписаться: ') + log_string)
#                 self.unfollow_on_cleanup(f[0])
#                 sleeptime = random.randint(self.unfollow_break_min, self.unfollow_break_max)
# #                 log_string = "%i%i %i" % (
# #                 sleeptime, self.unfollow_counter, self.follow_counter)
# #                 self.write_log(log_string)
#                 self.write_log(('Pausing for ' if normLang else u'Пауза на ') + str(sleeptime) +
#                                (' seconds... ' if normLang else u' секунд...') + str(self.unfollow_counter) +
#                                (' of' if normLang else u' из') + str(self.follow_counter))
#                  
#                 time.sleep(sleeptime)
#                 self.bot_follow_list.remove(f)
# 
        # Logout
        if (self.login_status):
            self.logout()
        exit(0)

    def get_media_id_by_tag(self, tag):
        """ Get media ID set, by your hashtag """
        if (self.login_status):
            log_string = "%s" % (tag)
            self.write_log(('Get media id by tag: ' if normLang else u'Получение ID медиа по хештегу: ') + log_string)
            if self.login_status == 1:
                url_tag = '%s%s%s' % (self.url_tag, tag, '/')

                try:    
                    r = self.s.get(url_tag)
                    text = r.text

                    finder_text_start = ('<script type="text/javascript">'
                                         'window._sharedData = ')
                    finder_text_start_len = len(finder_text_start) - 1
                    finder_text_end = ';</script>'

                    all_data_start = text.find(finder_text_start)
                    all_data_end = text.find(finder_text_end, all_data_start + 1)
                    json_str = text[(all_data_start + finder_text_start_len + 1) \
                        : all_data_end]
      
                    all_data = json.loads(json_str)
                    
                    self.media_by_tag = list(all_data['entry_data']['TagPage'][0] \
                                                 ['tag']['media']['nodes'])
                    
                except:
                    self.media_by_tag = []
                    self.write_log("Except on get_media!" if normLang else u'Ошибка при получении медиа!')
            else:
                return 0

    def like_all_exist_media(self, media_size=-1, delay=True):
        """ Like all media ID that have self.media_by_tag """
        if (self.login_status):
            if self.media_by_tag != 0:
                i = 0
                for d in self.media_by_tag:
                    # Media count by this tag.
                    if media_size > 0 or media_size < 0:
                        media_size -= 1
                        l_c = self.media_by_tag[i]['likes']['count']

                        if ((l_c <= self.media_max_like and l_c >= self.media_min_like)
                            or (self.media_max_like == 0 and l_c >= self.media_min_like)
                            or (self.media_min_like == 0 and l_c <= self.media_max_like)
                            or (self.media_min_like == 0 and self.media_max_like == 0)):
                            for blacklisted_user_name, blacklisted_user_id in self.user_blacklist.items():
                                if (self.media_by_tag[i]['owner']['id'] == blacklisted_user_id):
                                    self.write_log(("Not liking media owned by blacklisted user: " if normLang else u'Не лайкаю медиа нежелательного пользователя: ') + blacklisted_user_name)
                                    return False
                            if (self.media_by_tag[i]['owner']['id'] == self.user_id):
                                self.write_log("Keep calm - It's your own media ;)" if normLang else u'Все нормально - это Ваше медиа ;)')
                                return False

                            try:   
                                caption = self.media_by_tag[i]['caption'].encode('ascii',errors='ignore')
                                tag_blacklist = set(self.tag_blacklist)
                                tags = {str.lower(tag.strip("#")) for tag in caption.split() if tag.startswith("#")}
  
                                for blackTag in tags:
                                    for blacklist in tag_blacklist:
                                        if blackTag.find(blacklist) != -1:
                                            self.write_log(("Not liking media with blacklisted tag(s): " if normLang else u'Не лайкаю медиа  нежелательным хештегом: ') + blacklist)
                                            return False

                            except:
                                self.write_log("Couldn't find caption - not liking" if normLang else u'Не могу найти заголовок - не лайкаю')
                                return False

                            log_string = "%s" % \
                                         (self.media_by_tag[i]['id'])
                            self.write_log(('Trying to like media: ' if normLang else u'Попытка лайкнуть медиа: ') + log_string)
                            like = self.like(self.media_by_tag[i]['id'])
                            if like != 0:
                                if like.status_code == 200:
                                    # Like, all ok!
                                    self.error_400 = 0
                                    self.like_counter += 1
                                    labelLikes.setText(str(int(labelLikes.text()) + 1))
                                    QtGui.QApplication.processEvents()
             
                                    self.write_log(('Liked: ' if normLang else u'Лайкнуто: ') + str("www.instagram.com/p/" + self.media_by_tag[i]['code']) +
                                                   ('. Like #' if normLang else u'. Лайк #') + str(self.like_counter))
                                    
                                    self.write_log(log_string)
                                elif like.status_code == 400:
                                    log_string = "%i" \
                                                 % (like.status_code)
                                    self.write_log(('Not liked: ' if normLang else u'Не пролайкано: ') + log_string)
                                    # Some error. If repeated - can be ban!
                                    if self.error_400 >= self.error_400_to_ban:
                                        # Look like you banned!
                                        time.sleep(self.ban_sleep_time)
                                    else:
                                        self.error_400 += 1
                                else:
                                    log_string = "%i" \
                                                 % (like.status_code)
                                    self.write_log(('Not liked: ' if normLang else u'Не пролайкано: ') + log_string)
                                    return False
                                    # Some error.
                                i += 1
                                
                                if delay:
                                    time.sleep(self.like_delay * 0.9 +
                                               self.like_delay * 0.2 * random.random())
                                else:
                                    return True
                            else:
                                return False
                        else:
                            return False
                    else:
                        return False
            else:
                self.write_log("No media to like!" if normLang else u'ет медия, чтобы лайкнуть')

    def like(self, media_id):
        """ Send http request to like media by ID """
        if (self.login_status and looper):

            url_likes = self.url_likes % (media_id)
            try:
                like = self.s.post(url_likes)
#                 last_liked_media_id = media_id
            except:
                self.write_log("Except on like!" if normLang else u'Ошибка при лайканьи!')
                like = 0
            return like

    def unlike(self, media_id):
        """ Send http request to unlike media by ID """
        if (self.login_status and looper):
            url_unlike = self.url_unlike % (media_id)
            try:
                unlike = self.s.post(url_unlike)
            except:
                self.write_log("Except on unlike!" if normLang else u'Ошибка при анлайканьи!')
                unlike = 0
            return unlike

    def comment(self, media_id, comment_text):
        """ Send http request to comment """
        if (self.login_status and looper):
            comment_post = {'comment_text': comment_text}
            url_comment = self.url_comment % (media_id)
            try:
                comment = self.s.post(url_comment, data=comment_post)
                if comment.status_code == 200:
                    self.comments_counter += 1
#                     labelComments.setText(str(self.comments_counter))
                    labelComments.setText(str(int(labelComments.text()) + 1))
                    QtGui.QApplication.processEvents()
                    
                    log_string = '"%s". #%i.' % (comment_text, self.comments_counter)
                    self.write_log(('Write: ' if normLang else u'Пишу: ') + log_string)
                return comment
            except:
                self.write_log("Except on comment!" if normLang else u'Ошибка при комментировании!')
        return False

    def follow(self, user_id):
        """ Send http request to follow """
        if (self.login_status and looper):
            url_follow = self.url_follow % (user_id)
            try:
                follow = self.s.post(url_follow)
                if follow.status_code == 200:
                    self.follow_counter += 1
#                     labelFollows.setText(str(self.follow_counter))
                    labelFollows.setText(str(int(labelFollows.text()) + 1))
                    QtGui.QApplication.processEvents()
                    
                    log_string = "%s #%i." % (user_id, self.follow_counter)
                    self.write_log(('Followed: ' if normLang else u'Подписан: ') + log_string)
                return follow
            except:
                self.write_log("Except on follow!" if normLang else u'Ошибка при подписке! ')
        return False

    def unfollow(self, user_id):
        """ Send http request to unfollow """
        if (self.login_status and looper):
            url_unfollow = self.url_unfollow % (user_id)
            try:
                unfollow = self.s.post(url_unfollow)
                if unfollow.status_code == 200:
                    self.unfollow_counter += 1
                    
                    labelUnfollows.setText(str(int(labelUnfollows.text()) + 1))
                    QtGui.QApplication.processEvents()
                    
                    log_string = "%s #%i." % (user_id, self.unfollow_counter)
                    self.write_log(('Unfollow: ' if normLang else u'Отписка: ') + log_string)
                return unfollow
            except:
                self.write_log("Exept on unfollow!" if normLang else u'Ошибка при отписке! ')
        return False

    def unfollow_on_cleanup(self, user_id):
        """ Unfollow on cleanup by @rjmayott """
        if (self.login_status):
            url_unfollow = self.url_unfollow % (user_id)
            try:
                unfollow = self.s.post(url_unfollow)
                if unfollow.status_code == 200:
                    self.unfollow_counter += 1
                    log_string = "%s #%i of %i." % (user_id, self.unfollow_counter, self.follow_counter)
                    self.write_log(('Unfollow: ' if normLang else u'Отписка: ') + log_string)
                else:
                    log_string = "Slow Down - Pausing for 5 minutes so we don't get banned!" if normLang else u'Спокойствие - пауза на 5 минут, чтобы не быть забаненным!'
                    self.write_log(log_string)
                    time.sleep(300)
                    unfollow = self.s.post(url_unfollow)
                    if unfollow.status_code == 200:
                        self.unfollow_counter += 1
                        log_string = "%s #%i of %i." % (user_id, self.unfollow_counter, self.follow_counter)
                        self.write_log(('Unfollow: ' if normLang else u'Отписка: ') + log_string)
                    else:
                        log_string = "Still no good :( Skipping and pausing for another 5 minutes" if normLang else u'Все еще ничего хорошего:( Ждем еще 5 минут'
                        self.write_log(log_string)
                        time.sleep(300)
                    return False
                return unfollow
            except:
                log_string = "Except on unfollow... Looks like a network error" if normLang else u'Ошибка при отписке... похоже на сетевую ошибку'
                self.write_log(log_string)
        return False

    def auto_mod(self):
        """ Star loop, that get media ID by your tag list, and like it """
        if (self.login_status):
            while True:
                random.shuffle(self.tag_list)
                self.get_media_id_by_tag(random.choice(self.tag_list))
                self.like_all_exist_media(random.randint \
                                              (1, self.max_like_for_one_tag))

    def new_auto_mod(self):

        while looper:
            # ------------------- Get media_id -------------------
            if len(self.media_by_tag) == 0:
                self.get_media_id_by_tag(random.choice(self.tag_list))
                self.this_tag_like_count = 0
                self.max_tag_like_count = random.randint(1, self.max_like_for_one_tag)
            # ------------------- Like -------------------
            self.new_auto_mod_like()
            
            # ------------------- Follow -------------------
            self.new_auto_mod_follow()
            
            # ------------------- Unfollow -------------------
            self.new_auto_mod_unfollow()
            
            # ------------------- Comment -------------------
            self.new_auto_mod_comments()

            # Bot iteration in 1 sec
            time.sleep(1)
            # print("Tic!")

    def new_auto_mod_like(self):
        if time.time() > self.next_iteration["Like"] and self.like_per_day != 0 \
                and len(self.media_by_tag) > 0:
            # You have media_id to like:
            if self.like_all_exist_media(media_size=1, delay=False):
                # If like go to sleep:
                self.next_iteration["Like"] = time.time() + \
                                              self.add_time(self.like_delay)
                # Count this tag likes:
                self.this_tag_like_count += 1
                if self.this_tag_like_count >= self.max_tag_like_count:
                    self.media_by_tag = [0]
            # Del first media_id
            del self.media_by_tag[0]

    def new_auto_mod_follow(self):
        if time.time() > self.next_iteration["Follow"] and \
                        self.follow_per_day != 0 and len(self.media_by_tag) > 0:
            if self.media_by_tag[0]["owner"]["id"] == self.user_id:
                self.write_log("Keep calm - It's your own profile ;)" if normLang else u'Все нормально - это Ваш профиль ;)')
                return

            if self.media_by_tag != 0:
                i = 0
                for d in self.media_by_tag:
                    try:
                        
                        caption = self.media_by_tag[i]['caption'].encode('ascii',errors='ignore')
                        tag_blacklist = set(self.tag_blacklist)
                        tags = {str.lower(tag.strip("#")) for tag in caption.split() if tag.startswith("#")}
  
                        for blackTag in tags:
                            for blacklist in tag_blacklist:
                                if blackTag.find(blacklist) != -1:
                                    self.write_log(("Not following by media with blacklisted tag: " if normLang else u'Не подписываюсь - медиа с нежелательным хештегом: ') + blacklist)
                                    return
                    except:
                        self.write_log("Couldn't find caption - not following" if normLang else u'Не могу найти заголовок - не подписываюсь')
                        return
                    i+=1

            log_string = "%s" % (self.media_by_tag[0]["owner"]["id"])
            self.write_log(('Trying to follow: ' if normLang else u'Попытка подписаться: ') + log_string)

            if self.follow(self.media_by_tag[0]["owner"]["id"]) != False:
                self.bot_follow_list.append([self.media_by_tag[0]["owner"]["id"],
                                             time.time()])
                self.next_iteration["Follow"] = time.time() + \
                                                self.add_time(self.follow_delay)
                                                
            del self.media_by_tag[0]

    def new_auto_mod_unfollow(self):
        if time.time() > self.next_iteration["Unfollow"] and \
                        self.unfollow_per_day != 0 and len(self.bot_follow_list) > 0:
            for f in self.bot_follow_list:
                if time.time() > (f[1] + self.follow_time):

#                     log_string = "%i: %s" % (self.unfollow_counter, f[0])
#                     self.write_log(('Trying to unfollow #' if normLang else u'Попытка отписаться #') + log_string)
                    log_string = "%s" % (f[0])
                    self.write_log(('Trying to unfollow: ' if normLang else u'Попытка отписаться ') + log_string)

                    if self.unfollow(f[0]) != False:
                        self.bot_follow_list.remove(f)
                        self.next_iteration["Unfollow"] = time.time() + \
                                                          self.add_time(self.unfollow_delay)

    def new_auto_mod_comments(self):
        if time.time() > self.next_iteration["Comments"] and self.comments_per_day != 0 \
                and len(self.media_by_tag) > 0 \
                and self.check_exisiting_comment(self.media_by_tag[0]['code']) == False:
            comment_text = self.generate_comment() if constructRadioButton.isChecked() else random.choice(stringPreparedComment)
            log_string = "%s" % (self.media_by_tag[0]['code'])
            self.write_log(('Trying to comment: ' if normLang else u'Попытка комментировать: ') + "www.instagram.com/p/" + log_string)

            if self.media_by_tag != 0:
                i = 0
                for d in self.media_by_tag:
                    try:
                        
                        caption = self.media_by_tag[i]['caption'].encode('ascii',errors='ignore')
                        tag_blacklist = set(self.tag_blacklist)
                        tags = {str.lower(tag.strip("#")) for tag in caption.split() if tag.startswith("#")}
  
                        for blackTag in tags:
                            for blacklist in tag_blacklist:
                                if blackTag.find(blacklist) != -1:
#                                             matching_tags = ', '.join(tags.intersection(tag_blacklist))
                                    self.write_log(("Not commenting media with blacklisted tag: " if normLang else u'Не комментирую - медиа с нежелательным хештегом: ') + blacklist)
                                    return
                    except:
                        self.write_log("Couldn't find caption - not commenting" if normLang else u'Не могу найти заголовок - не комментирую')
                        return
                    i+=1

            if self.comment(self.media_by_tag[0]['id'], comment_text) != False:
                self.next_iteration["Comments"] = time.time() + \
                                                  self.add_time(self.comments_delay)

    def add_time(self, time):
        """ Make some random for next iteration"""
        return time * 0.9 + time * 0.2 * random.random()

    def generate_comment(self):
        
        string1Comment = []
        for c1 in (unicode(firstPartComment.toPlainText().toUtf8(), encoding="UTF-8").split('\n')):
            string1Comment.append(c1)
            
        string2Comment = []
        for c2 in (unicode(secondPartComment.toPlainText().toUtf8(), encoding="UTF-8").split('\n')):
            string2Comment.append(c2)
            
        string3Comment = []
        for c3 in (unicode(thirdPartComment.toPlainText().toUtf8(), encoding="UTF-8").split('\n')):
            string3Comment.append(c3)

        string4Comment = []
        for c4 in (unicode(fourthPartComment.toPlainText().toUtf8(), encoding="UTF-8").split('\n')):
            string4Comment.append(c4)
        
        c_list = list(itertools.product(
            string1Comment,
            string2Comment,
            string3Comment,
            string4Comment,
            [".", "..", "...", "!", "!!", "!!!"]))

        repl = [("  ", " "), (" .", "."), (" !", "!")]
        res = " ".join(random.choice(c_list))
        for s, r in repl:
            res = res.replace(s, r)
        return res.capitalize()

    def check_exisiting_comment(self, media_code):
        url_check = self.url_media_detail % (media_code)
        check_comment = self.s.get(url_check)
        all_data = json.loads(check_comment.text)
        if all_data['media']['owner']['id'] == self.user_id:
                self.write_log("Keep calm - It's your own media ;)" if normLang else u'Все нормально - это Ваше медиа ;)')
                # Del media to don't loop on it
                del self.media_by_tag[0]
                return True
        comment_list = list(all_data['media']['comments']['nodes'])
        for d in comment_list:
            if d['user']['id'] == self.user_id:
                self.write_log("Keep calm - Media already commented ;)" if normLang else u'Все нормально - это медиа уже прокомментировано ;)')
                # Del media to don't loop on it
                del self.media_by_tag[0]
                return True
        return False

    def write_log(self, log_text):
        """ Write log by print() or logger """
        if self.log_mod == 0:
            try:
                print("[" + datetime.datetime.now().strftime("%H:%M:%S"), "] ", log_text)                
                logOutput.append("[" + datetime.datetime.now().strftime("%H:%M:%S") + "] " + log_text)
                QtGui.QApplication.processEvents()

            except UnicodeEncodeError:
                print("Your text has unicode problem!" if normLang else u'У Вашего текста проблемы с кодировкой!')
        elif self.log_mod == 1:
            # Create log_file if not exist.
            if self.log_file == 0:
                self.log_file = 1
                now_time = datetime.datetime.now()
                self.log_full_path = '%s%s_%s.log' % (self.log_file_path,
                                                      self.user_login,
                                                      now_time.strftime("%d%m%Y"))
                formatter = logging.Formatter('%(asctime)s - %(name)s '
                                              '- %(message)s')
                self.logger = logging.getLogger(self.user_login)
                self.hdrl = logging.FileHandler(self.log_full_path, mode='w')
                self.hdrl.setFormatter(formatter)
                self.logger.setLevel(level=logging.INFO)
                self.logger.addHandler(self.hdrl)
            # Log to log file.
            try:
                self.logger.info(log_text)
                
                logOutput.append("[" + datetime.datetime.now().strftime("%H:%M:%S") + "] " + log_text)
                QtGui.QApplication.processEvents()
                
            except UnicodeEncodeError:
                print("Your text has unicode problem!" if normLang else u'У Вашего текста проблемы с кодировкой!')


class myLineEdit(QtGui.QLineEdit):
    @pyqtSlot(QtCore.QString)
    def textChanged(self, string):
        if textboxLikesPerDay.text().size() > 0:
            a = float(textboxLikesPerDay.text())/1440
            b = "%.2f" % a
            labelLikesPerMin.setText('(' + b + '/min)')
        else:
            labelLikesPerMin.setText('(' + str(0) + '/min)')


# class Absolute(QtGui.QWidget):
class Absolute(QTabWidget):
    def __init__(self, parent=None):
        super(Absolute, self).__init__(parent)
        QtGui.QWidget.__init__(self, parent)
        
        self.setWindowTitle('styopik87bot')
        
        global normLang
        normLang = True

        global buttonSaveSettings
        buttonSaveSettings = QtGui.QPushButton('Save Data')
        buttonSaveSettings.clicked.connect(saveData)
        
        global buttonLoadSettings
        buttonLoadSettings = QtGui.QPushButton('Load Data')
        buttonLoadSettings.clicked.connect(loadData)
        
        global tab1
        tab1 = QWidget()
        global tab2
        tab2 = QWidget()
        global tab3
        tab3 = QWidget()
        global tab4
        tab4 = QWidget()
        
        global tabs
        tabs = QTabWidget()
        
        tabs.addTab(tab1, 'Main Settings')
        tabs.addTab(tab2,"Users")
        tabs.addTab(tab3,"Comments")
        tabs.addTab(tab4,"Log and Statistics")

        global buttonClearLog
        buttonClearLog = QtGui.QPushButton('Clear log')
        buttonClearLog.clicked.connect(clearLog)
        
        global buttonClearStatistic
        buttonClearStatistic = QtGui.QPushButton('Clear statistic')
        buttonClearStatistic.clicked.connect(clearStatistic)

        global labelDescribeUser
        labelDescribeUser = QtGui.QLabel('(one set login:password per row)')
        
        global labelDescribeTag
        labelDescribeTag = QtGui.QLabel('(one hashtag per row)   ')

        global labelDescribeBlackTag
        labelDescribeBlackTag = QtGui.QLabel('(one hashtag per row)   ')
        
        global labelDescribeBlackUser
        labelDescribeBlackUser = QtGui.QLabel('(one black user per row)')
        
        global labelDescribeComment
        labelDescribeComment = QtGui.QLabel('(one comment per row)')

        global constructRadioButton
        constructRadioButton = QtGui.QRadioButton('Constructed', self)
        constructRadioButton.setChecked(True)
        
        global firstPartComment
        firstPartComment = QtGui.QTextEdit(self)
        firstPartComment.append('this')
        firstPartComment.append('the')
        firstPartComment.append('your')
        
        global secondPartComment
        secondPartComment = QtGui.QTextEdit(self)
        secondPartComment.append("photo")
        secondPartComment.append("picture")
        secondPartComment.append("pic")
        secondPartComment.append("shot")
        secondPartComment.append("snapshot")
                
        global thirdPartComment
        thirdPartComment = QtGui.QTextEdit(self)
        thirdPartComment.append("is")
        thirdPartComment.append("looks")
        thirdPartComment.append("feels")
        thirdPartComment.append("is really")
        
        global fourthPartComment
        fourthPartComment = QtGui.QTextEdit(self)
        fourthPartComment.append("great")
        fourthPartComment.append("super")
        fourthPartComment.append("good")
        fourthPartComment.append("very good")
        fourthPartComment.append("good")
        fourthPartComment.append("wow")
        fourthPartComment.append("WOW")
        fourthPartComment.append("cool")
        fourthPartComment.append("GREAT")
        fourthPartComment.append("magnificent")
        fourthPartComment.append("magical")
        fourthPartComment.append("very cool")
        fourthPartComment.append("stylish")
        fourthPartComment.append("so stylish")
        fourthPartComment.append("beautiful")
        fourthPartComment.append("so beautiful")
        fourthPartComment.append("so stylish")
        fourthPartComment.append("so professional")
        fourthPartComment.append("lovely")
        fourthPartComment.append("so lovely")
        fourthPartComment.append("very lovely")
        fourthPartComment.append("glorious")
        fourthPartComment.append("so glorious")
        fourthPartComment.append("very glorious")
        fourthPartComment.append("adorable")
        fourthPartComment.append("excellent")
        fourthPartComment.append("amazing")
                
        global preparedRadioButton
        preparedRadioButton = QtGui.QRadioButton('Prepared', self)
        
        global preparedComment
        preparedComment = QtGui.QTextEdit(self)
        
        global buttonLoadComment
        buttonLoadComment = QtGui.QPushButton('Comments', self)
#         buttonLoadComment.clicked.connect(self.getcomment)

        global buttonLoadUser
        buttonLoadUser = QtGui.QPushButton('Users', self)
#         buttonLoadUser.clicked.connect(self.getuser)
        
        global tagUsers
        tagUsers = QtGui.QTextEdit(self)
        
        global groupBoxActions
        groupBoxActions = QtGui.QGroupBox('Actions', self)
        
        global groupBoxStatistic
        groupBoxStatistic = QtGui.QGroupBox('Statistics', self)
        
        global label1
        label1 = QtGui.QLabel('likes:', self)
        
        global labelLikes
        labelLikes = QtGui.QLabel('0', self)
        
        global label4
        label4 = QtGui.QLabel('unfollows:', self)
        
        global labelUnfollows
        labelUnfollows = QtGui.QLabel('0', self)
        
        global label2
        label2 = QtGui.QLabel('follows:', self)
        
        global labelFollows
        labelFollows = QtGui.QLabel('0', self)
        
        global label3
        label3 = QtGui.QLabel('comments:', self)
        
        global labelComments
        labelComments = QtGui.QLabel('0', self)      
        
        global checkBoxLike
        checkBoxLike = QtGui.QCheckBox('Like', self)
        
        global checkBoxFollow
        checkBoxFollow = QtGui.QCheckBox('Follow', self)
        
        global checkBoxComment
        checkBoxComment = QtGui.QCheckBox('Comment', self)
        
        global checkBoxUnfollow
        checkBoxUnfollow = QtGui.QCheckBox('Unfollow', self)

        global label5
        label5 = QtGui.QLabel('Likes per day', self)
        
        objValidator = QtGui.QDoubleValidator(self)
        objValidator.setRange(0, 10000000.0, 1)
        
        global textboxLikesPerDay
        textboxLikesPerDay = myLineEdit(self)
        textboxLikesPerDay.setText(str(1000))
        textboxLikesPerDay.connect(textboxLikesPerDay,SIGNAL("textChanged(QString)"),textboxLikesPerDay,SLOT("textChanged(QString)"))
        textboxLikesPerDay.setValidator(objValidator)
        textboxLikesPerDay.setAlignment(QtCore.Qt.AlignCenter)

        global labelLikesPerMin
        a = float(textboxLikesPerDay.text())/1440
        b = "%.2f" % a
        labelLikesPerMin = QtGui.QLabel('(' + b + '/min)', self)

        global label6
        label6 = QtGui.QLabel('Comments per day', self)
        
        global textboxCommentsPerDay
        textboxCommentsPerDay = QtGui.QLineEdit("1000", self)
        textboxCommentsPerDay.setValidator(objValidator)
        textboxCommentsPerDay.setAlignment(QtCore.Qt.AlignCenter)

        global label7
        label7 = QtGui.QLabel('Max likes from one tag', self)
        
        global textboxMaxLikesFromOneTag
        textboxMaxLikesFromOneTag = QtGui.QLineEdit("50", self)
        textboxMaxLikesFromOneTag.setValidator(objValidator)
        textboxMaxLikesFromOneTag.setAlignment(QtCore.Qt.AlignCenter)

        global label8
        label8 = QtGui.QLabel('Follows per day', self)
        
        global textboxFollowsPerDay
        textboxFollowsPerDay = QtGui.QLineEdit("1500", self)
        textboxFollowsPerDay.setValidator(objValidator)
        textboxFollowsPerDay.setAlignment(QtCore.Qt.AlignCenter)

        global label9
        label9 = QtGui.QLabel('Unfollows per day', self)
        
        global textboxUnfollowsPerDay
        textboxUnfollowsPerDay = QtGui.QLineEdit("1500", self)
        textboxUnfollowsPerDay.setValidator(objValidator)
        textboxUnfollowsPerDay.setAlignment(QtCore.Qt.AlignCenter)
        
        global logOutput
        logOutput = QtGui.QTextEdit(self)

        global tagOutput
        tagOutput = QtGui.QTextEdit(self)

        global blackTagOutput
        blackTagOutput = QtGui.QTextEdit(self)

        global buttonEng
        buttonEng = QtGui.QPushButton('Eng', self)
        buttonEng.setStyleSheet("QPushButton{font-size:11px; font:bold}")
        buttonEng.clicked.connect(setEng)
        
        global buttonRus
        buttonRus = QtGui.QPushButton(u'Рус', self)
        buttonRus.setStyleSheet("QPushButton{font-size:11px}")
        buttonRus.clicked.connect(setRus)

        global buttonStart
        buttonStart = QtGui.QPushButton('Start', self)
        buttonStart.setStyleSheet("QPushButton{color:green;font-size:20px;}")
        buttonStart.clicked.connect(callback)
        
        global buttonStop
        buttonStop = QtGui.QPushButton('Stop', self)
        buttonStop.setStyleSheet("QPushButton{color:red;font-size:20px;}")
        buttonStop.clicked.connect(stop)
        buttonStop.setDisabled(True)
        
        global buttonLoadTag
        buttonLoadTag = QtGui.QPushButton('Tags', self)
#         buttonLoadTag.clicked.connect(self.getfile)
        
        global buttonLoadBlackTag
        buttonLoadBlackTag = QtGui.QPushButton('BlackTags', self)
#         buttonLoadBlackTag.clicked.connect(self.getblackfile)
        
        global buttonLoadBlackUser
        buttonLoadBlackUser = QtGui.QPushButton('BlackUsers', self)
#         buttonLoadBlackUser.clicked.connect(self.getblackuserfile)
        
        global blackUserOutput
        blackUserOutput = QtGui.QTextEdit(self)
        
        self.connect(buttonLoadBlackUser, SIGNAL("clicked()"), partial(self.fill, blackUserOutput))
        self.connect(buttonLoadBlackTag, SIGNAL("clicked()"), partial(self.fill, blackTagOutput))
        self.connect(buttonLoadTag, SIGNAL("clicked()"), partial(self.fill, tagOutput))
        self.connect(buttonLoadUser, SIGNAL("clicked()"), partial(self.fill, tagUsers))
        self.connect(buttonLoadComment, SIGNAL("clicked()"), partial(self.fill, preparedComment))
#         global blackUserOutput
#         blackUserOutput = QtGui.QTextEdit(self)
        
        self.tab2UI()
        self.tab1UI()
        self.tab4UI()
        self.tab3UI()
        
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        
        hbox2 = QtGui.QHBoxLayout()
        hbox2.addWidget(buttonEng)
        hbox2.addWidget(buttonRus)
        hbox2.addWidget(QLabel('                                                        '))
        hbox2.addWidget(QLabel('                                                        '))
        hbox2.addWidget(QLabel('                                                        '))
        hbox2.addWidget(QLabel('                                                        '))
        hbox.addLayout(hbox2)
        
        hbox.addWidget(buttonStart)
        hbox.addWidget(buttonStop)
     
        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
  
        self.setLayout(vbox)
        self.setFixedSize(450, 500)
        self.addTab(tabs, '                                                                                                                                             ')


    def tab1UI(self):

        vBoxLayout112 = QVBoxLayout()
        
        hBoxLayout112 = QHBoxLayout()        
        
        hBoxLayout112.addWidget(buttonSaveSettings)
        hBoxLayout112.addWidget(buttonLoadSettings)

        vBoxLayout112.addLayout(hBoxLayout112)
        
        hBoxLayout110 = QHBoxLayout()
        
        hBoxLayout110.addWidget(groupBoxActions)

        vBoxLayout10 = QVBoxLayout()
        vBoxLayout10.addWidget(checkBoxLike)
        vBoxLayout10.addWidget(checkBoxFollow)
        vBoxLayout10.addWidget(checkBoxComment)
        vBoxLayout10.addWidget(checkBoxUnfollow)

        layout = QFormLayout()
        
        hBoxLayout114 = QHBoxLayout()
        hBoxLayout114.addWidget(textboxLikesPerDay)
        hBoxLayout114.addWidget(labelLikesPerMin)
        
        layout.addRow(label5, hBoxLayout114)
        layout.addRow(label6, textboxCommentsPerDay)
        layout.addRow(label7, textboxMaxLikesFromOneTag) 
        layout.addRow(label8, textboxFollowsPerDay) 
        layout.addRow(label9, textboxUnfollowsPerDay)    
        
        hBoxLayout110.addLayout(layout)
        
        vBoxLayout112.addLayout(hBoxLayout110)
        
        hBoxLayout16 = QHBoxLayout()
        vBoxLayout16 = QVBoxLayout()
        vBoxLayout16.addWidget(buttonLoadTag)
        vBoxLayout16.addWidget(labelDescribeTag)

        hBoxLayout16.addLayout(vBoxLayout16)

        hBoxLayout16.addWidget(tagOutput)
        vBoxLayout112.addLayout(hBoxLayout16)
        
        hBoxLayout17 = QHBoxLayout()
        
        vBoxLayout17 = QVBoxLayout()
        vBoxLayout17.addWidget(buttonLoadBlackTag)
        vBoxLayout17.addWidget(labelDescribeBlackTag)
        hBoxLayout17.addLayout(vBoxLayout17)

        hBoxLayout17.addWidget(blackTagOutput)
        vBoxLayout112.addLayout(hBoxLayout17)
        
        hBoxLayout18 = QHBoxLayout()
        
        vBoxLayout18 = QVBoxLayout()
        vBoxLayout18.addWidget(buttonLoadBlackUser)
        vBoxLayout18.addWidget(labelDescribeBlackUser)
        hBoxLayout18.addLayout(vBoxLayout18)
        
        hBoxLayout18.addWidget(blackUserOutput)

        vBoxLayout112.addLayout(hBoxLayout18)
        vBoxLayout112.addWidget(QLabel())
        vBoxLayout112.addWidget(QLabel())
        
        groupBoxActions.setLayout(vBoxLayout10)

        tab1.setLayout(vBoxLayout112)
    
    
    def tab2UI(self):

        vBoxLayout20 = QVBoxLayout()
        hBoxLayout20 = QHBoxLayout()
        
        vBoxLayout20.addWidget(buttonLoadUser)
        vBoxLayout20.addWidget(labelDescribeUser)
        
        hBoxLayout20.addLayout(vBoxLayout20)
        hBoxLayout20.addWidget(tagUsers)
        
        vBoxLayout21 = QVBoxLayout()
        vBoxLayout21.addLayout(hBoxLayout20)

        vBoxLayout21.addWidget(QLabel())
        vBoxLayout21.addWidget(QLabel())
        
        tab2.setLayout(vBoxLayout21)
        
        
    def tab3UI(self):
        
        vBoxLayout40 = QVBoxLayout()
        vBoxLayout40.addWidget(constructRadioButton)
        
        hBoxLayout41 = QHBoxLayout()
        hBoxLayout41.addWidget(firstPartComment)
        hBoxLayout41.addWidget(secondPartComment)
        hBoxLayout41.addWidget(thirdPartComment)
        hBoxLayout41.addWidget(fourthPartComment)
        
        vBoxLayout40.addLayout(hBoxLayout41)
        vBoxLayout40.addWidget(preparedRadioButton)
        
        vBoxLayout41 = QVBoxLayout()
        vBoxLayout41.addWidget(buttonLoadComment)
        vBoxLayout41.addWidget(labelDescribeComment)
        
        hBoxLayout42 = QHBoxLayout()

        hBoxLayout42.addLayout(vBoxLayout41)
        hBoxLayout42.addWidget(preparedComment)
        
        vBoxLayout40.addLayout(hBoxLayout42)
        
        vBoxLayout40.addWidget(QLabel())
        vBoxLayout40.addWidget(QLabel())
        
        tab3.setLayout(vBoxLayout40)
      
  
    def tab4UI(self):
        
        vBoxLayout40 = QVBoxLayout()
        
        hBoxLayout41 = QHBoxLayout()
        hBoxLayout41.addWidget(label1)
        hBoxLayout41.addWidget(labelLikes)
        
        vBoxLayout4 = QVBoxLayout()
        vBoxLayout4.addLayout(hBoxLayout41)
        
        hBoxLayout42 = QHBoxLayout()
        hBoxLayout42.addWidget(label2)
        hBoxLayout42.addWidget(labelFollows)

        vBoxLayout4.addLayout(hBoxLayout42)
        
        hBoxLayout43 = QHBoxLayout()
        hBoxLayout43.addWidget(label3)
        hBoxLayout43.addWidget(labelComments)
        
        hBoxLayout45 = QHBoxLayout()
        hBoxLayout45.addWidget(label4)
        hBoxLayout45.addWidget(labelUnfollows)
        
        vBoxLayout4.addLayout(hBoxLayout43)
        
        vBoxLayout4.addLayout(hBoxLayout45)
        
        groupBoxStatistic.setLayout(vBoxLayout4)
        
        hBoxLayout44 = QHBoxLayout()
        
        vBoxLayout44 = QVBoxLayout()
        vBoxLayout44.addWidget(buttonClearStatistic)
        vBoxLayout44.addWidget(buttonClearLog)
        
        hBoxLayout44.addWidget(groupBoxStatistic)
        hBoxLayout44.addLayout(vBoxLayout44)

        vBoxLayout40.addLayout(hBoxLayout44)

        vBoxLayout40.addWidget(logOutput)
        
        vBoxLayout40.addWidget(QLabel())
        vBoxLayout40.addWidget(QLabel())

        tab4.setLayout(vBoxLayout40)
  
  
    def fill(self, obj):
        fileName = QFileDialog.getOpenFileName(self, "OpenFile", "", "Text files (*.txt)")
        try:
            f = open(fileName, 'r')
            data = f.read()
            obj.setText(data)
        except:
            None


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

# if __name__ == '__main__':
app = QtGui.QApplication(sys.argv)
qb = Absolute()
qb.show()
sys.exit(app.exec_())
