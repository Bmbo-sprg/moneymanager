import datetime
import re
import traceback
import discord
from discord.ext import tasks
from os import getenv

MONEY_CH_ID = 1005320470603767848
TAKE_ID = 823804645910118400
HARU_ID = 837326439707312163
COREMO_KEYWORD = ['coremo', 'コレモ', 'これも', 'COREMO', 'Coremo']
SEISENKAN_KEYWORD = ['seisenkan', '生鮮館なかむら', '生鮮館', 'なかむら', 'せいせんかん', 'せいせん']
GRACE_KEYWORD = ['grace', 'グレースたなか', 'グレース', 'ぐれーす', 'たなか', 'GRACE',
                 'Grace']
CONVENI_KEYWORD = ['conveni', 'コンビニ', 'こんびに', 'ファミマ', 'ふぁみま', 'ファミリーマート',
                   'ローソン', 'ロソーン', 'ろーそん', 'セブンイレブン', 'セブン']
YUTAKA_KEYWORD = ['yutaka', 'ゆたか', 'ユタカ', 'ドラッグユタカ']

intents = discord.Intents.all()
client = discord.Client(intents=intents)


@client.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
    await ctx.send(error_msg)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user or \
       message.channel.id != MONEY_CH_ID:
        return

    if message.content.startswith('$'):
        with open('money_delta.txt', 'r') as fin:
            money_delta = (int)(fin.readline())

        if message.content == '$now':
            await message.channel.send(f'今の差額（竹馬 - はる）：{money_delta / 2} 円')
            return

        transaction_info = []

        transaction_info.append(datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=9))
        ).strftime('%Y/%m/%d'))

        for shop_keyword in [COREMO_KEYWORD, SEISENKAN_KEYWORD,
                             GRACE_KEYWORD, CONVENI_KEYWORD, YUTAKA_KEYWORD]:
            if any(map(message.content.__contains__, shop_keyword)):
                transaction_info.append(shop_keyword[0])
                break
        else:
            transaction_info.append('others')

        if message.author.id == TAKE_ID:
            transaction_info.append("take")
        elif message.author.id == HARU_ID:
            transaction_info.append("haru")
        else:
            transaction_info.append("who")

        price = re.findall(r"\d+", message.content)
        if len(price) == 0:
            await message.add_reaction("❓")
        else:
            transaction_info.append(price[0])
            with open('transactions.csv', 'a') as fout:
                print(",".join(transaction_info), file=fout)
            if message.author.id == TAKE_ID:
                money_delta += int(price[0])
            elif message.author.id == HARU_ID:
                money_delta -= int(price[0])
            with open('money_delta.txt', 'w') as fout:
                print(money_delta, file=fout)
            print("transaction info: ", transaction_info)
            print("money_delta: ", money_delta)
            await message.add_reaction("✅")


@tasks.loop(hours=24)
async def loop():
    with open('money_delta.txt', 'r') as fin:
        money_delta = (int)(fin.readline())

    await client.get_channel(MONEY_CH_ID)\
        .send(f'今の差額（竹馬 - はる）：{money_delta / 2} 円')
    return

token = getenv('DISCORD_BOT_TOKEN')
client.run(token)
