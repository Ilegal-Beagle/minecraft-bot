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
mc_data = require('minecraft-data')(bot.version)

LOGS = [
    'acacia_log',
    'birch_log',
    'cherry_log',
    'dark_oak_log',
    'jungle_log',
    'mangrove_log',
    'oak_log',
    'spruce_log']
LOGS = [mc_data.blocksByName[log].id for log in LOGS]

bot.loadPlugin(pathfinder.pathfinder)
print("Started mineflayer")

@On(bot, 'spawn')
def handle(*args):
    print("I spawned 👋")
    movements = pathfinder.Movements(bot)

    @On(bot, 'chat')
    def handleMsg(this, sender, message, *args):
        if not sender and (sender == BOT_USERNAME):
            return

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
            go_to(pos)

        elif 'look at me' in message:
            sender_pos = bot.players[sender].entity['position']
            bot.lookAt(sender_pos.offset(0, 1, 0))

        elif 'mine logs' in message:
            # find one log nearby and go to it 
            blocks = find_blocks(LOGS, block_count=1)
            blocks = [bot.blockAt(block) for block in blocks]

            if not blocks:
                bot.chat('ion see any doggone trees \'round these parts')
                return
            
            pos = blocks[0]['position']
            bot.pathfinder.setMovements(movements)
            go_to(pos)

            # find all reachable blocks at tree and mine it
            blocks = find_blocks(LOGS, 5, 64)
            blocks = [bot.blockAt(block) for block in blocks]
            blocks = [block for block in blocks if bot.canDigBlock(block)]
            for block in blocks:
                bot.dig(block,True)
                print(block.position)                
                bot.chat('mined all nearby logs!')


@On(bot, 'end')
def handle(*args):
    print("Bot ended!", args)

def go_to(pos):
    bot.pathfinder.setGoal(pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, RANGE_GOAL))

def find_blocks(block_id:list=None, search_area:int=512, block_count:int=512) -> list:
    return bot.findBlocks(
        {
            'point':bot.entity.position.offset(0,1,0),
            'matching': block_id,
            'maxDistance':search_area,
            'count': block_count
        })
