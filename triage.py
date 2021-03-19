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


def calculate_size(p):
    x = p.toString()
    y = x.count('NumberAdvancedThisRound') + x.count('NumberAdvancedByAction') + x.count('IsNewNeutral') + x.count(
        'marker') + x.count('progress_value') + x.count('move_value') + x.count('neutrals') + x.count(
        'actions') + x.count('lambda') + x.count('map') + x.count('sum') + x.count('argmax') + x.count('+') + x.count(
        '-') + x.count('*')
    return y


class bus:
    def __init__(self):
        self.f = open("a.txt", "w")
        self.dict = {}
        self.evaluated = 0
        self.generated = 0
        self.out = set()
        self.mark = 0
        self.apporach = 0
        self.current_best_strategy = None
        self.IBR = 0

    def grow(self, plist, operation, size):
        new_plist = []
        for op in operation:
            op.grow(plist, new_plist, self.dict, size)
        for i in new_plist:
            if (i.toString() not in self.out):
                self.out.add(i.toString())
                print(i.toString(), file=self.f)
                if (size < 7):
                    x = calculate_size(i)
                    if (x in self.dict.keys()):
                        self.dict[x].append(i)
                    else:
                        self.dict[x] = []
                        self.dict[x].append(i)
                plist.append(i)

    def synthesize(self, n, operation, state, values, functions, eval, programs_not_to_eval):
        plist = []
        for i in functions:
            plist.append(i())
        plist.append(VarScalar('marker'))
        for i in values:
            plist.append(VarScalarFromArray(i))
        for i in state:
            plist.append(VarList(i))

        self.dict[1] = []
        for i in plist:
            self.dict[1].append(i)
        for i in range(n):
            print(i)
            print(i, file=self.f)
            print(len(plist))
            self.grow(plist, operation, i + 2)
            if (self.current_best_strategy == None):
                for j in range(self.apporach, len(plist)):
                    self.apporach += 1
                    if (isinstance(plist[j], Argmax)):
                        program_yes_no = Sum(Map(Function(Times(Plus(NumberAdvancedThisRound(), Constant(1)), VarScalarFromArray('progress_value'))),VarList('neutrals')))
                        program_decide_column = plist[j]
                        p1 = Rule_of_28_Player_PS(program_yes_no, program_decide_column)
                        p2 = Rule_of_28_Player_PS(program_yes_no, program_decide_column)
                        victories1 = 0
                        victories2 = 0
                        try:
                            victories1, victories2 = play_n_matches(p1, p2, 50)
                            print(victories1, victories2)
                            print('Player 1: ', victories1 / (victories1 + victories2))
                            print('Player 2: ', victories2 / (victories1 + victories2))
                            if ((victories1 / (victories1 + victories2)) <= .40 or (
                                    victories1 / (victories1 + victories2)) >= .60):
                                self.IBR += 1
                                self.current_best_strategy = plist[j]
                                break
                        except:
                            pass
            for j in range(self.apporach, len(plist)):
                self.apporach += 1
                if (isinstance(plist[j], Argmax)):
                    program_yes_no = Sum(Map(Function(Times(Plus(NumberAdvancedThisRound(), Constant(1)), VarScalarFromArray('progress_value'))),VarList('neutrals')))
                    p1 = Rule_of_28_Player_PS(program_yes_no, self.current_best_strategy)
                    p2 = Rule_of_28_Player_PS(program_yes_no, plist[j])
                    try:
                        victories1 = 0
                        victories2 = 0
                        victories1,victories2=play_n_matches(p1,p2,5)
                        if(victories2>=2):
                            x, y = play_n_matches(p1, p2, 95)
                            victories1+=x
                            victories2+=y
                            if((victories2 / (victories1 + victories2))>.55):
                                x, y = play_n_matches(p1, p2, 400)
                                victories1 += x
                                victories2 += y
                        print(victories1, victories2)
                        print('Player 1: ', victories1 / (victories1 + victories2))
                        print('Player 2: ', victories2 / (victories1 + victories2))
                        print("IBR", self.IBR)
                        if ( (victories2 / (victories1 + victories2))>=.55):
                            self.IBR += 1
                            self.current_best_strategy = plist[j]
                            if (self.IBR == 6):
                                return self.current_best_strategy
                    except:
                        pass


if __name__ == "__main__":
    start = time.time()
    b = bus()
    my_prog = b.synthesize(10, [Sum, Map, Argmax, Function, Plus, Times, Minus], ['neutrals', 'actions'],
                           ['progress_value', 'move_value'],
                           [NumberAdvancedThisRound, NumberAdvancedByAction, IsNewNeutral], 5, 10)
    print("Best strategy:", my_prog.toString())

    program_yes_no = Sum(
        Map(Function(Times(Plus(NumberAdvancedThisRound(), Constant(1)), VarScalarFromArray('progress_value'))),
            VarList('neutrals')))
    program_decide_column = Argmax(Map(Function(Sum(Map(Function(
        Minus(Times(NumberAdvancedByAction(), VarScalarFromArray('move_value')),
              Times(VarScalar('marker'), IsNewNeutral()))), None))), VarList('actions')))
    print(program_decide_column.toString())
    # p1 = RandomPlayer()
    p1 = Rule_of_28_Player_PS(program_yes_no, b.current_best_strategy)
    p2 = Rule_of_28_Player_PS(program_yes_no, program_decide_column)
    victories1 = 0
    victories2 = 0

    victories1, victories2 = play_n_matches(p1, p2, 500)

    end = time.time()
    print(victories1, victories2)
    print('Player 1: ', victories1 / (victories1 + victories2))
    print('Player 2: ', victories2 / (victories1 + victories2))
    print(end - start, ' seconds')
