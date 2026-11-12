# Name: Luke Heaton, Matthew Conger, John Sandberg & Jacob harrison
# Enter your python code below. Replace this line with a description.
import random
import os
import platform


def clear_screen():
    """
    Clears the terminal screen to make it easier to follow along with code.
    """
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

clear_screen()


#Moves Class
class Move:
    def __init__(self,move_name,elemental_type,low_attack_points,high_attack_points):
        self.move_name=move_name
        self.elemental_type=elemental_type
        self.low_attack_points=low_attack_points
        self.high_attack_points=high_attack_points

    #This shows the current info of the pokemon
    def get_info(self):
        return(f"{self.move_name} (Type: {self.elemental_type}): {self.low_attack_points} to {self.high_attack_points} Attack Points")

    #this allows for the attack value to be generated
    def generate_attack_value(self):
        randattack=random.randint(self.low_attack_points,self.high_attack_points)
        return randattack

#Pokemon Class
class Pokemon:
    def __init__(self,name,elemental_type,hit_points):
        self.name=str(name)
        self.elemental_type=str(elemental_type)
        self.hit_points=int(hit_points)
        self.list_of_moves = []

    #This gets the info for the pokemon type
    def get_info(self):
        return(f"{self.name} - Type: {self.elemental_type} - Hit Points: {self.hit_points}")

    #this is how the pokemon can heal themselves
    def heal(self):
        self.hit_points = self.hit_points + 15
        print(f"\n{self.name} has been healed to {self.hit_points} hit points.\n")
        return

    #this displays the choices
    def display_choices(self):
        print("Your options: ")
        for index, move in enumerate(self.list_of_moves, start = 1):
            print(f"{index}: {move.get_info()}")
        print (f"H: Heal 15 hit points")

    #this allows the pokemon to attack
    def attack(self, move_index, opposing_pokemon):
        self.move_index = move_index
        move = self.list_of_moves[int(move_index) - 1]
        damage_taken = move.generate_attack_value()
        rounded_number = round(damage_taken,1)
        output_message = ""
        if (move.elemental_type == "Grass" and opposing_pokemon.elemental_type == "Water") or (move.elemental_type == "Water" and opposing_pokemon.elemental_type == "Fire") or (move.elemental_type == "Fire" and opposing_pokemon.elemental_type == "Grass"):
            multiplier = 2
            output_message = f"It's super effective!"
        elif (move.elemental_type == "Water" and opposing_pokemon.elemental_type == "Grass") or (move.elemental_type == "Fire" and opposing_pokemon.elemental_type == "Water") or (move.elemental_type == "Grass" and opposing_pokemon.elemental_type == "Fire"):
            multiplier = .5
            output_message = f"It's not very effective…"
        else:
            multiplier = 1
        critical_hit = random.random() < .06
        if critical_hit:
            multiplier *= 1.5
            output_message = f"Critical hit! \n{output_message}"

        #this real damage variable taken variable for matt was decided upon at 11:30 pm, it saved us lots of time
        real_taken_damage_variable_for_matt = (multiplier * rounded_number)
        opposing_pokemon.hit_points = opposing_pokemon.hit_points - real_taken_damage_variable_for_matt
        final_message = f"\n{self.name} used {move.move_name} \n{output_message}\n{opposing_pokemon.name} took {real_taken_damage_variable_for_matt} points of damage!\n"
        print (final_message)





#Moves
Tackle=Move("Tackle","Normal",5,20)
QuickAttack=Move("Quick Attack","Normal",6,25)
Slash=Move("Slash","Normal",10,30)
Flamethrower=Move("Flamethrower","Fire",5,30)
Ember=Move("Ember","Fire",10,20)
WaterGun=Move("Water Gun","Water",5,15)
HydroPump=Move("Hydro Pump","Water",20,25)
VineWhip=Move("Vine Whip","Grass",10,25)
SolarBeam=Move("Solar Beam","Grass",18,27)

#List of Moves
MoveList=[Tackle,QuickAttack,Slash,Flamethrower,Ember,WaterGun,HydroPump,VineWhip,SolarBeam]

#Pokemon
Bulbasaur=Pokemon("Bulbasaur","Grass",60)
Charmander=Pokemon("Charmander","Fire",55)
Squirtle=Pokemon("Squirtle","Water",65)

#Pokemon List
Pokedex=[Bulbasaur,Charmander,Squirtle]

#Moves Loop
def print_moves():
    print(f"These are the moves the pokemon will randomly select from:")
    for move in MoveList:
        print(f"\t{move.get_info()}")
    print()
    return


#Function to assign moves
def assign_moves():
    #loop for all pokemon
    for Pokemon in Pokedex:
        #creates a new list of the moves allowed for a specific pokemon
        selected_moves = [move for move in MoveList if move.elemental_type == Pokemon.elemental_type or move.elemental_type == "Normal"]
        first_move = random.choice(selected_moves)
        selected_moves.remove(first_move)
        second_move = random.choice(selected_moves)
        #removes the used moves from the main list so there arent repeats
        MoveList.remove(first_move)
        MoveList.remove(second_move)
        #adds the moves to the pokemons move list
        Pokemon.list_of_moves.append(first_move)
        Pokemon.list_of_moves.append(second_move)
        #prints pokemons and their moves lists
        print(f"{Pokemon.name} was assigned: ")
        #the .move_name is what makes it looks pretty
        print(f"\t {first_move.move_name}")
        print(f"\t {second_move.move_name}")
    print()



# Select your pokemon and opponent's pokemon
def choosing_my_and_opp_pokemon():
    print("Available Pokemon:")
    for index, pokemon in enumerate(Pokedex, start = 1):
        print(index, pokemon.get_info())

    selected_pokemon = int(input("Choose the # of your pokemon: "))
    print()
    my_pokemon = Pokedex[selected_pokemon - 1]
    Pokedex.remove(Pokedex[selected_pokemon - 1])
    print(f"You chose {my_pokemon.name} as your pokemon\n")

    #This prints out the options and lets you pick your pokemon
    for index, pokemon in enumerate(Pokedex, start = 1):
        print(index, pokemon.get_info())
    selected_pokemon = int(input("Choose the # of the opponent pokemon: "))
    opponent_pokemon = Pokedex[selected_pokemon - 1]
    Pokedex.remove(Pokedex[selected_pokemon - 1])
    print(f"You chose {opponent_pokemon.name} as the opponent\n")
    print()

    return(my_pokemon,opponent_pokemon)

#This starts the battle between the two pokemon
def pokemon_battle(my_pokemon,opponent_pokemon):
    print("BATTLE START!")
    print(f"{opponent_pokemon.name} wants to fight!")
    print(f"Go! {my_pokemon.name}!")
    print()

    #this is the loop that runs the battle
    while True:
        print (f"Opponent: {opponent_pokemon.get_info()}")
        print (f"You: {my_pokemon.get_info()}")
        #this print line makes the spacing look better
        print()
        my_pokemon.display_choices()
        my_selection = input("Choose an option: ")
        if my_selection == "H" or my_selection == "h":
            my_pokemon.heal()
        else:
            my_pokemon.attack(my_selection,opponent_pokemon)
        input("Press enter to proceed...")
        if opponent_pokemon.hit_points <= 0:
            print(f"\n{opponent_pokemon.name} has been defeated.\n{my_pokemon.name} has won!\n")
            break
        options = [1, 2, 'h']
        opponent_selection = random.choice(options)
        if opponent_selection == 'h':
            opponent_pokemon.heal()
        else:
            opponent_pokemon.attack(opponent_selection, my_pokemon)
        input("Press enter to proceed...")
        if my_pokemon.hit_points <= 0:
            print(f"\n{my_pokemon.name} has been defeated.\n{opponent_pokemon.name} has won!\n")
            break



#these call the methods that we defied above
print_moves()
assign_moves()
my_pokemon,opp_pokemon = choosing_my_and_opp_pokemon()
pokemon_battle(my_pokemon,opp_pokemon)
