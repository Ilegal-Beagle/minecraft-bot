from javascript import require, On
from pprint import pprint

mineflayer = require('mineflayer')
pathfinder = require('mineflayer-pathfinder')
vec3 = require('vec3')

RANGE_GOAL = 2
BOT_USERNAME = 'python'

bot = mineflayer.createBot({
    'host': 'localhost',
    'port': 3000,
    'username': BOT_USERNAME,
    'auth':'offline',
    'hideErrors': False,
    'version':'1.21',
})

bot.loadPlugin(pathfinder.pathfinder)
print("Started mineflayer")

@On(bot, 'spawn')
def handle(*args):
    print("I spawned 👋")
    movements = pathfinder.Movements(bot)

    @On(bot, 'chat')
    def handleMsg(this, sender, message, *args):
        # TODO: remove repetition
        if sender and (sender != BOT_USERNAME):

            if 'come' in message:
                player = bot.players[sender]
                target = player.entity

                if not target:
                    bot.chat("I don't see you !")
                    return

                pos = target.position
                bot.pathfinder.setMovements(movements)
                bot.pathfinder.setGoal(pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, RANGE_GOAL))

            elif 'test' in message:
                bot.chat(f'i am in {bot.game.dimension}')

            elif 'go to entity' in message:
                entity = bot.nearestEntity()
                if not entity:
                    bot .chat('I dont see you!')
                    return

                pprint(entity)
                pos = entity.position
                bot.pathfinder.setMovements(movements)
                bot.pathfinder.setGoal(pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, RANGE_GOAL))

            elif 'look at me' in message:
                sender_pos = bot.players[sender].entity['position']
                bot.lookAt(sender_pos.offset(0, 1, 0))

            elif 'look for new tree' in message:
                blocks = bot.findBlocks(
                    {
                        'point':bot.position,
                        'matching':lambda block: block.name != 'air',
                        'count':2048 + 2048
                    })
                
                blocks = [bot.blockAt(pos) for pos in blocks if 'log' in bot.blockAt(pos).name]
                
                if blocks:
                    pos = blocks[0]
                    bot.pathfinder.setGoal(
                        pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, RANGE_GOAL))
                else:
                    bot.chat('ion see any doggone trees \'round these parts')

            elif 'l' in message:
                print(bot['position'])
                blocks = bot.findBlocks(
                    {
                        'point':bot.position,
                        'matching':lambda block: block.name != 'air',
                        'count':512
                    })
                
                blocks = [bot.blockAt(pos) for pos in blocks if 'log' in bot.blockAt(pos).name]
                
                if blocks:
                    for block in blocks:
                        print(f'{block.name}, {block.position}')

                    for block in blocks:
                        if bot.canDigBlock(block):
                            bot.dig(block,True)
                            print(block.position)
                        else:
                            bot.chat(f'bruh you KNOW i cant reach that {block.name} at {block.position}')
                else:
                    bot.chat('ion see any doggone trees \'round these parts')


@On(bot, '')
                
@On(bot, 'health')
def handle(*args):
    bot.chat('ouch!!')

@On(bot, 'end')
def handle(*args):
  print("Bot ended!", args)