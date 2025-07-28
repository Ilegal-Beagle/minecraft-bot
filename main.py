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
        if sender and (sender != BOT_USERNAME):

            if 'come' in message:
                player = bot.players[sender]
                target = player.entity

                if not target:
                    bot.chat("I don't see you !")
                    return

                pos = target.position
                bot.pathfinder.setMovements(movements)
                go_to(pos)

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
                go_to_nearest_log()

            elif 'l' in message:
                mine_nearby_logs()


@On(bot, 'diggingCompleted')
def handle(block, *args):
    print(f'block broken')

@On(bot, 'health')
def handle(*args):
    bot.chat('ouch!!')

@On(bot, 'end')
def handle(*args):
    print("Bot ended!", args)

def go_to(pos):
    bot.pathfinder.setGoal(pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, RANGE_GOAL))


def find_blocks(block_identifier:str=None, search_area:int=512) -> list:
    blocks = bot.findBlocks(
        {
            'point':bot.position,
            'matching':lambda block: block.name != 'air',
            'count': search_area
        })
    
    blocks = [bot.blockAt(pos) 
              for pos in blocks if block_identifier in bot.blockAt(pos).name]
    return blocks

def go_to_nearest_log(search_area=512):
    blocks = find_blocks('log',search_area)
    
    # pathfind to nearest log in list
    if blocks:
        pos = blocks[0]
        bot.pathfinder.setGoal(
            pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, RANGE_GOAL))
    else:
        bot.chat('ion see any doggone trees \'round these parts')

def mine_nearby_logs(search_area:int=512):
    blocks = find_blocks('log')    
    
    if blocks:
        for block in blocks:
            if bot.canDigBlock(block):
                bot.dig(block,True)
                print(block.position)
        
        bot.chat('mined all nearby logs!')
    else:
        bot.chat('ion see any doggone trees \'round these parts')