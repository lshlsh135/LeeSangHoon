# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 15:28:21 2017

@author: SH-NoteBook
"""

import telegram
my_token = '413222030:AAG-Yz8eDMfJ-XNCw9UceSVZ7RXNM8EDlvE'
bot = telegram.Bot(token = my_token)   #bot을 선언합니다.

updates = bot.getUpdates()  #업데이트 내역을 받아옵니다.

for u in updates :   # 내역중 메세지를 출력합니다.
    print(u.message)
    a=u.message

chat_id = bot.getUpdates()[-1].message.chat.id #가장 최근에 온 메세지의 chat id를 가져옵니다

bot.sendMessage(chat_id = chat_id, text="저는 봇입니다.") # 개신기하게도 "저는 봇입니다"라고 메세지가 왔음 ..




import telegram

my_token = '413222030:AAG-Yz8eDMfJ-XNCw9UceSVZ7RXNM8EDlvE' #토큰을 설정해 줍니다.
bot = telegram.Bot(token = my_token) #봇을 생성합니다.
bot.sendMessage(chat_id='@lshlsh135_test', text="I'm bot 1")