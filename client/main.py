from datetime import datetime
from typing import Optional
from generate import generate_maze
from tinydb import TinyDB, Query
from getpass import getpass
from level import Level
from settings import *
import pygame, sys
import threading
import requests
import socketio
import argparse
import random
import json

parser = argparse.ArgumentParser()
parser.add_argument("--custom", action="store_true", help="Custom Instance?")
args = parser.parse_args()

APPURL = input("Instance URL: ") if args.custom else "http://localhost:5000"


def logger(str):
    print(f"[{datetime.today().isoformat()}] {str}")


class AsyncIOHandler:
    def __init__(self, app_url, token):
        self.sio = socketio.Client()
        self.app_url = app_url
        self.token = token
        self.clientid = None
        self.game: Optional[Game] = None
        self.connected_event = threading.Event()

    def connect(self):
        @self.sio.on("disconnect")  # type: ignore
        def on_disconnect():
            logger("Disconnected!")

        @self.sio.on("connect")  # type: ignore
        def connect():
            self.sio.emit("joinqueue", ("chase", self.clientid))

        @self.sio.on("connected")  # type: ignore
        def authed(clientid):
            logger("Authenticated!")
            self.clientid = clientid
            print(self.clientid)

        @self.sio.on("idqueue")  # type: ignore
        def queued(id):
            logger(f"Queued... {id}")

        @self.sio.on("statusqueue")  # type: ignore
        def queuestatus(length):
            logger(f"Queue: {length}")

        @self.sio.on("donequeue")  # type: ignore
        def donequeue():
            logger("Done queuing!")
            self.connected_event.set()

        @self.sio.on("stateupdate")  # type: ignore
        def updategame(data):
            logger(data)
            if self.game:
                match data["type"]:
                    case "move":
                        if self.game.level:
                            to_move = list(
                                filter(
                                    lambda p: p.id == data["id"],
                                    self.game.level.players,
                                )
                            )[0]
                            to_move.rect.x = round(data["x"] / 64) * 64
                            to_move.rect.y = round(data["y"] / 64) * 64
                            to_move.hitbox.x = round(data["x"] / 64) * 64
                            to_move.hitbox.y = round(data["y"] / 64) * 64
                            to_move.status = data["stat"]
                            to_move.animate()
                    case "dc":
                        if self.game.level:
                            to_kill = list(
                                filter(
                                    lambda p: p.id == data["id"],
                                    self.game.level.players,
                                )
                            )[0]
                            to_kill.kill()

        @self.sio.on("worldgen")  # type: ignore
        def worldgen(data, players):
            logger("World data received.")
            logger(players)
            if self.game and self.clientid:
                self.game.level = Level(
                    layout=list(map(lambda row: list(map(str, row)), data)),
                    player_ids=list(map(str, players)),
                    player=str(self.clientid),
                    aio=self,
                )

        self.sio.connect(self.app_url, auth=self.token)

    def is_connected(self):
        return self.connected_event.is_set()


class Game:
    def __init__(self, aio: AsyncIOHandler):
        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        pygame.display.set_caption("Heritage hunters")
        self.clock = pygame.time.Clock()
        self.level: Level = None  # type: ignore
        aio.game = self

        # print("players", list(map(lambda p: (p.rect.x, p.rect.y), self.level.players)))

        # sound
        # main_sound = pygame.mixer.Sound("../audio/main.ogg")
        # main_sound.set_volume(0.1)
        # main_sound.play(loops=-1)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        if self.level:
                            self.level.toggle_menu()

            self.screen.fill("#000000")
            if self.level:
                self.level.run()
            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == "__main__":

    db = TinyDB("db.json")
    sio = socketio.Client()
    ClientData = Query()
    token = db.get(ClientData.token.exists())

    print(
        """
'||  ||`                      ||                          '||  ||`                     ||                        
 ||  ||                 ''    ||                           ||  ||                      ||                        
 ||''||  .|''|, '||''|  ||  ''||''   '''|.  .|''|, .|''|,  ||''||  '||  ||` `||''|,  ''||''  .|''|, '||''| ('''' 
 ||  ||  ||..||  ||     ||    ||    .|''||  ||  || ||..||  ||  ||   ||  ||   ||  ||    ||    ||..||  ||     `'') 
.||  ||. `|...  .||.   .||.   `|..' `|..||. `|..|| `|...  .||  ||.  `|..'|. .||  ||.   `|..' `|...  .||.   `...' 
                                                ||                                                               
                                             `..|'                                                               
"""
    )
    if not token:
        print("User data not found or invalidated!")
        print(
            """Would you like to:
1.) Log-in 
2.) Register"""
        )
        login = input("Choose (1 or 2): ").strip().lower()

        while True:
            if login not in ["1", "2"]:
                print("Invalid input!")
                login = input("Choose (1 or 2): ").strip().lower()
                continue

            match login:
                case "1":
                    print(
                        "Please enter your credentials. The password is hidden, just input your password and enter."
                    )
                    username = input("Username: ").strip()
                    password = getpass("Password: ").strip()
                    with requests.session() as s:
                        res = s.post(
                            APPURL + "/login",
                            json.dumps({"username": username, "password": password}),
                        )
                        if res.status_code != 200:
                            print("Failed to login! Please try again.")
                            continue
                        db.insert({"token": res.content.decode()})
                        print("Logged in!")
                        break
                case "2":
                    print("Please enter your username.")
                    username = input("Username: ").strip()
                    body = random.choice(["TINGGI", "PENDEK", "BESAR", "KURUS"])
                    with requests.session() as s:
                        res = s.post(
                            APPURL + "/register",
                            json.dumps({"username": username, "body": body}),
                        )
                        if res.status_code == 409:
                            print("Username taken! Please try again.")
                            continue
                        if res.status_code != 200:
                            print("Failed to register! Please try again.")
                            continue
                        print("Registered!")
                        print(f"Your password is: {res.content.decode()}")
                        print(
                            "Please remember this password! You may now log in using the password."
                        )
                        login = "1"
                        continue

    token = db.get(ClientData.token.exists())
    async_io_handler = AsyncIOHandler(APPURL, token)
    connection_thread = threading.Thread(target=async_io_handler.connect)
    connection_thread.start()
    game = Game(async_io_handler)

    while True:
        if async_io_handler.is_connected():
            game.run()
