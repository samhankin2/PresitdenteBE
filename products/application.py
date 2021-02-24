from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
from flask_socketio import SocketIO
from random import randint,shuffle
import uuid




app = Flask(__name__)
api = Api(app)
socketio = SocketIO(app, cors_allowed_origins="*")



class Player:
    def __init__(self, username):
        self.username = username
        self.uid = uuid.uuid4()
        self.hand = []

class Card:
    def __init__(self, number, suit, id):
        self.number = number
        self.suit = suit
        self.id = id
        self.human_readable_card = ""

class Deck:
    def __init__(self):
        cards = []
        suits = ["spades", "clubs","hearts", "diamonds"]
        id = 0
        for suit in suits:
          for cardNumber in range(1,14):
              card = Card(cardNumber, suit, id)
              id+=1
              cards.append(card)
        self.cards = cards

    def shuffle(self):
        shuffle(self.cards)
            
class Game:
    def __init__(self, username):
        self.deck = Deck()
        self.players = [Player(username)]
        self.started = False
        self.uid = uuid.uuid4()
    
    def shuffleDeck(self):
        self.deck.shuffle()

    def addPlayer(self, username):
        self.players.append(Player(username))

    def dealCards(self):
        self.shuffleDeck()
        while len(self.deck.cards)>0:
            for player in self.players:
                if len(self.deck.cards) == 0:
                    break
                player.hand.append(self.deck.cards.pop())

    def canPlayCard(self, cardNumber, cardSuit):
        if len(self.deck.cards) == 0:
            return True
        suits = ["spades", "clubs", "hearts", "diamonds"]
        topCard = self.deck.cards[-1]
        
        if cardNumber > topCard.number:
            return True

        if cardNumber == topCard.number:
            playedCardSuitIndex = suits.index(cardSuit)
            topCardSuitIndex = suits.index(topCard.suit)

        if playedCardSuitIndex > topCardSuitIndex:
            return True

        return False

    
    def playCard(self, username, cardNumber, cardSuit):
        playerFound = None
        for player in self.players:
            if player.username == username:
                playerFound = player
                break

        playerHand = playerFound.hand

        cardFound = None
        for card in playerHand:
            if card.number == cardNumber and card.suit == cardSuit:
                cardFound = card
      
        if cardFound:
            print("here A", flush=True)
            if self.canPlayCard(cardNumber, cardSuit):
                playerHand.remove(cardFound)
                self.deck.cards.append(cardFound)
            return
      
        return "Card not in your deck"

gameDict = {}
gameDict["200"] = Game("player 1")

class CreateGame(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        pin = randint(100, 999)
        gameDict[pin] = Game(json_data["username"])
        return {
            "game_pin": pin
        }

class JoinGame(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        gamePin = json_data["game_pin"]
        username = json_data["username"]

        game = gameDict[gamePin]
        if not game.started:
            game.addPlayer(username)
            return 200

        return 400


class StartGame(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        gamePin = json_data["game_pin"]
        game = gameDict[gamePin]
        game.started = True
        game.shuffleDeck()
        game.dealCards()
        # Give someones go

        player = game.players[0]
        hand = []
        for card in player.hand:
            hand.append((card.number, card.suit))

        return hand

class PlayCard(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        gamePin = json_data["game_pin"]
        playedCard = json_data["card"]
        username = json_data["username"]

        print(playedCard, flush=True)
        print(username, flush=True)

        game = gameDict[gamePin]
        game.playCard(username, playedCard["number"], playedCard["suit"])

        hand = []
        player = game.players[0]

        for card in player.hand:
            hand.append((card.number, card.suit))

        return hand



        # Deal cards
        # Give someones go

        # return 200

class Test(Resource):
    def get(self):
        json.dump(game('test'))
        # Deal cards
        # Give someones go

        return 200



api.add_resource(CreateGame, '/create-game')
api.add_resource(JoinGame, '/join-game')
api.add_resource(StartGame, '/start-game')
api.add_resource(PlayCard, '/play-card')
api.add_resource(Test, '/test')

@socketio.on('test')
def handle_message(data):
    socketio.emit('okay', {'data': 42})
    print('received messag' + data, flush=True)

@socketio.on('message')
def handle_message(data):
    print(data)
    socketio.emit('message', data)
    print('received messag' + data, flush=True)



if __name__ == '__main__':
    # socketio.run(app, debug=True)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

    # app.run(host='0.0.0.0', port=5000, debug=True)