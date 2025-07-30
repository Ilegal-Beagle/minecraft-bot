from javascript import require, On, AsyncTask
from pprint import pprint
import asyncio, threading

mineflayer = require('mineflayer')
pathfinder = require('mineflayer-pathfinder')
vec3 = require('vec3')

class Bot:
    RANGE_GOAL=0
    LOG_NAMES = [
        'acacia_log',
        'birch_log',
        'cherry_log',
        'dark_oak_log',
        'jungle_log',
        'mangrove_log',
        'oak_log',
        'spruce_log']
    AIR_ID = 0

    def __init__(self, host:str, port:int, username:str, version:str):
        self.bot = mineflayer.createBot({
            'host': host,
            'port': port,
            'username': username,
            'auth':'offline',
            'hideErrors': False,
            'version':version,
        })
        self.mc_data = require('minecraft-data')(self.bot.version) # used for getting ID of blocks
        self.LOGS = [self.mc_data.blocksByName[log].id for log in self.LOG_NAMES] # gets log IDs
        self.bot.loadPlugin(pathfinder.pathfinder)
        self.movements = pathfinder.Movements(self.bot) # sets the type of movements pathing can do
        self.setup_events()

    def go_to(self, pos):
        try:
            goal = pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, self.RANGE_GOAL) # set destination
            self.bot.pathfinder.setMovements(self.movements) # set how bot will move
            self.bot.pathfinder.goto(goal)
        except Exception:
            self.bot.chat("Couldn't reach the destination.")
            self.bot.pathfinder.stop()

    def find_blocks(self, block_id:list=None, search_area:int=512, block_count:int=512) -> list:
        return self.bot.findBlocks(
            {
                'point':self.bot.entity.position, # starting point to search blocks
                'matching': block_id, # give a list of block IDs to look for. if None, will retreive any block
                'maxDistance':search_area, # how far to search for blocks
                'count': block_count # how many blocks to return
            })

    def setup_events(self):
        # this is where you tell the bot to do something when a certain event happens
        @On(self.bot, 'spawn')
        def handle(*args):
            self.movements = pathfinder.Movements(self.bot)
            print("I spawned 👋")

        @On(self.bot, 'chat')
        def handleMsg(this, sender, message, *args):
            # NOTE: some functions need to wait to see if function was a success
            # that is why you will see some functions that are wrapped inside another
            # function with the decorator @AsyncTask(start=True). this is the JS way of
            # of 'await'ing it

            # NOTE: Should find a way to make this more consice
            if not sender and (sender == BOT_USERNAME):
                return

            if 'come' in message:
                try:
                    @AsyncTask(start=True)
                    def async_come_to_sender(task):
                        self.come_to_sender(sender)
                except Exception as e:
                    print(e)

            elif 'go to entity' in message:
                try:
                    @AsyncTask(start=True)
                    def async_go_to_entity(task):
                        self.go_to_nearest_entity()
                except Exception as e:
                    print(e)

            elif 'look at me' in message:
                try:
                    @AsyncTask(start=True)
                    def async_go_to_entity(task):
                        self.look_at(sender)
                except Exception as e:
                    print(e)

            elif 'mine logs' in message:
                try:
                    @AsyncTask(start=True)
                    def async_mine_logs(task):
                        self.mine_logs()
                except Exception as e:
                    print(e)

            elif 'build hut' in message:
                try:
                    @AsyncTask(start=True)
                    def async_build_hut(task):
                        self.build_hut()
                except Exception as e:
                    print(f'ERROR: {e}')

        @On(self.bot, 'end')
        def handle(*args):
            print("Bot ended!", args)

    # Event handler functions
    def come_to_sender(self, sender):
        # get the entity obj. of sender
        player = self.bot.players[sender]
        target = player.entity

        if not target: # no target found
            self.bot.chat("I don't see you !")
            return
    
        self.go_to(target.position)

    def go_to_nearest_entity(self):
        entity = self.bot.nearestEntity()

        if not entity:
            self.bot.chat('I dont see you!')
            return

        pos = entity.position
        self.go_to(pos)

    def look_at(self, sender):
        sender_pos = self.bot.players[sender].entity['position']
        self.bot.lookAt(sender_pos.offset(0, 1, 0))

    def mine_logs(self):
        blocks = self.find_blocks(self.LOGS, block_count=1) # find one log nearby 
        blocks = [self.bot.blockAt(block) for block in blocks]  # get the block obj of block

        if not blocks:
            self.bot.chat('ion see any doggone trees \'round these parts')
            return
        
        self.go_to(blocks[0]['position']) # go to the block

        # find all reachable blocks at tree and mine it
        blocks = self.find_blocks(self.LOGS, 5, 64)
        blocks = [self.bot.blockAt(block) for block in blocks]
        blocks = [block for block in blocks if self.bot.canDigBlock(block)]
        for block in blocks:
            try:
                self.bot.dig(block,True)
                print(block.position)
            except Exception:
                self.bot.chat('couldnt break block in given time. aborting')
                self.bot.stopDigging()
        self.bot.chat('mined all nearby logs!')

    def build_hut(self):
        blocks = self.find_blocks(lambda block: block, search_area=5, block_count=250)
        blocks = [ # gets rid of air blocks and blocks below bot
            self.bot.blockAt(block) for block in blocks
            if block.y >= self.bot.entity.position.y and self.mc_data.blocksByName[self.bot.blockAt(block).name].id != self.AIR_ID
            ]

        print(len(blocks))
        for block in blocks:
            if not self.bot.canDigBlock(block):
                print('too far')
                self.go_to(block.position)
            self.bot.dig(block, True)
        
        self.bot.chat('finished!')

if __name__ == '__main__':
    bot = Bot('localhost', 3000, 'python', '1.21')