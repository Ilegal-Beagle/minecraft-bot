from javascript import require, On, AsyncTask
from pprint import pprint
import asyncio, random
import discord_bot as db

mineflayer = require('mineflayer')
pathfinder = require('mineflayer-pathfinder')
vec3 = require('vec3')

class Bot:
    RANGE_GOAL=1
    LOG_NAMES = [
        'acacia_log',
        'birch_log',
        'cherry_log',
        'dark_oak_log',
        'jungle_log',
        'mangrove_log',
        'oak_log',
        'spruce_log']
    ORE_NAMES = [
        'coal_ore',
        'copper_ore',
        'diamond_ore',
        'emerald_ore',
        'gold_ore',
        'iron_ore',
        'lapis_ore',
        'redstone_ore',
        'deepslate_coal_ore',
        'deepslate_copper_ore',
        'deepslate_diamond_ore',
        'deepslate_emerald_ore',
        'deepslate_gold_ore',
        'deepslate_iron_ore',
        'deepslate_lapis_ore',
        'deepslate_redstone_ore',
        
    ]
    AIR_ID = 1

    def __init__(self, host:str, port:int, username:str, version:str, disc_bot=None):
        self.bot = mineflayer.createBot({
            'host': host,
            'port': port,
            'username': username,
            'auth':'offline',
            'hideErrors': True,
            'version':version,
        })
        self.disc_bot = disc_bot
        self.mc_data = require('minecraft-data')(self.bot.version) # used for getting ID of blocks
        self.LOGS = [self.mc_data.blocksByName[log].id for log in self.LOG_NAMES] # gets log IDs
        self.ORES = [self.mc_data.blocksByName[ore].id for ore in self.ORE_NAMES] # gets ore IDs
        self.bot.loadPlugin(pathfinder.pathfinder)
        self.movements = pathfinder.Movements(self.bot) # sets the type of movements pathing can do
        self.wandering = False # flag for when bot is in wandering state
        self.sender_req_actions = ['come', 'look at me'] # actions that require a sender argument
        
        # Dict that defines keywords to find in messages and the function those words should execute
        self.actions = {
            'come': self.come_to_sender,
            'look at me': self.look_at,
            'go to entity': self.go_to_nearest_entity,
            'mine logs': self.mine_logs,
            'build hut': self.build_hut,
            'attack': self.attack,
            'quit': self.quit,
            'wander': self.wander_loop,
        }
        
        self.setup_events()

    def go_to(self, pos):
        try:
            goal = pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, self.RANGE_GOAL) # set destination
            self.bot.pathfinder.setMovements(self.movements) # set how bot will move
            self.bot.pathfinder.goto(goal)
        except Exception:
            self.bot.chat("Couldn't reach the destination.")

    def find_blocks(
        self,
        block_id:list=lambda block: block,
        search_area:int=512,
        block_count:int=512) -> list:
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
            # that is why you will see functions that are wrapped inside another
            # function with the decorator @AsyncTask(start=True). this is the 
            # JS way of waiting for it to finish

            for keyword, function in self.actions.items():
                if keyword in message:
                    try:
                        @AsyncTask(start=True)
                        def run(task):
                            self.wandering = not self.wandering if keyword == 'wander' else self.wandering
                            function(sender) if keyword in self.sender_req_actions else function()

                    except Exception as e:
                        print(f'ERROR: {e}, {type(e)}')

        @On(self.bot, 'end')
        def handle(*args):
            print("Bot ended!", args)

    # ACTIONS THAT THE BOT CAN DO

    def come_to_sender(self, sender):
        # get the entity obj. of sender
        print(sender)
        player = self.bot.players[sender].entity

        if not player: # no target found
            self.bot.chat("I don't see you !")
            return
    
        self.go_to(player.position)

    def go_to_nearest_entity(self):
        entity = self.bot.nearestEntity()

        if not entity:
            self.bot.chat('I dont see you!')
            return

        self.go_to(entity.position)

    def look_at(self, sender):
        sender_pos = self.bot.players[sender].entity.position
        self.bot.lookAt(sender_pos.offset(0, 1, 0))

    def mine_logs(self):
        # find one log nearby
        blocks = list(map(lambda block: self.bot.blockAt(block), self.find_blocks(self.LOGS, block_count=1)))

        if not blocks:
            self.bot.chat('ion see any doggone trees \'round these parts')
            return
        
        self.go_to(blocks[0]['position']) # go to the block

        self.bot.waitForTicks(10)

        # find all reachable blocks at tree and mine it
        blocks = list(map(lambda block: self.bot.blockAt(block), self.find_blocks(self.LOGS, 5, 64)))
        blocks = [block for block in blocks if self.bot.canDigBlock(block)]
        for block in blocks:
            try:
                self.bot.dig(block,True)
                print(block.position)
            except Exception:
                self.bot.chat('couldnt break block in given time. aborting')
        self.bot.chat('mined all nearby logs!')

    def mine_ore(self):
        # find one log nearby 
        blocks = map(lambda block: self.bot.blockAt(block), self.find_blocks(self.ORES, block_count=1))

        if not blocks:
            self.bot.chat('ion see any doggone ore \'round these parts')
            return
        
        self.go_to(blocks[0].position) # go to the block

        # find all reachable blocks at tree and mine it
        blocks = map(lambda block: self.bot.blockAt(block), self.find_blocks(self.ORES, 5, 64))
        blocks = [block for block in blocks if self.bot.canDigBlock(block)]
        for block in blocks:
            try:
                self.bot.dig(block,True)
                print(block.position)
            except Exception:
                self.bot.chat('couldnt break block in given time. aborting')
        self.bot.chat('mined all nearby ores!')


    def build_hut(self):
        blocks = self.find_blocks(search_area=5, block_count=250)
        blocks = list(filter(lambda block: self.bot.blockAt(block).name == 'air', blocks))

        print(len(blocks))
        for block in blocks:
            if not self.bot.canDigBlock(block):
                print('too far')
                self.go_to(block.position)
            self.bot.dig(block, True)
        
        self.bot.chat('finished!')

    def attack(self):
        # filter what entities it detects
        entity = self.bot.nearestEntity(
            lambda entity: entity.kind in ['Hostile mobs', 'player', 'Passive mobs'])

        if not entity:
            self.bot.chat('I dont see you!')
            return

        # attack until it is gone
        try:
            while entity.isValid:
                self.go_to(entity.position)
                self.bot.attack(entity)
        except Exception as e:
            print(f'ERROR: {e}, {type(e)}')

        self.bot.chat(f'{entity.name} killed')

    def wander_loop(self):
        while self.wandering:
            self.bot.look(random.random()*20, 0)
            walk_forward_time = random.randint(1, 30)
            self.bot.setControlState("forward", True)
            self.bot.setControlState("jump", True) if random.random() < .05 else None
            self.bot.waitForTicks(walk_forward_time)
            self.bot.clearControlStates()
            self.bot.waitForTicks(random.randint(0, 50))

    def quit(self):
        try:
            self.bot.chat('Bye!')
            self.bot.quit()
        except Exception as e:
            print(f'ERROR: {e}, {type(e)}')

    def send(self, msg:str):
        self.bot.chat(msg)

if __name__ == '__main__':
    bot = Bot('localhost', 3000, 'python', '1.21')