from random import choices, shuffle
import pandas as pd
import numpy as np
import sys
import os
from time import sleep

class Club:
    goals_for = 0
    goals_against = 0
    goals_difference = 0
    won = 0
    drawn = 0
    lost = 0
    points = 0

    def __init__(self, name, rank_points, abrev):
        self.name = name
        self.rank_points = rank_points
        self.abrev = abrev.upper()

    def score(self, goals):
        self.goals_for += goals
        self.gd_update()

    def concede(self, goals):
        self.goals_against += goals
        self.gd_update()

    def gd_update(self):
        self.goals_difference = self.goals_for - self.goals_against

    def victory(self):
        self.won += 1
        self.points_update()
    
    def defeat(self):
        self.lost += 1

    def draw(self):
        self.drawn += 1
        self.points_update()

    def points_update(self):
        self.points = 3 * self.won + self.drawn

class Match:
    
    number_goals = [0,1,2,3,4,5]
    home_goals = 0
    away_goals = 0  

    def __init__(self, home, away):
        self.home = home
        self.away = away
        self.result()

    def result(self, verbose=False):

        rank_diff = self.home.rank_points - self.away.rank_points

        if rank_diff == 0:

            weights = [2.25,2,1.75,1.5,1.25,1]

            self.home_goals = choices(self.number_goals, weights)[0]
            self.away_goals = choices(self.number_goals, weights)[0]

        elif abs(rank_diff) <= 2:

            higher_rank_weights = [1, 2, 3, 3, 2, 1]
            lower_rank_weights = [2, 1.75, 1.5, 1, 0.75, 0.5]

            if self.home.rank_points > self.away.rank_points:
                self.home_goals = choices(self.number_goals, higher_rank_weights)[0]
                self.away_goals = choices(self.number_goals, lower_rank_weights)[0]

            else:
                self.away_goals = choices(self.number_goals, higher_rank_weights)[0]
                self.home_goals = choices(self.number_goals, lower_rank_weights)[0]

        else:

            higher_rank_weights = [1, 2, 4, 4, 3, 2.5]
            lower_rank_weights = [3, 2.75, 2, 1, 0.5, 0.25]

            if self.home.rank_points > self.away.rank_points:
                self.home_goals = choices(self.number_goals, higher_rank_weights)[0]
                self.away_goals = choices(self.number_goals, lower_rank_weights)[0]

            else:
                self.away_goals = choices(self.number_goals, higher_rank_weights)[0]
                self.home_goals = choices(self.number_goals, lower_rank_weights)[0]

        if self.home_goals == self.away_goals:
            self.home.draw()
            self.away.draw()

        elif self.home_goals > self.away_goals:
            self.home.victory()
            self.away.defeat()

        else:
            self.home.defeat()
            self.away.victory()

        self.home.score(self.home_goals)
        self.home.concede(self.away_goals)

        self.away.score(self.away_goals)
        self.away.concede(self.home_goals)

        if verbose:
            return (f'{self.home.get_abr()} {self.home_goals} x {self.away_goals} {self.away.get_abr()}')

class Championship:

    def __init__(self, clubs):
        self.clubs = clubs
        self.current_round = 1
        self.rounds = 2 * (len(self.clubs) - 1)
        self.set_matches_table()
        self.set_classification()

    def set_classification(self):
        self.classification = pd.DataFrame(None, columns=['Club', 'Won', 'Drawn', 'Lost', 'GF', 'GA', 'GD', 'Points'])
        
        for i in range (len(self.clubs)):

            row = [self.clubs[i].name, self.clubs[i].won, self.clubs[i].drawn, self.clubs[i].lost, self.clubs[i].goals_for, \
            self.clubs[i].goals_against, self.clubs[i].goals_difference, self.clubs[i].points]

            self.classification.loc[i] = row

        self.classification = self.classification.sort_values(by=['Points', 'Won', 'GD', 'GF', 'GA', 'Club'], \
            ascending=[False, False, False, False, True, True], ignore_index=True)

    def set_matches_table(self):
        self.table_by_club = {}
        self.matches_table = {}

        clubs = self.clubs.copy()

        for club in clubs:
            self.table_by_club[club] = []

        for i in range (2 * len(clubs) - 1):
            self.matches_table[i+1] = []

        shuffle(clubs)
        for i in range (len(clubs) - 1):
            free_clubs = clubs.copy()
            
            while len(free_clubs) > 0:
                home = free_clubs[0]
                free_clubs.remove(home)
  
                possible_away = [x for x in free_clubs if x not in self.table_by_club[home]]
            
                away = possible_away[0]
                free_clubs.remove(away)

                self.table_by_club[home].append(away)
                self.table_by_club[away].append(home)        

                match = [home, away]
                shuffle(match)

                self.matches_table[i+1].append(match)
                self.matches_table[i+len(clubs)].append([match[1], match[0]])

    def get_next_match_by_club(self, club):
        for match in self.matches_table[self.current_round]:
            if club in match:
                home = list(match)[0]
                away = list(match)[1]
        
        return f'{home.abrev} X {away.abrev}'

    def get_table_by_round(self):
        print (f'Rodada {self.current_round}:')
        for match in self.matches_table[self.current_round]:
            home = list(match)[0]
            away = list(match)[1]
            print(f'{home.abrev} X {away.abrev}')

    def play_round(self):
        print (f'Rodada {self.current_round}:')

        for match in self.matches_table[self.current_round]:
            home = list(match)[0]
            away = list(match)[1]

            partida = Match(home, away)

            print(f'{home.abrev} {partida.home_goals} X {partida.away_goals} {away.abrev}')
        
        self.current_round += 1
        self.set_classification()

    def get_classification(self):
        print(self.classification)

    def get_current_club_position(self, club):
        return self.classification.loc[self.classification['Club'] == club.name].index[0] + 1

    def get_leader(self):
        return self.classification['Club'].iloc[0]

class User:
    def __init__(self, name, club):
        self.name = name
        self.club = club

class FutSimulator:
    
    def __init__(self, path='brasileirao2020.csv'):
        self.load_championship(path)
        self.start()

    def load_championship(self, path):
        self.clubs = []

        with open(path, 'r') as br:
            for club in br:
                club = club.strip('\n').split(',')
                self.clubs.append(Club(club[0], int(club[1]), club[2]))

        self.championship = Championship(self.clubs)

    def create_user(self):
        name = str(input('Entre o nome do Técnico: '))

        print('Qual time você deseja treinar no campeonato?')

        i = 1
        for club in self.clubs:
            print(f'{i}. {club.name}')
            i += 1

        index_club = int(input('Entre o numero referente ao time: '))

        club = self.clubs[index_club - 1]
        self.user = User(name, club)

        print(f'{self.user.club.name} anuncia {self.user.name} como novo treinador.\n')
        sleep(3)

    def show_current_position(self):
        return self.championship.get_current_club_position(self.user.club)

    def show_next_match(self):
        return self.championship.get_next_match_by_club(self.user.club)

    def show_classification(self):
        self.championship.get_classification()
        sleep(5)
        self.main_menu()
    
    def show_round_games(self):
        self.championship.get_table_by_round()
        sleep(3)
        self.main_menu()

    def show_champion(self):
        return self.championship.get_leader()
     
    def play_round(self):
        self.championship.play_round()
        sleep(5)
        self.main_menu()
        
    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def final_message(self):
        if self.show_current_position() == 1:
            print(f'PARABÉNS!!!! O {self.user.club.name.upper()} É O MAIS NOVO CAMPEÃO !!!')
            print(f'O técnico {self.user.name} afirma \"Esse grupo é maravilhoso e esse título veio para coroar um trabalho muito bem feito\" ') 
        else:
            print(f'Que pena, não foi dessa vez que você foi campeão, o {self.user.club.name} ficou apenas em {self.show_current_position()}º!')
            print(f'O {self.show_champion()} foi o campeão do atual campeonato!\n')
        
        print('Classificação Final:\n')
        self.championship.get_classification()
    
    def simulate_left_games(self):
        while self.championship.current_round <= self.championship.rounds:
            self.championship.play_round()
            sleep(0.1)
            self.clear()

    def main_menu(self):

        while self.championship.current_round <= self.championship.rounds:
            self.clear()
            print(f'Time: {self.user.club.name}')
            print(f'Treinador: {self.user.name}')
            print(f'Posição Atual: {self.show_current_position()}º\n')

            print(f'Próxima partida:\n{self.show_next_match()}\n')

            print('O que deseja fazer agora?\n 1. Jogar Próxima Partida\n 2. Jogos da Rodada\n 3. Visualizar Classificação\n 4. Simular todos os jogos restantes\n 5. Sair (o jogo atual não será salvo)\n')
            choice = int(input('Entre a opção desejada:' ))

            if choice == 1:
                self.clear()
                self.play_round()
            
            elif choice == 2:
                self.clear()
                self.show_round_games()

            elif choice == 3:
                self.clear()
                self.show_classification()
            
            elif choice == 4:
                self.clear()
                self.simulate_left_games()
            else:
                quit()
        
        self.clear()
        self.final_message()
        quit()

    def start(self):
        self.create_user()
        self.main_menu()

if len(sys.argv) == 1:
    FutSimulator()
else:
    FutSimulator(sys.argv[1])
