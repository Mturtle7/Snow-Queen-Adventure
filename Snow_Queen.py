#!/usr/local/bin/python
#The Snow Queen: a simple adventure game
#by Milo Kim

from enum import Enum, auto
import re

#define classes
#class Game:
#	def __init__(self, player, rooms):
#		self.player = player
#		self.rooms = rooms
#	def win(self):
#		print("Congratulations,", self.player + "!")

class Direction(Enum):
	NORTH = auto()
	SOUTH = auto()
	EAST = auto()
	WEST = auto()

def get_direction(s):
	s = s.lower()
	for name, dir in Direction.__members__.items():
		if ((name.lower() == s) or (name.lower()[0] == s)):
			return dir
	return None

class Element():
	lastest_id = 1
	def __init__(self, id, name, descr):
		self.id = id
		self.name = name
		self.descr = descr
	def new_id(self):
		Element.lastest_id+=1
		Element.lastest_id
	def inspect(self):
		return self.descr
	def __str__(self):
		return self.name
	def __repr__(self):
		return self.__str__()

class Player(Element):
	#attributes: name (string), location (Room), items (list of Items)
	def __init__(self, name, descr, location, inventory = []):
		self.id = Element.new_id
		self.name = name
		self.descr = descr
		self.location = location
		self.items = inventory
	def __str__(self):
		return self.name
	def __repr__(self):
		return self.__str__()
	def move(self, s):
		#later, should really remember to untangle the letter-or-word functionality from move and back to the user interface
		dir = get_direction(s)
		if (not dir):
			print("Move_error: not a cardinal direction (north, east, south, west, or first letters thereof)")
		elif (dir in self.location.exits):
			print("Moving", dir.name.lower())
			self.location = self.location.exits[dir]
		else:
			print("Move_error: no exit that way")
	def take(self, new_item):
		new_item = new_item.lower()
		for x in self.location.objects:
			#print("found the", x.name)
			if x.name.lower() == new_item and isinstance(x, Item):
				self.items.append(x)
				self.location.objects.remove(x)
				print("you take the", x.name)
				break
			elif x.name.lower() == new_item:
				print("you can't pick that up")
				break
		else:
			print("you don't see that in here")
	def use_item(self, tool, target):
		tool = tool.lower()
		target = target.lower()
		for x in self.location.objects:
			if x.name.lower() == target:
				#print("found target:", x.name)
				good_target = x
				break
		else:
			print("you don't see that in here")
			return

		for y in self.items:
			if y.name.lower() == tool:
				#print("found tool:", y.name)
				y.use_on(good_target, self)
				break
		else:
			print("you don't have that with you")



class Room(Element): 
	#attributes: name (string), descr (string), objects (list of Things), exits (dictionary of chars->rooms)

	def __init__(self, name, descr, objects = [], n = None, e = None, s = None, w = None):
		self.id = Element.new_id
		self.name = name
		self.descr = descr
		self.exits = {}
		self.add_exits(n = n, e = e, s = s, w = w)
		self.objects = objects
		#print("making", self.name, ": exits are", self.exits) 
	def __str__(self):
		return self.name
	def __repr__(self):
		return self.__str__()
	def add_exits(self, n = None, e = None, s = None, w = None):
		if n:
			self.exits[Direction.NORTH] = n
		if e:
			self.exits[Direction.EAST] = e
		if s:
			self.exits[Direction.SOUTH] = s
		if w:
			self.exits[Direction.WEST] = w
	def get_exits(self):
		# returns a list of the full words for exit directions
		return [k.name.lower() for k in self.exits.keys()]
	def inspect(self):
		response = self.descr
		for x in self.objects:
			response += ("\nThere is a {} here".format(x))
		return response

class Thing(Element):
	#attribues: name(string), descr(string), is_used(boolean)
	def __init__(self, name, descr):
		self.id = Element.new_id
		self.name = name
		self.descr = descr
		self.is_changed = False

class Item(Thing):
	#attribues: name(string), descr(string), use(function), is_used(boolean)
	def __init__(self, name, descr, use):
		self.id = Element.new_id
		self.name = name
		self.descr = descr
		self.use = use
		self.is_changed = False
	def use_on(self, target, player):
		check = self.use(target, player)
		if check:
			target.descr = check
			target.is_changed = True
		return check

#class SetPiece(Thing):
#	def __init__(self, name, descr, use):
#		self.name = name
#		self.descr = descr
#		self.is_changed = False

def run_game(player_name):
	hero = initialize_game(player_name, "an innocent young girl, searching for her friend Kay")
	print("You are", hero, ", distraught at Kay's disappearance")
	print("""\ncommands are: 
	quit, help, inventory, exits, look, 
	move [compass direction - word or first letter], inspect [name], 
	take [item_name], use [item_name] on [name]""")

	to_quit = False
	while(to_quit != True):
		command = input("you are in {}. What do you do?\n".format(hero.location))
		if (command == "quit"):
			to_quit = True
		elif (command == "help"):
			print("commands are: quit, help, inventory, exits, look, inspect [item_name], move [compass direction]")
		elif (command == "inventory"):
			print(hero.items)
		elif (command == "exits"):
			print("Exits are:", ", ".join(hero.location.get_exits()))
		elif (command == "look"):
			print(hero.location.inspect())
		elif (command[:4] == "move"):
			hero.move(command[5:])
		elif (get_direction(command)):
			hero.move(command)
		elif (command[:7] == "inspect"):
			x = command[8:].lower()
			if x == hero.name.lower():
				print(hero.inspect())
			elif x == hero.location.name.lower():
				print(hero.location.inspect())
			elif x in [i.name.lower() for i in hero.items]:
				for j in hero.items:
					if x == j.name.lower():
						print(j.inspect())
			elif x in [i.name.lower() for i in hero.location.objects]:
				for j in hero.location.objects:
					if x == j.name.lower():
						print(j.inspect())
			else:
				print("you don't see anything with that name here")
		elif(command[:4] == "take"):
			hero.take(command[5:])
		elif(command[:3] == "use"):
			on_index = command.find(" on ")
			if on_index == -1:
				print("use format: use [item_name] on [name]")
			else:
				hero.use_item(command[4:on_index], command[(on_index+4):])
		else:
			print("I don't understand that")

def initialize_test_game(player_name, player_descr):
	balloon = Thing("Balloon", "a test Set Piece, to be popped with the Pin")
	def pin_pop(target, player):
		if target.name == "Balloon":
			print("pop!")
			return True
		else:
			print("Error, test failed - target not a balloon")
			return False

	pin = Item("Pin", "a test Item, to use on balloon", pin_pop)

	test_room_north = Room("Testing Suite North", "a cold room")
	test_room1 = Room("Testing Suite Start", "a boring room", [pin, balloon])

	test_room_north.add_exits(s = test_room1)
	test_room1.add_exits(n = test_room_north)

	return Player(player_name, player_descr, test_room1)

def parse_map(map_string):
	# will be like [{name:"deep_forest",start:19,end:aa,west:name,east:name}]
	previous_room_list = []
	# will be like [{position:22,locked:True}]
	exits = []
	current_room_list = []
	lines = map_string.split("\n")
	for line in lines:
		current_room_list = []
		previous_room = None
		for m in re.finditer(r'(:)?(\w+)', line):
			room = dict()
			#m.group(1) = ':'
			#m.group(2) = 'crossroads'
			#m.group(0) = ':crossroads'
			room['name'] = m.group(2)
			room['start'] = m.start
			room['end'] = m.end
			if (m.group(1) and previous_room):
				room['west'] = previous_room['name']
				previous_room['east'] = room['name']
			previous_room = room

def initialize_game(player_name, player_descr):

	# north is up, west is left, east is right
	map = parse_map("""
                    a             :b               c
               deepredroom  :lightblueroom

                    deep_forest
                        ^#
                    stables
                        ^
                     bedrooms        kitchens
                         ^              ^
                     first_hall:second_hall
                        ^              ^
                    palace_gates   back_stairs
                        ^#              ^#
            old_hollow:crossroads:garden_path
                           ^#
            odd_house:flower_garden
                 ^
            cherry_orchard
                 ^#
            river_bank-><-start_room
	""")

	"""puzzle notes:
		player BEGINS with item "eyes", which almost always say "you see the light of hope inside it - just as always. Kay used to see it too."
			using eyes on things like witch's hat and Kay himself produces more spiritual effects in you and them
		The Kind Woman actually has a WHOLE TON of little quests, that are actually magic lessons,
			and which get you various special objects to use in MUCH LATER puzzles.
			THIS is what keeps the player going back and forth, so this doesn't get so totally linear.
		player must find bauble to give to crow so he can go to his sweetheart for the back door key, 
			or maybe learn crow language from something in the odd house; or maybe use heart on crow to hear it clearly? YES

		player must find and light lamp to be able to clearly see the prince and princess
			then, use heart on them to get them to tell them everything and get them to like you
		

	"""

	#create STARTING ROOM; things = wooden box and watering can
	box = Thing("Wooden Box", """This large wooden box streches out the window to Kay's window. 
		It carries a rose bush, now wilted from neglect""")

	def water_rose(target, player):
		if target.name == "Wooden Box" and target.is_changed == False:
			print("You water the rose, and it seems to perk up with life and renewal against the bitter snow")
			return """This large wooden box streches out the window to Kay's window. 
It carries a rose bush, fresh and ready to face the oncoming winter."""
		else:
			print("it seems to get quite wet, but nothing else happens.")
			return False

	water_can = Item("Watering Can", "a small watering can, kept in your grandmother's set of gardening tools.", water_rose)
	start_descr = "a small cottage in a large town, with not much room but a roaring fire and lots of love."
	start_room = Room("Grandma's Cottage", start_descr, [box, water_can])

	#creating RIVER BANK; things = river and boat
	river = Thing("River", """The wide, cruel river that Grandma says took Kay away from you. 
He vanished in winter, but now springmelt makes the river rush even faster.""")
	boat = Thing("Boat", "a boat - small compared to the river but quite large to someone of your size.\nIt is stuck in the reeds of the river.")
	river_bank = Room("The River Bank", """A muddy bank, at the side of a wide river filled with reeds. 
Grandmother said that Kay mmust have drowned here. But you can't just accept such cruelty from the world. 
Perhaps an offering would encourage the river to bring Kay back to you...""", [river, boat])

	#creating CHERRY ORCHARD: thing = rose trees, cherry trees, kind_woman
	cherry_orchard = Room("The Cherry Orchard", """A large cherry orchard, streching north away from the river banks.
In the middle of it is a small red house, with strange re-and-blue windows. 
It also has a thatched roof, and outside are two wooden soldiers that present arms to you as you pass.""")

	#drawing connections between all the rooms
	start_room.add_exits(w = river_bank)
	river_bank.add_exits(e = start_room)
	cherry_orchard.add_exits(s = river_bank)

	#creating player; things = red shoes, heart
	def offer_shoes(target, player):
		if target.name == "River":
			print("You throw the shoes into the water, but the waves just carry them right back.\nMaybe if you were farther out...")
			return False
		if target.name == "Boat":
			print("""You climb to the far end of the boat and throw the shoes away, but the boat was not fastened, and your movement sends it gliding away from the land...
You hasten to reach the end of the boat, but by then it is already a yard away from the bank.
You cry, but no one hears you but the sparrows, who sing as if to comfort you, "here we are! here we are!
You watch the beautiful banks of the river pass by, and think that maybe the river is taking you to Kay, which cheers you.
eventually you come to a house, where you see and old woman. At your request, she wades out to drag the boat back to land with her crutch.""")
			player.location.add_exits(n = cherry_orchard)
			player.move("n")
			return "a boat - small compared to the river but quite large to someone of your size.\nIt is resting on the mud of the shore."
		else:
			print("You would never give up your fine red shoes like that.")
			return False
	shoes = Item("Red Shoes", "Your fine Red Shoes, which you like better than anything else you own", offer_shoes)

	def use_heart(target, player):
		if target.name == "flower_hat":
			print("""you look at the woman's hat, and though you see an impossible multitude of flowers on it, some of which are strange and exotic and whose names you can only guess at...
the prettiest of all of them is the rose. You realize with a jolt that roses, your favorite flower (for some reason you can't remember), are the only flower you hvae not seen in this house.
you run franctically into the garden, then the orchard, crying, "What, are there no roses here?".
When you find none, you sit down and weep, and your tears fall down onto a bed of seemingly empty dirt, and a rose-tree blooms up at once.
It had always been there, before the good Which here had made it sink below the ground so you would always stay here.
But now, the smell of real live roses reminds you of the fresh and brave roses back home,a nd of you best friend Kay.
"Oh, how I have been detained!", you shout, and go off once more to find Kay, out past the garden gate you had never considered leaving before.""")
		else:
			print("You see the light of hope and love shining from deep within it, just as you always do. Kay used to see it too...")
	heart = Item("Heart", "innocent and pure.", use_heart)

	new_player = Player(player_name, player_descr, start_room, [shoes, heart])

	return new_player


#Main Program

print("*	*	*	*	*	*	*	*	*	*\nThe Snow Queen: A Fairy Tale Adventure\nBy Milo Kim")
print("includes original descriptions from the Hans Christian Anderson fairy tale\n*	*	*	*	*	*	*	*	*	*")

#intro entirely made from excerpts from fairy tale (except for user input)

intro1 = """In a large town, full of houses and people, there is not room for everybody to have even a little garden, 
therefore they are obliged to be satisfied with a few flowers in flower-pots. 
In one of these large towns lived two poor children who had a garden something larger and better than a few flower-pots. 
They were not brother and sister, but they loved each other almost as much as if they had been."""
print(intro1)
player_name = input("The boy's name was Kay. What was the girl's name?")
#player_name = "Gerda"

run_game(player_name)



#remember to replace "Gerda" w/ player name here if these are ever actually included in intro
intro2 = """...Those were splendid summer days. How beautiful and fresh it was out among the rose-bushes, 
which seemed as if they would never leave off blooming. One day Kay and Gerda sat looking at a book full of 
pictures of animals and birds, and then just as the clock in the church tower struck twelve, Kay said, 
“Oh, something has struck my heart!” and soon after, “There is something in my eye.”

The little girl put her arm round his neck, and looked into his eye, but she could see nothing.

“I think it is gone,” he said. But it was not gone; it was one of those bits of the looking-glass—that magic mirror, 
of which we have spoken—the ugly glass which made everything great and good appear small and ugly, while all that
was wicked and bad became more visible, and every little fault could be plainly seen. Poor little Kay had also 
received a small grain in his heart, which very quickly turned to a lump of ice. He felt no more pain, but the 
glass was there still. “Why do you cry?” said he at last; “it makes you look ugly. There is nothing the matter 
with me now. Oh, see!” he cried suddenly, “that rose is worm-eaten, and this one is quite crooked. After all they 
re ugly roses, just like the box in which they stand,” and then he kicked the boxes with his foot, and pulled off 
he two roses.

“Kay, what are you doing?” cried the little girl; and then, when he saw how frightened she was, 
he tore off another rose, and jumped through his own window away from little Gerda. """
#print(intro2)

intro3 = """ In the great square, the boldest among the boys would often tie their sledges to the country people’s 
carts, and go with them a good way. This was capital. But while they were all amusing themselves, and Kay with 
them, a great sledge came by; it was painted white, and in it sat some one wrapped in a rough white fur, and 
wearing a white cap. The sledge drove twice round the square, and Kay fastened his own little sledge to it, so 
that when it went away, he followed with it. It went faster and faster right through the next street, and then the 
person who drove turned round and nodded pleasantly to Kay, just as if they were acquainted with each other, but 
whenever Kay wished to loosen his little sledge the driver nodded again, so Kay sat still, and they drove out 
through the town gate. Then the snow began to fall so heavily that the little boy could not see a hand’s breadth 
before him, but still they drove on; then he suddenly loosened the cord so that the large sled might go on without 
him, but it was of no use, his little carriage held fast, and away they went like the wind. Then he called out 
loudly, but nobody heard him, while the snow beat upon him, and the sledge flew onwards. Every now and then it 
gave a jump as if it were going over hedges and ditches. The boy was frightened, and tried to say a prayer, but 
he could remember nothing but the multiplication table.

The snow-flakes became larger and larger, till they appeared like great white chickens. All at once they sprang 
on one side, the great sledge stopped, and the person who had driven it rose up. The fur and the cap, which were 
made entirely of snow, fell off, and he saw a lady, tall and white, it was the Snow Queen.

...They flew over woods and lakes, over sea and land; below them roared the wild wind; the wolves howled and 
the snow crackled; over them flew the black screaming crows, and above all shone the moon, clear and bright,
—and so Kay passed through the long winter’s night, and by day he slept at the feet of the Snow Queen.  """
#print(intro3)

"""
print(hero.location)
hero.location.inspect()

print(hero.location.objects)
print("trying to take the Pin")
hero.take("Pin")
hero.items[0].inspect()

print("trying to use the Pin on the Balloon")
hero.use_item("Pin", "Balloon")
hero.location.objects[0].inspect()

hero.location.get_exits()
hero.move("N")
print(hero.location)
hero.location.inspect()

hero.location.get_exits()
hero.move("S")
print(hero.location)
hero.location.inspect()


production notes:
		issue: maybe set attribute to rooms so instead of seperate nswe attributes, just one List (or array?)
			of exits. Or maybe dictionary? keys = chars, values = rooms? Use **kwargs?
		conclusion: set char->room dictionary attribute exits, default None, function add_exits
			in addition to an initalization exits option
		idea: consolidate all classes so far into Element base class, so name & descr & inspect easy
		issue: is game data just consolidated in the player? originally tried Start_Wars.py method 
		of Game(), but seems unnecesary right now.
		idea: have unique ID for each element"""
