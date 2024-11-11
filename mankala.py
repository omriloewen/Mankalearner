import pygame
import sys
import time
import copy
import pickle
import random
import numpy as np


class MancalaGame:

    def __init__(self):
        # initialize the game default parameters
        self.board = [0] + [4] * 6 + [0] + [4] * 6
        self.difficulty = None
        self.current_player = None  # currnent_player = True if the player is th current player and False if the cumputer is
        self.game_over = False
        self.extra_turn = False

        # seting the messeges the can be dispalyed, False value means its off
        self.messeges = {
            "you got another turn": False,
            "I got another turn": False,
            "my turn": False,
            "your turn": False,
            "thinking": False,
            "Invalid selection": False,
        }
        self.mesg_arr = [  # seting the location for each mesege
            ("you got another turn", 450, 0),
            ("I got another turn", 450, 0),
            ("my turn", 300, 0),
            ("your turn", 300, 0),
            ("thinking", 100, 0),
            ("Invalid selection", 60, 0),
        ]

        # intialize the game agent - choosing moves and learning
        self.Q_agent = Mancala_Q_learner()

        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((800, 400))
        pygame.display.set_caption("Mancala Game")
        self.font = pygame.font.Font(None, 36)

        self.main_menu()  # start the game with the main menu

    def main_menu(self):
        """
        display the start menu. set the game parammeters by the player choices.
        when finished, starting the main game loop.
        """
        menu_running = True  # running, parameters weren chosen yet
        # seting the buttons name, shape and loacation.
        buttons = {
            "easy": pygame.Rect(100, 100, 150, 50),
            "medium": pygame.Rect(300, 100, 150, 50),
            "hard": pygame.Rect(500, 100, 150, 50),
            "player": pygame.Rect(100, 200, 150, 50),
            "computer": pygame.Rect(300, 200, 150, 50),
            "start": pygame.Rect(500, 300, 150, 50),
        }

        while menu_running:  # while the parameters havnt set yet
            # choosing parameters
            mouse_pos = pygame.mouse.get_pos()  # save the mous position
            for event in pygame.event.get():  # go over the events happening right now
                if event.type == pygame.QUIT:  # quiting
                    pygame.quit()
                    sys.exit()
                elif (
                    event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                ):  # left click has acured
                    for key, rect in buttons.items():  # go over the buttons
                        if rect.collidepoint(
                            mouse_pos
                        ):  # check if the click was on the current button
                            # check on wich button the click was and set the parameter acordingly
                            if key in {"easy", "medium", "hard"}:
                                self.difficulty = key
                            elif key in {"player", "computer"}:
                                self.current_player = key

                            elif (
                                key == "start"
                                and self.difficulty
                                and self.current_player
                            ):  # if the click was on "start" button and the parameters are set
                                menu_running = False  # you can stop running the menu
                                # set the relevnt boolen value of the currnet player
                                if self.current_player == "player":
                                    self.current_player = True
                                else:
                                    self.current_player = False
                                self.main_loop()  # start the game
            # display
            self.screen.fill((255, 255, 255))
            for key, rect in buttons.items():  # go over the buttons
                color = (
                    (170, 170, 170) if rect.collidepoint(mouse_pos) else (200, 200, 200)
                )  # set default, or slightly highlight color if the mouse is on top the button
                if (
                    self.difficulty == key or self.current_player == key
                ):  # if the button was already chosen
                    color = (
                        100,
                        200,
                        100,
                    )  # set its color green to Highlight the one chosen
                # draw the button
                pygame.draw.rect(self.screen, color, rect)
                self.draw_text(key.capitalize(), rect.x + 20, rect.y + 10)

            pygame.display.flip()  # update display

    def main_loop(self):
        selected_pit = None
        while not self.check_if_over(self.board):

            # go over the event happening righ now
            events = pygame.event.get()
            if events == None:
                events = [None]

            for event in events:

                if event.type == pygame.QUIT:  # quiting
                    pygame.quit()
                    sys.exit()

                elif self.current_player:  # its the player turn
                    self.display_mesege("your turn")

                    if self.extra_turn:  # check if its an extar turn
                        self.display_mesege("your turn", "you got another turn")

                    if (
                        event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                    ):  # Left click
                        selected_pit = self.handle_click(
                            pygame.mouse.get_pos()
                        )  # get the pit clicked
                        # if the click was valid
                        if selected_pit is not None and self.board[selected_pit] != 0:
                            self.player_move(selected_pit)  # do the player move

                        else:
                            self.display_mesege(
                                "Invalid selection", "your turn"
                            )  # let the player know

                elif not self.current_player:  # its the computer turn
                    self.display_mesege("my turn")

                    if self.extra_turn:  # check if its an extra turn
                        self.display_mesege("my turn", "I got another turn")

                    time.sleep(0.3)  # just for smother interface
                    self.computer_move()  # do the computer move

            self.screen.fill((255, 255, 255))  # white background
            self.display_board()

        self.Q_agent.save_q_dict()  # save the data colected before exiting
        self.finish_screen(self.board[7], self.board[0])  # display the game conclusion

    def display_board(self):
        """
        drawing the game elements to the screen.
        updatind the display according to the board status and the meseges to show.
        seting the location of the player pits for player choosing input.
        """
        # Define colors
        board_color = (153, 102, 51)  # A nice wood color
        pit_color = (128, 128, 128)  # Gray pits
        stone_color = (200, 0, 50)  # smoth red
        black = (0, 0, 0)

        # Draw the board
        pygame.draw.rect(self.screen, board_color, pygame.Rect(50, 50, 700, 300))
        pygame.draw.rect(self.screen, stone_color, pygame.Rect(50, 0, 700, 45))

        # set the pits and stores structure and location
        pit_x_start = 80  # pits horizontal location
        pit_y_top = 100  # top pits vertical location
        pit_y_bottom = 230  # bttm pits vertical loaction
        pit_width = 80
        pit_height = 80
        stone_radius = 10

        # Draw stores
        pygame.draw.ellipse(
            self.screen, pit_color, pygame.Rect(50, 100, pit_width, 200)
        )
        self.draw_text(
            str(self.board[0]), 85, 290, stone_color
        )  # draw stone number in computer store
        pygame.draw.ellipse(
            self.screen, pit_color, pygame.Rect(670, 100, pit_width, 200)
        )
        self.draw_text(
            str(self.board[7]), 705, 290, stone_color
        )  # draw stone number in player store

        self.pits = []  # intialize the pits list for future player input

        # Draw the pits and add to the list
        for i in range(1, 7):
            rect_top = pygame.Rect(
                pit_x_start + 80 * i, pit_y_top, pit_width, pit_height
            )
            self.pits.append(rect_top)  # saving the top (player) pits
            pygame.draw.ellipse(self.screen, pit_color, rect_top)
            self.draw_text(
                str(self.board[i]),
                pit_x_start + 80 * i + 30,
                pit_y_top + 65,
                stone_color,
            )  # draw stone number in top pits
        # self.pits.append(None) #for future two player mode feature

        for i in range(6, 0, -1):
            rect_bottom = pygame.Rect(
                pit_x_start + 80 * i, pit_y_bottom, pit_width, pit_height
            )
            # self.pits.append(rect_bottom)  # for future two player mode feature
            pygame.draw.ellipse(self.screen, pit_color, rect_bottom)
            self.draw_text(
                str(self.board[14 - i]),
                pit_x_start + 80 * i + 30,
                pit_y_bottom + 65,
                stone_color,
            )  # draw stone number in bttm pits

        # Draw stones in each pit
        for i, stones in enumerate(self.board):  # for every pit
            # claculate the stones loaction
            pit_x = pit_x_start + 80 * (i if i < 7 else -i + 14)  # horizontal
            pit_y = pit_y_top if i < 7 else pit_y_bottom  # vertical
            if i == 0 or i == 7:  # stones in the stores
                pit_x = 50 if i == 0 else 670
                pit_y = 100
            # draw the stones in the pit
            for j in range(stones):
                pygame.draw.circle(
                    self.screen,
                    stone_color,
                    (
                        pit_x + stone_radius * 2 + (j % 3) * stone_radius,
                        pit_y + stone_radius + (j // 3) * stone_radius,
                    ),
                    stone_radius,
                    0,
                )
                pygame.draw.circle(
                    self.screen,
                    black,
                    (
                        pit_x + stone_radius * 2 + (j % 3) * stone_radius,
                        pit_y + stone_radius + (j // 3) * stone_radius,
                    ),
                    stone_radius,
                    1,
                )

        # drowing the game directions
        self.draw_text("player pits -->", 500, 60, pit_color)
        self.draw_text("<-- computer pits", 100, 320, pit_color)

        # drowing the messeges wich are "on"
        for mesg in self.mesg_arr:
            if self.messeges[mesg[0]]:
                self.draw_text(mesg[0], mesg[1], mesg[2])

        pygame.display.flip()  # updating the dislay

    def display_mesege(self, *args):
        """
        switchin "on" the given masegges, "off" the not guven ones,
        and displaying the screen with those meseges.
        only the given messeges will show after aplying the method.

        parameters:
        args(str): the text meseges from the default ones to show.
        """
        for mesg in self.mesg_arr:
            if mesg[0] in args:  # switching "on" the given meseges
                self.messeges[mesg[0]] = True
            else:
                self.messeges[mesg[0]] = False  # switching "off" the not given ones
        self.display_board()  # showing the screen with the messeges

    def draw_text(self, text: str, x: int, y: int, color=(0, 0, 0)):
        """
        drawing a text mesege on the screen.

        parameters:
        text(str): the mesege to show.
        x(int): the horizontal location.
        y(int): the vertucal location
        """
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def finish_screen(self, player_score, computer_score):
        """
        displaying a screen with the game results

        parameters:
        player_score(int): number of stones in the player store
        computer_score(int): number of stones in the computer store
        """
        # יcreate the result text
        if player_score > computer_score:
            winner_text = "player won!"
        elif player_score < computer_score:
            winner_text = "computer won!"
        else:
            winner_text = "tie!"

        result_text = f"result: player{player_score}, computer {computer_score}"
        result_surface = self.font.render(result_text, True, (255, 255, 255))
        winner_surface = self.font.render(winner_text, True, (255, 255, 255))

        # drawing the text to the screen
        self.screen.fill((0, 0, 128))  # dark blue background
        self.screen.blit(result_surface, (50, 50))
        self.screen.blit(winner_surface, (50, 100))
        pygame.display.flip()

        # waiting for user action to inish desplaying the screen
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if (
                        event.key == pygame.K_ESCAPE
                    ):  # pressing esc will end the display
                        running = False

    def player_move(self, move: int):
        """
        aplying the player move acording to the selected pit and the board ststus.
        updating and displaying the board. aplying the agents' learning logic for from that move.

        parameters:
        move(int): the slected pit as a board index

        """
        state = self.Q_agent.get_state_for_player_move(
            self.board
        )  # save the board state for learning
        pit = move - 1  # save the action done as its represented in the qdict
        self.update_board(move)  # do the move
        next_state = self.Q_agent.get_state_for_player_move(
            self.board
        )  # save the board state after the move
        # calcolate the reward for learning
        if self.check_if_over(self.board):
            reward = self.board[7] - self.board[0]
        else:
            reward = 0

        self.Q_agent.update_q(state, pit, reward, next_state)  # update the agent memory

    def computer_move(self):
        """
        chosing and aplying the player move acording to the board ststus.
        updating and displaying the board. aplying the agents' learning logic for from that move.
        """
        # agent choosing move
        pit = self.Q_agent.choose_pit(self.board)
        # pit = self.calc_move()
        while self.board[pit] == 0 and not self.check_if_over(
            self.board
        ):  # making sure its a valid move
            pit = self.Q_agent.choose_pit(self.board)
            # pit = self.calc_move()

        state = self.Q_agent.get_state(self.board)  # save the board state for learning
        self.update_board(pit)  # do the move
        next_state = self.Q_agent.get_state(
            self.board
        )  # save the board state after the move
        # calcolate the reward for learning
        if self.check_if_over(self.board):
            reward = self.board[0] - self.board[7]
            if reward > 0:
                reward += 8
            elif reward < 0:
                reward -= 8
            else:
                reward = -5
        else:
            reward = 0

        self.Q_agent.update_q(
            state, pit - 8, reward, next_state
        )  # update the agent memory

    def update_board(self, selected: int):
        """
        updating the game board according to the game logic.
        switching the currnt player according to the rules.
        displaying the board changes.

        parapmeters:
        selected(int): the selected pit as a board index
        """

        # take the stones out of the selected pit
        stones = self.board[selected]
        self.board[selected] = 0
        self.display_board()
        # spray the stones according to the game logic
        c = selected
        i = 0
        while i < stones:
            c = (selected + 1 + i) % 14  # compute the board index to put the stone in
            # skip the oponent pit and make sure u not missing any stones
            if (self.current_player and c == 0) or (
                (not self.current_player) and c == 7
            ):
                stones += 1
                i += 1
                continue
            # put the stone in the pit
            self.board[c] += 1
            i += 1
            # show it
            self.display_board()
            time.sleep(0.3)  # just for smother interface

        # the last stone was put in an empty pit
        if self.board[c] == 1 and c != 0 and c != 7:
            j = 14 - c  # calculating the oposite pit
            tmp = self.board[j]
            # if it is in the current player side, empty the oposite pit and the current pit, and add to the player pit
            if self.current_player and c < 7:
                self.board[c] = 0
                self.board[j] = 0
                self.board[7] += tmp + 1
            elif not self.current_player and c > 7:
                self.board[c] = 0
                self.board[j] = 0
                self.board[0] += tmp + 1

        # it was the last move
        if self.check_if_over(self.board):
            left_stones = 0
            for i in range(1, 14):  # go over the pits
                if i != 7:
                    # colect the left stones
                    left_stones += self.board[i]
                    self.board[i] = 0
            # add to the current player store
            if self.current_player:
                self.board[7] += left_stones
            else:
                self.board[0] += left_stones

        # the last stone was put in the current player pit
        if c == 7 or c == 0:
            self.extra_turn = True  # got an extrae turn
        else:  # anyway else switch the turn to the other player
            self.current_player = not self.current_player
            self.extra_turn = False

        time.sleep(0.3)  # just for smother interface
        self.display_board()  # show it
        time.sleep(0.3)

    def handle_click(self, position):
        """
        handle the click done to check if it hit a valid pit and wich pit.

        parameters:
        position: the mouse position when the click acured

        returns:
        the the chosen pit matching board index if the click was on valid location,
        None otherwise
        """
        for index, rect in enumerate(self.pits):  # gon over the valid pits
            if rect != None and rect.collidepoint(
                position
            ):  # if the click was on this pit location
                return index + 1  # returns the chosen pit matching board index
        return None  # None if the click wasnt on any valid pits

    def check_if_over(self, board):
        """
        check if the game ended acording to the rules

        returns:
        True if the gmae is over, False otherwise
        """

        top_over = True
        bttm_over = True  # at the start asume both over

        for i in range(1, 7):  # go over the top pits
            if board[i] != 0:  # check if its not empty
                top_over = False  # if so its not over
                break

        for i in range(8, 14):  # go over the bttm pits
            if board[i] != 0:  # check if its not empty
                bttm_over = False  # if so its not over
                break

        return top_over or bttm_over  # game done if one or both are done

    def calc_move(self, player=False):
        """
        claculating a move for the computer/player acording to the board stsus with a basic strategy -
          if there any move that will give another turn, do it,
          if no such move, do the move wich will add the most stones to the store.

          returns:
          the best move, acording to the stategy, matching board index
        """
        best_score = -1
        extra_turn_move = None
        best_score_move = None
        start_pit = 1 if player else 8  # pick the pits to check

        for i in range(start_pit, start_pit + 6):  # go over the checked player pits
            if self.board[i] > 0:  # if the pit is not empty
                temp_board = copy.deepcopy(self.board)  # make a board copy
                score, extra_turn_given, finished_game = self.update_board_copy(
                    temp_board, i, player
                )  # make the move and check the results
                if finished_game:  # if its finished the game just do it
                    return i
                if extra_turn_given:
                    extra_turn_move = i
                if score > best_score:
                    best_score_move = i

        if extra_turn_move != None:  # we prfer getin an extra turn
            return extra_turn_move

        return best_score_move  # but also the best score will be ok

    def update_board_copy(self, board, selected, player):
        """
        do the move given on the board copy given, and returns the result of the move
        returns: the checked player score after the move, wether it ended the game, wether it given an extra turn
        """
        finished_game = False
        extra_move_given = False

        # take the stones out of the selected pit
        stones = board[selected]
        board[selected] = 0

        # spray the stones according to the game logic
        i = 0
        c = selected
        while i < stones:
            c = (selected + 1 + i) % 14  # compute the board index to put the stone in
            # skip the oponent pit and make sure u not missing any stones
            if (player and c == 0) or ((not player) and c == 7):
                stones += 1
                i += 1
                continue
            # put the stone in the pit
            board[c] += 1
            i += 1

        # the last stone was put in an empty pit
        if board[c] == 1 and c != 0 and c != 7:
            j = 14 - c  # calculating the oposite pit
            tmp = board[j]
            # if it is in the current player side, empty the oposite pit and the current pit, and add to the player pit
            if player and c < 7:
                self.board[c] = 0
                self.board[j] = 0
                self.board[7] += tmp + 1
            elif not player and c > 7:
                self.board[c] = 0
                self.board[j] = 0
                self.board[0] += tmp + 1

        # it was the last move
        if self.check_if_over(board):
            finished_game = True

        # the last stone was put in the current player pit
        if c == 7 or c == 0:
            extra_move_given = True  # got an extrae turn

        score = board[7] if player else board[0]

        return score, finished_game, extra_move_given


class Mancala_Q_learner:

    def __init__(self, load_existing=True, filename="q_dict.pkl", a=0.9, g=0.9, e=0.1):
        # initialize the learner parameters
        self.num_pits = 6
        self.a = a
        self.g = g
        self.e = e

        # load exicting dict
        self.filename = filename
        if load_existing:
            self.Q = self.load_q_dict()
        else:
            self.Q = {}

    def load_q_dict(self):
        try:
            with open(self.filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return {}

    def save_q_dict(self):
        with open(self.filename, "wb") as f:
            pickle.dump(self.Q, f)

    def get_state(self, board):
        """
        take a board and trnsfer it to a state that can be a dictionry key, ignores the stores status for it should not make a difrence

        returns: the state as a tuple
        """
        return tuple([board[i] for i in range(14) if i != 0 and i != 7])

    def get_state_for_player_move(self, board):
        """
        take a board at the player turn and transfer it to a state the agent can learn from, ignoring the stores and twisting it to be like cumputer state
        """
        return tuple([board[(i + 7) % 14] for i in range(1, 14) if i != 7])

    def choose_pit(self, board):
        """
        choose an action acording to th exploit - explor protocol, from the q dict.
        it returns the matching index in the game board
        """
        state = self.get_state(board)

        if (
            random.uniform(0, 1) < self.e or state not in self.Q
        ):  # explore or if we havnt seen the state before
            return random.randint(0, self.num_pits - 1) + 8
        else:
            return (
                np.argmax(self.Q[state]) + 8
            )  # exploit and add 8 to match the board index

    def update_q(self, state, pit, reward, next_state):
        """
        updating the q dictionary acording to the furmula after making a move
        """
        if state not in self.Q:
            self.Q[state] = np.zeros(self.num_pits)  # add zeros if we havnt seen it yet
        if next_state not in self.Q:
            self.Q[next_state] = np.zeros(self.num_pits)
        # calculate the furmula and update the dictionary
        max_future = np.max(self.Q[next_state])
        curr = self.Q[state][pit]
        new = curr + self.a * (reward + self.g * max_future - curr)
        self.Q[state][pit] = new


class MancalaGame_trainer:

    def __init__(self, num_episodes=1000):
        # initialize the game default parameters
        self.board = [0, 4, 4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 4]
        self.difficulty = None
        self.current_player = False  # currnent_player = True if the player is th current player and False if the cumputer is
        self.extra_turn = False
        self.num_episodes = num_episodes

        # intialize the game agent - choosing moves and learning
        self.Q_agent = Mancala_Q_learner()
        self.main_loop()

    def main_loop(self):
        # print("main loop")

        for episode in range(self.num_episodes):
            if random.uniform(0, 1) < 0.1:
                self.current_player = True
            else:
                self.current_player = False

            while not self.check_if_over(self.board):

                if self.current_player:  # its the player turn
                    self.player_move()  # do the player move

                else:  # its the computer turn
                    self.computer_move()  # do the computer move

            self.Q_agent.save_q_dict()  # save the data colected before exiting

    def player_move(self):
        """
        aplying the player move acording to the board ststus.
        updating the board. aplying the agents' learning logic for from that move.

        """
        # print("player move")
        move = self.calc_move(True)  # calculate the move for the player
        state = self.Q_agent.get_state_for_player_move(
            self.board
        )  # save the board state for learning
        pit = move - 1  # save the action done as its represented in the qdict
        org_score = self.board[7]
        self.update_board(move)  # do the move
        next_state = self.Q_agent.get_state_for_player_move(
            self.board
        )  # save the board state after the move
        # calcolate the reward for learning
        reward = self.board[7] - org_score
        if self.check_if_over(self.board):
            if self.board[7] > self.board[0]:
                reward += 10
            else:
                reward = 0

        self.Q_agent.update_q(state, pit, reward, next_state)  # update the agent memory

    def computer_move(self):
        """
        chosing and aplying the player move acording to the board ststus.
        updating the board. aplying the agents' learning logic for from that move.
        """
        # print("comp move")
        # agent choosing move
        pit = self.Q_agent.choose_pit(self.board)
        # pit = self.calc_move()
        while self.board[pit] == 0 and not self.check_if_over(
            self.board
        ):  # making sure its a valid move
            pit = self.Q_agent.choose_pit(self.board)
            # pit = self.calc_move()
        org_score = self.board[0]
        state = self.Q_agent.get_state(self.board)  # save the board state for learning
        self.update_board(pit)  # do the move
        next_state = self.Q_agent.get_state(
            self.board
        )  # save the board state after the move
        # calcolate the reward for learning

        reward = self.board[0] - org_score
        if self.check_if_over(self.board):
            if self.board[0] > self.board[7]:
                reward += 10
            else:
                reward = 0
        else:
            reward = 0

        self.Q_agent.update_q(
            state, pit - 8, reward, next_state
        )  # update the agent memory

    def update_board(self, selected: int):
        """
        updating the game board according to the game logic.
        switching the currnt player according to the rules.

        parapmeters:
        selected(int): the selected pit as a board index
        """
        # print("update board")
        # take the stones out of the selected pit
        stones = self.board[selected]
        self.board[selected] = 0
        # spray the stones according to the game logic
        i = 0
        while i < stones:
            c = (selected + 1 + i) % 14  # compute the board index to put the stone in
            # skip the oponent pit and make sure u not missing any stones
            if (self.current_player and c == 0) or (
                (not self.current_player) and c == 7
            ):
                stones += 1
                i += 1
                continue
            # put the stone in the pit
            self.board[c] += 1
            i += 1

        # the last stone was put in an empty pit
        if self.board[c] == 1 and c != 0 and c != 7:
            j = 14 - c  # calculating the oposite pit
            tmp = self.board[j]
            # if it is in the current player side, empty the oposite pit and the current pit, and add to the player pit
            if self.current_player and c < 7:
                self.board[c] = 0
                self.board[j] = 0
                self.board[7] += tmp + 1
            elif not self.current_player and c > 7:
                self.board[c] = 0
                self.board[j] = 0
                self.board[0] += tmp + 1

        # it was the last move
        if self.check_if_over(self.board):
            left_stones = 0
            for i in range(1, 14):  # go over the pits
                if i != 7:
                    # colect the left stones
                    left_stones += self.board[i]
                    self.board[i] = 0
            # add to the current player store
            if self.current_player:
                self.board[7] += left_stones
            else:
                self.board[0] += left_stones

        # the last stone was put in the current player pit
        if c == 7 or c == 0:
            self.extra_turn = True  # got an extrae turn
        else:  # anyway else switch the turn to the other player
            self.current_player = not self.current_player
            self.extra_turn = False

    def check_if_over(self, board):
        """
        check if the game ended acording to the rules

        returns:
        True if the gmae is over, False otherwise
        """
        # print("check over")
        top_over = True
        bttm_over = True  # at the start asume both over

        for i in range(1, 7):  # go over the top pits
            if board[i] != 0:  # check if its not empty
                top_over = False  # if so its not over
                break

        for i in range(8, 14):  # go over the bttm pits
            if board[i] != 0:  # check if its not empty
                bttm_over = False  # if so its not over
                break

        return top_over or bttm_over  # game done if one or both are done

    def calc_move(self, player=False):
        """
        claculating a move for the computer/player acording to the board stsus with a basic strategy -
          if there any move that will give another turn, do it,
          if no such move, do the move wich will add the most stones to the store.

          returns:
          the best move, acording to the stategy, matching board index
        """
        # print("calc move")
        best_score = -1
        extra_turn_move = None
        best_score_move = None
        start_pit = 1 if player else 8  # pick the pits to check

        for i in range(start_pit, start_pit + 6):  # go over the checked player pits
            if self.board[i] > 0:  # if the pit is not empty
                temp_board = copy.deepcopy(self.board)  # make a board copy
                score, extra_turn_given, finished_game = self.update_board_copy(
                    temp_board, i, player
                )  # make the move and check the results
                if finished_game:  # if its finished the game just do it
                    return i
                if extra_turn_given:
                    extra_turn_move = i
                if score > best_score:
                    best_score_move = i

        if extra_turn_move != None:  # we prfer getin an extra turn
            return extra_turn_move

        return best_score_move  # but also the best score will be ok

    def update_board_copy(self, board, selected, player):
        """
        do the move given on the board copy given, and returns the result of the move
        returns: the checked player score after the move, wether it ended the game, wether it given an extra turn
        """
        finished_game = False
        extra_move_given = False

        # take the stones out of the selected pit
        stones = board[selected]
        board[selected] = 0

        # spray the stones according to the game logic
        i = 0
        c = selected
        while i < stones:
            c = (selected + 1 + i) % 14  # compute the board index to put the stone in
            # skip the oponent pit and make sure u not missing any stones
            if (player and c == 0) or ((not player) and c == 7):
                stones += 1
                i += 1
                continue
            # put the stone in the pit
            board[c] += 1
            i += 1

        # the last stone was put in an empty pit
        if board[c] == 1 and c != 0 and c != 7:
            j = 14 - c  # calculating the oposite pit
            tmp = board[j]
            # if it is in the current player side, empty the oposite pit and the current pit, and add to the player pit
            if player and c < 7:
                self.board[c] = 0
                self.board[j] = 0
                self.board[7] += tmp + 1
            elif not player and c > 7:
                self.board[c] = 0
                self.board[j] = 0
                self.board[0] += tmp + 1

        # it was the last move
        if self.check_if_over(board):
            finished_game = True

        # the last stone was put in the current player pit
        if c == 7 or c == 0:
            extra_move_given = True  # got an extrae turn

        score = board[7] if player else board[0]

        return score, finished_game, extra_move_given


if __name__ == "__main__":
    # trainer = MancalaGame_trainer(2100)

    game = MancalaGame()
    #ql = Mancala_Q_learner()s

    # ql.Q = {}
    # ql.save_q_dict()
    # ql = Mancala_Q_learner()
    #print(ql.Q[(0, 0, 3, 0, 0, 0, 2, 1, 0, 0, 0, 0)])
