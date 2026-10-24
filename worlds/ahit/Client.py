import asyncio
import time

import Utils
import websockets
import functools
from copy import deepcopy
from typing import List, Any, Iterable
from NetUtils import decode, encode, JSONtoTextParser, JSONMessagePart, NetworkItem, NetworkPlayer
from MultiServer import Endpoint

# UT integration
tracker_loaded = False
try:
    from worlds.tracker.TrackerClient import TrackerGameContext as CommonContext, gui_enabled, ClientCommandProcessor, logger, get_base_parser
    tracker_loaded = True
except ModuleNotFoundError:
    from CommonClient import CommonContext, gui_enabled, ClientCommandProcessor, logger, get_base_parser

DEBUG = False

# TODO: move mapping dicts to another file?
# NOTE: Em pointed out that most of the mappings basically exist already in spaceship_overview
# poptracker_name_mapping = {
    # # TODO: add loc ids
    # # Alpine Skyline
    # "Goat Village/Below Hookpoint":
    # "Goat Village/Hidden Branch":
    # # TODO: Figure out if/how to handle Badge Seller
    # #"Badge Seller/Scammed":
    # "Bird Pass Fork/Yarn":
    # "Yellow Band Hills/Yarn":
    # "Purrloined Village: Horned Stone/Token":
    # "Purrloined Village: Chest Reward/Token":
    # "Bird House/Triple Crow Chest":
    # "Bird House/Brewing Crate House"
    # "Bird House/Hay Bale"
    # "Bird House/Alpine Crow Mini-Gauntlet"
    # "Bird House/Outer Edge"
    # "Bird House/Time Piece"
    # "The Twilight Path/Token"
    # "The Twilight Bell/Wide Purple Platform"
    # "The Twilight Bell/Ice Platform"
    # "The Twilight Bell/Time Piece"
    # "Mystifying Time Mesa: Zipline/Token"
    # "Mystifying Time Mesa: Gate Puzzle/Relic"
    # "Ember Summit/Yarn"
    # "Lava Cake/Center Fence Cage"
    # "Lava Cake/Dweller Pillars"
    # "Lava Cake/Outer Island Chest"
    # "Lava Cake/Top Cake"
    # "Lava Cake/Time Piece"
    # "Goat Outpost Horn/Yarn"
    # "Windy Passage/Yarn"
    # "The Windmill/Entrance"
    # "The Windmill/Inside Pon Cluster"
    # "The Windmill/Dropdown"
    # "The Windmill/House Window"
    # "The Windmill/Time Piece"
    # "Goat Refinery/Yarn"
    # "The Illness has Spread/Time Piece"
    # "The Twilight Bell (Rift)/Time Rift"
    # "Curly Tail Trail/Time Rift"
    # "Alpine Skyline (Rift)/Time Rift"
    # # TODO: Figure out how to handle the Rift pages. UT doesn't support count

    # # Dead Bird Basement
    # "Small Room/Token"
    # "Vent Pipe/Yarn"
    # "Logo Wall/Yarn"
    # "Cardboard Conductor/Yarn"
    # "Above Conductor Sign/Yarn"
    # "Tightrope/Yarn"
    # "Window Platform/Yarn"
    # "Cameras/Yarn"
    # "Disco Room/Yarn"
    # "Locked Room/Relic"
    # "Act Completion/Time Piece"
    
    # # The Arctic Cruise
    # "Lamp Post Top/Relic"
    # "Mafia Cargo Ship/Token"
    # "Control Room/Bon Voyage!"
    # "Toilet/Relic"
    # "Bar/Token"
    # "Dive Board Ledge/Token"
    # "Top Balcony/Token"
    # "Octopus Room/Relic"
    # "Octopus Room Top/Token"
    # "Laundry Room/Token"
    # "Ship Side/Token"
    # "Silver Ring/Relic"
    # # TODO: Figure out if/how to handle badge seller
    # # "Badge Seller/Scammed"
    # "Lost and Found/Ship Shape"
    # "Reception Room/Suitcase"
    # "Reception Room/Under Desk"
    # "Lamp Post/Token"
    # "Iceberg Top/Token"
    # "Post Captain Rescue/Time Piece"
    # "Post Captain Rescue/Behind Iceberg"
    # "Deep Sea/Time Rift"
    # # TODO: Figure out how to handle Deep Sea Rift pages
    # "Balcony/Time Rift"
    
    # # Dead Bird Studio
    # "Act Completion/Dead Bird Studio"
    # "Act Completion/Award Ceremony"
    # "Picture Perfect/Time Piece"
    # "Picture Perfect - Behind Badge Seller/Yarn"
    # "Picture Perfect - Hats Buy Building/Yarn"
    # # TODO: Figure out if/how to handle Badge Seller
    # # "Badge Seller/Scammed"
    # # TODO: Figure out if/how UT handles the weird token 1-8 internal and reference thing
    # # TODO: Continue at locations deadbirdstudio
# }

# TODO: Add poptracker_entrance_mapping

class AHITJSONToTextParser(JSONtoTextParser):
    def _handle_color(self, node: JSONMessagePart):
        return self._handle_text(node)  # No colors for the in-game text


class AHITCommandProcessor(ClientCommandProcessor):
    def _cmd_ahit(self):
        """Check AHIT Connection State"""
        if isinstance(self.ctx, AHITContext):
            logger.info(f"AHIT Status: {self.ctx.get_ahit_status()}")


class AHITContext(CommonContext):
    tags = {"AP"} # remove tracker tag if UT loaded
    command_processor = AHITCommandProcessor
    game = "A Hat in Time"

    def __init__(self, server_address, password):
        super().__init__(server_address, password)
        self.proxy = None
        self.proxy_task = None
        self.gamejsontotext = AHITJSONToTextParser(self)
        self.autoreconnect_task = None
        self.endpoint = None
        self.items_handling = 0b111
        self.room_info = None
        self.connected_msg = None
        self.game_connected = False
        self.awaiting_info = False
        self.full_inventory: List[Any] = []
        self.server_msgs: List[Any] = []

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(AHITContext, self).server_auth(password_requested)

        await self.get_username()
        await self.send_connect()

    def get_ahit_status(self) -> str:
        if not self.is_proxy_connected():
            return "Not connected to A Hat in Time"

        return "Connected to A Hat in Time"

    async def send_msgs_proxy(self, msgs: Iterable[dict]) -> bool:
        """ `msgs` JSON serializable """
        if not self.endpoint or not self.endpoint.socket.open or self.endpoint.socket.closed:
            return False

        if DEBUG:
            logger.info(f"Outgoing message: {msgs}")

        await self.endpoint.socket.send(msgs)
        return True

    async def disconnect(self, allow_autoreconnect: bool = False):
        await super().disconnect(allow_autoreconnect)

    async def disconnect_proxy(self):
        if self.endpoint and not self.endpoint.socket.closed:
            await self.endpoint.socket.close()
        if self.proxy_task is not None:
            await self.proxy_task

    def is_connected(self) -> bool:
        return self.server and self.server.socket.open

    def is_proxy_connected(self) -> bool:
        return self.endpoint and self.endpoint.socket.open

    def on_print_json(self, args: dict):
        text = self.gamejsontotext(deepcopy(args["data"]))
        msg = {"cmd": "PrintJSON", "data": [{"text": text}], "type": "Chat"}
        self.server_msgs.append(encode([msg]))

        if self.ui:
            self.ui.print_json(args["data"])
        else:
            text = self.jsontotextparser(args["data"])
            logger.info(text)

    def update_items(self):
        # just to be safe - we might still have an inventory from a different room
        if not self.is_connected():
            return

        self.server_msgs.append(encode([{"cmd": "ReceivedItems", "index": 0, "items": self.full_inventory}]))

    def on_package(self, cmd: str, args: dict):
        # TODO: see how this interacts or nullifies the optimization logic below. Can maybe modify to only keep slot info, and anything else, for itself instead of wiping it all? How does this affect the game itself?
        # Should probably talk to CookieCat about how to handle this.
        # UT integration
        super().on_package(cmd, args)

        if cmd == "Connected":
            json = args
            # This data is not needed and causes the game to freeze for long periods of time in large asyncs.
            if "slot_info" in json.keys():
                json["slot_info"] = {}
            if "players" in json.keys():
                me: NetworkPlayer
                for n in json["players"]:
                    if n.slot == json["slot"] and n.team == json["team"]:
                        me = n
                        break

                # Only put our player info in there as we actually need it
                json["players"] = [me]
            if DEBUG:
                print(json)
            self.connected_msg = encode([json])
            if self.awaiting_info:
                self.server_msgs.append(self.room_info)
                self.update_items()
                self.awaiting_info = False

        elif cmd == "RoomUpdate":
            # Same story as above
            json = args
            if "players" in json.keys():
                json["players"] = []

            self.server_msgs.append(encode(json))

        elif cmd == "ReceivedItems":
            if args["index"] == 0:
                self.full_inventory.clear()

            for item in args["items"]:
                self.full_inventory.append(NetworkItem(*item))

            self.server_msgs.append(encode([args]))

        elif cmd == "RoomInfo":
            self.seed_name = args["seed_name"]
            self.room_info = encode([args])

        else:
            if cmd != "PrintJSON":
                self.server_msgs.append(encode([args]))

    def make_gui(self):
        ui = super().make_gui()
        ui.base_title = "Archipelago A Hat in Time Client"
        ui.logging_pairs = [("Client", "Archipelago")]
        return ui


async def proxy(websocket, path: str = "/", ctx: AHITContext = None):
    ctx.endpoint = Endpoint(websocket)
    try:
        await on_client_connected(ctx)

        if ctx.is_proxy_connected():
            async for data in websocket:
                if DEBUG:
                    logger.info(f"Incoming message: {data}")

                for msg in decode(data):
                    if msg["cmd"] == "Connect":
                        # Proxy is connecting, make sure it is valid
                        if msg["game"] != "A Hat in Time":
                            logger.info("Aborting proxy connection: game is not A Hat in Time")
                            await ctx.disconnect_proxy()
                            break

                        if ctx.seed_name:
                            seed_name = msg.get("seed_name", "")
                            if seed_name != "" and seed_name != ctx.seed_name:
                                logger.info("Aborting proxy connection: seed mismatch from save file")
                                logger.info(f"Expected: {ctx.seed_name}, got: {seed_name}")
                                text = encode([{"cmd": "PrintJSON",
                                                "data": [{"text": "Connection aborted - save file to seed mismatch"}]}])
                                await ctx.send_msgs_proxy(text)
                                await ctx.disconnect_proxy()
                                break

                        if ctx.auth:
                            name = msg.get("name", "")
                            if name != "" and name != ctx.auth:
                                logger.info("Aborting proxy connection: player name mismatch from save file")
                                logger.info(f"Expected: {ctx.auth}, got: {name}")
                                text = encode([{"cmd": "PrintJSON",
                                                "data": [{"text": "Connection aborted - player name mismatch"}]}])
                                await ctx.send_msgs_proxy(text)
                                await ctx.disconnect_proxy()
                                break

                        if ctx.connected_msg and ctx.is_connected():
                            await ctx.send_msgs_proxy(ctx.connected_msg)
                            ctx.update_items()
                        continue

                    if not ctx.is_proxy_connected():
                        break

                    if msg["cmd"] == "Bounce" and msg.get("tags") == ["DeathLink"] and "data" in msg:
                        msg["data"]["time"] = time.time()

                    await ctx.send_msgs([msg])

    except Exception as e:
        if not isinstance(e, websockets.WebSocketException):
            logger.exception(e)
    finally:
        await ctx.disconnect_proxy()


async def on_client_connected(ctx: AHITContext):
    if ctx.room_info and ctx.is_connected():
        await ctx.send_msgs_proxy(ctx.room_info)
    else:
        ctx.awaiting_info = True


async def proxy_loop(ctx: AHITContext):
    try:
        while not ctx.exit_event.is_set():
            if len(ctx.server_msgs) > 0:
                for msg in ctx.server_msgs:
                    await ctx.send_msgs_proxy(msg)

                ctx.server_msgs.clear()
            await asyncio.sleep(0.1)
    except Exception as e:
        logger.exception(e)
        logger.info("Aborting AHIT Proxy Client due to errors")


def launch(*launch_args: str):
    async def main():
        parser = get_base_parser()
        args = parser.parse_args(launch_args)

        ctx = AHITContext(args.connect, args.password)
        logger.info("Starting A Hat in Time proxy server")
        ctx.proxy = websockets.serve(functools.partial(proxy, ctx=ctx),
                                     host="localhost", port=11311, ping_timeout=999999, ping_interval=999999)
        ctx.proxy_task = asyncio.create_task(proxy_loop(ctx), name="ProxyLoop")

        if tracker_loaded:
            ctx.run_generator()
        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        await ctx.proxy
        await ctx.proxy_task
        await ctx.exit_event.wait()

    Utils.init_logging("AHITClient")
    # options = Utils.get_options()

    import colorama
    colorama.just_fix_windows_console()
    asyncio.run(main())
    colorama.deinit()
