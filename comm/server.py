import random
import socket

from config import CONFIG
from core.model import Model, GameException
from utils.logs import create_logger

SERVER_SIZE = 2
LOGGER = create_logger()


class NetworkException(Exception):
    pass


class ProtocolError(Exception):
    pass


class Server:

    BUFFER_SIZE = 1024

    def __init__(self):
        self.players_addr = []
        self.model = Model()
        self.model.start_game()
        self.socket = None

    def _send_message(self, data, player_addr):
        data = data.encode('utf-8')
        self.socket.sendto(data, player_addr)

    def create_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            self.socket = s
            self.socket.bind((CONFIG['HOST'], int(CONFIG['PORT'])))

            LOGGER.info('player 0')
            data, addr_p1 = s.recvfrom(1024)
            LOGGER.info('Connected from {}'.format(addr_p1))

            self._send_message('ack', addr_p1)
            self.players_addr.append(addr_p1)
            self._send_message('Waiting for an opponent...', addr_p1)
            while True:
                data, addr_p2 = s.recvfrom(1024)
                if addr_p2 != addr_p1:
                    self._send_message('ack', addr_p2)
                    self.players_addr.append(addr_p2)
                    LOGGER.info('Connected from {}'.format(addr_p2))
                    self._send_message('You have found an opponent', addr_p2)
                    break

            random.shuffle(self.players_addr)
            self.start()

    def start(self):
        for player_addr in self.players_addr:
            self._send_message('The game is about to start', player_addr)

        self._send_message('first', self.players_addr[0])
        self._send_message('second', self.players_addr[1])

        has_won = False
        while True:
            for player_id, player_addr in enumerate(self.players_addr):
                has_won = self.play_round(player_addr, player_id)
                if has_won:
                    break
            if has_won:
                break

        for score in self.model.score:
            if score > 100:
                return

        self.start()

    def listen_to(self, player_addr):
        while True:
            data, addr = self.socket.recvfrom(self.BUFFER_SIZE)
            if player_addr == addr:
                return self.read_data(data)

    def play_round(self, player_addr, player_id):
        has_won = False
        for identifier, addr in enumerate(self.players_addr):
            self._send_message(self.model.describe(identifier), addr)
        """
        ################# STEP ONE ################# 
        """

        data = self.listen_to(player_addr)
        if data[0] == 's':
            self.model.steal_card(player_id)
        elif data[0] == 'd':
            self.model.draw_card(player_id)
        else:
            LOGGER.debug(data)
            raise NetworkException('Unreadable data')

        """
        ################# STEP TWO ################# 
        """
        self._send_message(self.model.describe(player_id), player_addr)
        data = self.listen_to(player_addr)
        if data[0] == 'l':
            card = data[1:].strip()
            self.model.discard_card(player_id, card)
        else:
            LOGGER.debug(data)
            raise NetworkException('Unreadable data')

        """
        ################# STEP THREE #################
        """
        self._send_message(self.model.describe(player_id), player_addr)
        data = self.listen_to(player_addr)
        if data[0] == 'k':
            try:
                score = self.model.knock(player_id)
                identifier = player_id if score > 0 else 0 if player_id is 1 else 1
                self.end_game(identifier, score)
                has_won = True
            except GameException:
                self.prevent_knock(player_id)
        else:
            self._send_message('Your score : {}'.format(self.model.count(player_id)), player_addr)

        return has_won

    def prevent_knock(self, player_id):
        self._send_message('You cannot knock yet: your score is {}'.format(self.model.count(player_id)), self.players_addr[player_id])

    def end_game(self, player_id, score):
        self.players_addr[0], self.players_addr[1] = self.players_addr[1], self.players_addr[0]
        for player_addr in self.players_addr:
            self._send_message('Player {} has won, scores : {}'.format(player_id, ' - '.join(self.model.score)),
                               player_addr)

    def read_data(self, data):
        message = data.decode('utf-8')
        LOGGER.info(message)
        try:
            return message[message.index(':') + 1: len(message)].strip()
        except ValueError:
            pass
