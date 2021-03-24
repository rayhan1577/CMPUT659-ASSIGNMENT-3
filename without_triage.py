import random
import time
from game import Game
from random_player import RandomPlayer
from rule_of_28_sketch import Rule_of_28_Player_PS
from DSL import *



def play_match(p1, p2):
    game = Game(n_players=2, dice_number=4, dice_value=6, column_range=[2, 12],
                offset=2, initial_height=3)

    is_over = False
    who_won = None

    number_of_moves = 0
    current_player = game.player_turn
    while not is_over:
        moves = game.available_moves()
        if game.is_player_busted(moves):
            if current_player == 1:
                current_player = 2
            else:
                current_player = 1
            continue
        else:
            if game.player_turn == 1:
                chosen_play = p1.get_action(game)
            else:
                chosen_play = p2.get_action(game)
            if chosen_play == 'n':
                if current_player == 1:
                    current_player = 2
                else:
                    current_player = 1
            game.play(chosen_play)
            number_of_moves += 1
        who_won, is_over = game.is_finished()

        if is_over:
            return is_over, who_won

        if number_of_moves >= 300:
            print('Draw!')
            return False, None


def play_n_matches(p1, p2, n):
    p1_victories = 0
    p2_victories = 0

    for _ in range(n):
        # plays a match with br as player 1
        finished, who_won = play_match(p1, p2)

        if finished:
            if who_won == 1:
                p1_victories += 1
            else:
                p2_victories += 1

        # plays another match with br as player 2
        finished, who_won = play_match(p2, p1)

        if finished:
            if who_won == 1:
                p2_victories += 1
            else:
                p1_victories += 1

    return p1_victories, p2_victories




class bus:
    def __init__(self):
        self.f = open("a.txt", "w")
        self.out = set()
        self.current_best_strategy = None
        self.IBR = 0
        self.prog_generated=5
        self.prog_eval=0
        self.my_program =None

    def grow(self, plist, operation, size):
        new_plist = []
        temp=[]
        for op in operation:
            op.grow(plist, new_plist,size,)
        for i in new_plist:

            if (i.toString() not in self.out):
                self.out.add(i.toString())
                self.prog_generated += 1
                if(isinstance(i,Argmax)):
                    temp.append(i)
                print(i.toString(), file=self.f)
                plist.append(i)
        for i in temp:
            self.prog_eval += 1
            if (self.current_best_strategy == None):
                program_yes_no = Sum(Map(Function(Times(Plus(NumberAdvancedThisRound(), Constant(1)), VarScalarFromArray('progress_value'))),VarList('neutrals')))
                program_decide_column = i
                p1 = Rule_of_28_Player_PS(program_yes_no, program_decide_column)
                p2 = Rule_of_28_Player_PS(program_yes_no, program_decide_column)
                victories1 = 0
                victories2 = 0
                try:
                    victories1, victories2 = play_n_matches(p1, p2, 50)
                    print(victories1, victories2)
                    print('Player 1: ', victories1 / (victories1 + victories2))
                    print('Player 2: ', victories2 / (victories1 + victories2))
                    print("First strategy: ", i.toString())
                    self.current_best_strategy = i

                except:
                    pass

            else:
                program_yes_no = Sum(Map(Function(Times(Plus(NumberAdvancedThisRound(), Constant(1)), VarScalarFromArray('progress_value'))),VarList('neutrals')))
                p1 = Rule_of_28_Player_PS(program_yes_no, self.current_best_strategy)
                p2 = Rule_of_28_Player_PS(program_yes_no, i)
                try:
                    victories1 = 0
                    victories2 = 0
                    victories1, victories2 = play_n_matches(p1, p2, 500)

                    if (victories2 / (victories1 + victories2)>= .5 and (victories1 + victories2)>500):
                        self.current_best_strategy = i
                        self.IBR += 1
                        print("New strategy found!!!!!!!!!!!!!!!!")
                        if (self.IBR == 5):
                            return
                except:
                    pass

    def synthesize(self, n, operation, state, values, functions, eval, programs_not_to_eval):
        plist = []
        for i in functions:
            plist.append(i())
        #plist.append(VarScalar('marker'))
        for i in values:
            plist.append(VarScalarFromArray(i))
        for i in state:
            plist.append(VarList(i))

        for i in range(n):
            self.grow(plist, operation, i+1 )
            #print(i+1)
            print(i+1, file=self.f)
            #print(len(plist))
            if(self.IBR==5):
                return




if __name__ == "__main__":
    start = time.time()
    b = bus()
    b.synthesize(10, [Sum, Map, Argmax, Function,  Times], ['neutrals', 'actions'],['progress_value', 'move_value'],[NumberAdvancedThisRound, NumberAdvancedByAction, IsNewNeutral], 5, 10)
    print("Best strategy:", b.current_best_strategy.toString())

    program_yes_no = Sum(
        Map(Function(Times(Plus(NumberAdvancedThisRound(), Constant(1)), VarScalarFromArray('progress_value'))),
            VarList('neutrals')))
    program_decide_column = Argmax(Map(Function(Sum(Map(Function(
        Minus(Times(NumberAdvancedByAction(), VarScalarFromArray('move_value')),
              Times(VarScalar('marker'), IsNewNeutral()))), None))), VarList('actions')))
    #print(program_decide_column.toString())
    # p1 = RandomPlayer()
    p1 = Rule_of_28_Player_PS(program_yes_no, b.current_best_strategy)
    p2 = RandomPlayer()
    victories1 = 0
    victories2 = 0
    victories1, victories2 = play_n_matches(p1, p2, 500)
    print(victories1, victories2)
    print("with Random player")
    print('My program:   ', victories1 / (victories1 + victories2))
    print('Random player', victories2 / (victories1 + victories2))

    print("##################################")

    p1 = Rule_of_28_Player_PS(program_yes_no, b.current_best_strategy)
    p2 = Rule_of_28_Player_PS(program_yes_no, program_decide_column)
    victories1 = 0
    victories2 = 0
    victories1, victories2 = play_n_matches(p1, p2, 500)
    print(victories1, victories2)
    print("with given program")
    print('My program:  ', victories1 / (victories1 + victories2))
    print('Given Program:', victories2 / (victories1 + victories2))


    print("##################################")


    print("Generated Program: ",b.prog_generated)
    print("Evaluated program: ",b.prog_eval)
    end = time.time()
    print(end - start, ' seconds')
