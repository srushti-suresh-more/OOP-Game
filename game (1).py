import tkinter
import random
from itertools import permutations

class Player:
    
    
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.selected_sq = set()

class Board:
    

    def __init__(self, parent, sq_size, color):
        self.parent = parent   # parent is root
        self.sq_size = sq_size
        self.color = color

        self._winning_combos = [{1, 2, 3}, {4, 5, 6}, {7, 8, 9},
                      {1, 4, 7}, {2, 5, 8}, {3, 6, 9},
                      {1, 5, 9}, {3, 5, 7}]

       
        self.unused_squares_dict = { '00': 1, '10': 2, '20': 3,
                                     '01': 4, '11': 5, '21': 6,
                                     '02': 7, '12': 8, '22': 9  }

        
        self.container = tkinter.Frame(self.parent)
        self.container.pack()

        
        self.canvas = tkinter.Canvas(self.container,
                                     width= self.sq_size * 3,
                                     height= self.sq_size * 3)
        
        self.canvas.grid()

    def get_unused_squares_dict(self):
        return self.unused_squares_dict

    def reset_unused_squares_dict(self):
        self.unused_squares_dict = { '00': 1, '10': 2, '20': 3,
                                     '01': 4, '11': 5, '21': 6,
                                     '02': 7, '12': 8, '22': 9  }

    def draw_board(self):
        for row in range(3):
            for column in range(3):
                self.canvas.create_rectangle(self.sq_size  * column,
                                        self.sq_size  * row,
                                        self.sq_size  * (column + 1),
                                        self.sq_size  * (row + 1),
                                        fill = self.color)

    def get_row_col(self, evt):
        # get the row and col from event's x and y coords
        return evt.x, evt.y

    def exact_cod(self, col, rw):
        
        col_flr = col // self.sq_size
        rw_flr = rw // self.sq_size
        return col_flr, rw_flr

    def convert_to_key(self, col_floor, row_floor):
        # turn col and row's quotient into a string for the key
        return str(col_floor) + str(row_floor)

    def find_coords_of_selected_sq(self, evt):
        
        # saves row and col tuple into two variables
        column, row = self.get_row_col(evt)
        # normalize for all square size by keeping the floor
        column_floor, row_floor = self.exact_cod(column, row)

        # convert to key, use key to locate position in 3x3 grid
        rowcol_key_str = self.convert_to_key(column_floor, row_floor)

        corner_column = (column_floor * self.sq_size) + self.sq_size
        corner_row =  (row_floor  * self.sq_size) + self.sq_size
        
        return corner_column, corner_row

    def color_selected_sq(self, evt, second_corner_col,
                          second_corner_row, player_color):

        self.canvas.create_rectangle(
            (evt.x // self.sq_size) * self.sq_size,
            (evt.y // self.sq_size) * self.sq_size,
            second_corner_col,
            second_corner_row,
            fill = player_color)

    @property
    def winning_combos(self):
        return self._winning_combos

class GameApp(object):
    

    def __init__(self, parent):
        self.parent = parent  

        # create a board
        self.board = Board(self.parent, 100, "white")  
        self.board.draw_board()

        self.unused_squares_dict = self.board.get_unused_squares_dict()

        # create all players instances
        self.player1 = Player("Player 1", "red") 
        self.player2 = Player("Player 2", "blue") 
        self.computer = Player("Computer", "orange") 

        self.initialize_buttons()

        self.show_menu()

    def initialize_buttons(self):
        #  --- create buttons for menu ---
        self.two_players_button = tkinter.Button(self.board.container,
                                text = "PLAY WITH A FRIEND",
                                width = 25,
                                command = self.init_two_players_game)

        
        

        self.reset_button = tkinter.Button(self.board.container,
                                           text = "RESET",
                                           width = 25,
                                           command = self.restart)
        self.exit_button = tkinter.Button(self.board.container,
                                        text = "EXIT",
                                        width = 25,
                                        command = self.init_exit_game)

    def show_menu(self):
         # register buttons to board's container
        self.two_players_button.grid()
        self.exit_button.grid()

    def init_exit_game(self):
        exit(0)

    def init_two_players_game(self):
        # reset board's unused squares
        self.board.reset_unused_squares_dict()

        # reset players' squares to empty set
        self.player1.selected_sq = set()
        self.player2.selected_sq = set()

        # keep track of turns
        self.player1_turn = True

        # show reset button
        self.reset_button.grid()

        self.board.canvas.bind("<Button-1>", self.play)

    def restart(self):
       
        self.board.container.destroy()
        # create a new board object and draw board + buttons again
        self.board = Board(self.parent, 100, "white")
        self.board.draw_board()
        self.initialize_buttons()
        self.show_menu()

    def add_to_player_sq(self, key, player_sq):
        
        current_selected_sq = self.board.unused_squares_dict[key]
        player_sq.add(current_selected_sq)   # player 1 = {1}
       

    def delete_used_sq(self, key):
        del self.board.unused_squares_dict[key]
        

    def play(self, event):
        

        # locate second column and row when player click on a square
        colrow_tuple = self.board.find_coords_of_selected_sq(event)

        # save the col and row as variable
        corner_two_col, corner_two_row = colrow_tuple[0], colrow_tuple[1]

        
        col_fl, row_fl = self.board.exact_cod(event.x, event.y)
        rowcol_key = self.board.convert_to_key(col_fl, row_fl)

        try:
            self.unused_squares_dict[rowcol_key]
        except KeyError:
            return

        if self.player1_turn == True:
            self.add_to_player_sq(rowcol_key, self.player1.selected_sq)

            # delete from game unused dictionary of set
            self.delete_used_sq(rowcol_key)

            self.board.color_selected_sq(event,
                                   corner_two_col,
                                   corner_two_row,
                                   self.player1.color)

            # check game for 3 conditions: a tie, player1 win, or player2 win
            self.check_for_winner(self.player1.selected_sq, self.player1.name)

            # switch turn
            self.player1_turn = False

        else:  # player2's turn
            self.board.color_selected_sq(event,
                                   corner_two_col,
                                   corner_two_row,
                                   self.player2.color)

            self.add_to_player_sq(rowcol_key, self.player2.selected_sq)
            self.delete_used_sq(rowcol_key)
            self.check_for_winner(self.player2.selected_sq, self.player2.name)
            self.player1_turn = True

    def check_for_winner(self, player_sq, player_name):

        if len(self.board.unused_squares_dict) >= 0:
            # if player selected at least 3 squares
            if len(player_sq) > 2:
                # start permutation of selected squares
                for combo in permutations(player_sq, 3):
                    #return all possible combinations
                    for wc in self.board.winning_combos:
                        if set(combo) == wc :
                            self.show_game_result(player_name + " WIN!")
                            self.restart

        if len(self.board.unused_squares_dict) == 0:
            self.show_game_result("OHH , IT'S A TIE. ")
            self.restart()

    def show_game_result(self, txt):
        
        result_label = tkinter.Label(self.board.container,
                                            text = txt,
                                            width = 32,
                                            height = 10,
                                            foreground = "black",
                                            background = "white",
                                            borderwidth = 3)

        result_label.grid(row = 0, column = 0)
        # unbind button so player cannot click on square
        self.board.canvas.unbind("<Button-1>", self.play)

def main():
    root = tkinter.Tk()
    root.title("Tic Tac Toe")
    tictac_game = GameApp(root)  # root is parent
    root.mainloop()

if __name__ == '__main__':
    main()