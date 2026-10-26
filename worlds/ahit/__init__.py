from BaseClasses import Item, ItemClassification, Tutorial, Location, MultiWorld
from .Items import item_table, create_item, relic_groups, act_contracts, create_itempool, get_shop_trap_name, \
    calculate_yarn_costs, alps_hooks, junk_weights
from .Regions import create_regions, randomize_act_entrances, chapter_act_info, create_events, get_shuffled_region
from .Locations import location_table, contract_locations, is_location_valid, get_location_names, TASKSANITY_START_ID, \
    get_total_locations
from .Rules import set_rules, has_paintings
from .Options import AHITOptions, slot_data_options, adjust_options, RandomizeHatOrder, EndGoal, create_option_groups
from .Types import HatType, ChapterIndex, HatInTimeItem, hat_type_to_item, Difficulty
from .DeathWishLocations import create_dw_regions, dw_classes, death_wishes
from .DeathWishRules import set_dw_rules, create_enemy_events, hit_list, bosses
from worlds.AutoWorld import World, WebWorld, CollectionState
from worlds.generic.Rules import add_rule
from typing import List, Dict, TextIO, Any, ClassVar
from worlds.LauncherComponents import Component, components, icon_paths, launch as launch_component, Type
from Utils import local_path
from settings import Group, FilePath


def launch_client(*args: str):
    from .Client import launch
    launch_component(launch, name="AHITClient", args=args)


components.append(Component("A Hat in Time Client", "AHITClient", func=launch_client,
                            component_type=Type.CLIENT, icon='yatta'))

icon_paths['yatta'] = local_path('data', 'yatta.png')


class AWebInTime(WebWorld):
    theme = "partyTime"
    option_groups = create_option_groups()
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide for setting up A Hat in Time to be played in Archipelago.",
        "English",
        "setup_en.md",
        "setup/en",
        ["CookieCat"]
    )]


# Basically copied from https://github.com/ArsonAssassin/DSAP/commit/62b0c4d87483977e86fdfba2229259ec581c4fdb
# TODO: Is there a way to make it only prompt when people want it to? Is that desirable over auto-prompt?
class AHITSettings(Group):
    class UTPoptrackerPath(FilePath):
        """Path to the user's AHIT Poptracker Pack."""
        description= "AHIT Poptracker Pack zip file"
        required = False
    ut_poptracker_path: UTPoptrackerPath | str = UTPoptrackerPath()

# TODO: Move?
map_page_locations = [
    "locations/spaceship_overview.json",
    "locations/alpineskyline.json",
    "locations/basement.json",
    "locations/cruise.json",
    "locations/deadbirdstudio.json",
    # "locations/deathwish.json", # Has comments in the file, UT can't parse
    # "locations/mafiatown.json", # Has comments in the file
    "locations/nyakuza.json",
    # "locations/spaceship.json", # Has commnets in the file
    "locations/subcon.json"
]

# TODO: move mapping dicts to another file
# TODO: Deal with the abbreviated ones Em mentioned
tracker_name_mapping = {
    # TODO: add loc ids
    
    # Mafia Town
    "Welcome to Mafia Town/Time Piece" : 2000311771,
    "Welcome to Mafia Town/Umbrella" : 2000301002,
    "Barrel Battle/Time Piece" : 2000311958,
    "Mafia Geek/She Came from Outer Space" : 2000312262,
    "Mafia HQ/Time Piece" : 2000311326,
    "Mafia HQ/Hallway Brewing Crate" : 2000305387,
    "Mafia HQ/Freezer Chest" : 2000303241,
    "Mafia HQ/Secret Room" : 2000304979,
    "Mafia HQ/Bathroom Stall Chest" : 2000303243,
    "Beach Alcove/Cheating the Race" : 2000312318,
    "Mafia Geek/Heating Up Mafia Town" : 2000311481,
    "The Golden Vault/Time Piece" : 2000312250,
    "Bazaar/Time Rift" : 2000312465,
    "Sewers/Time Rift" : 2000312484,
    "Mafia of Cooks/Time Rift" : 2000311855,
    # "Mafia of Cooks/Pages" # TODO: Decide how to handle
    "Red Vault/Yarn" : 2000302848,
    "Dweller Boxes/Yarn" : 2000304462,
    "Old Man 2/Seaside Spaghetti" : 2000303833,
    "Ledge Chest/Yarn" : 2000303530,
    "Yellow Sphere Building Chest/Yarn" : 2000303535,
    "Beneath Scaffolding/Yarn" : 2000304456,
    "On Scaffolding/Yarn" : 2000304457,
    "Plaza Under Boxes/Yarn" : 2000304458,
    "Blue Vault/Brewing Crate" : 2000305572,
    "Small Boat/Yarn" : 2000304460,
    "Cargo Ship/Yarn" : 2000304459,
    "Beach Alcove/Yarn" : 2000304463,
    "Steel Beams/Wood Cage" : 2000304606,
    "Staircase Pon Cluster/Yarn" : 2000304611,
    "Blue Vault/Vault" : 2000302850,
    "Old Man/Yarn" : 2000303832,
    "Palm Tree/Yarn" : 2000304609,
    "Beach Patio/Freestanding" : 2000304610,
    "Steel Beams/Nest" : 2000304608,
    "Top of Ruined Tower/Yarn" : 2000304607,
    "Ice Hat Cage/Yarn" : 2000304831,
    "Hot Air Balloon/Yarn" : 2000304829,
    "Camera Badge/smile :)" : 2000302003,
    "Camera Badge 2/smile :)" : 2000302004,
    "Chest Beneath Aqueduct/Relic" : 2000303489,
    "Secret Cave/Relic" : 2000305220,
    "Crow Chest/Relic" : 2000303532,
    "Port/Relic" : 2000305219,
    "Docks Chest/Relic" : 2000303534,
    "Above Boats/Relic" : 2000305218,
    "Beach Patio/Slip Slide Chest" : 2000303529,
    "Green Vault/Token" : 2000302851,
    "Behind Faucet/Token" : 2000304214,
    "Hidden Buttons/Grab a beach ball" : 2000303483,
    "Clock Tower Chest/Token" : 2000303481,
    "Top of Lighthouse/Token" : 2000304213,
    "Mafia Geek Platform/Token" : 2000304212,
    "Mafia HQ/Behind HQ Chest" : 2000303486,
    
    # Battle of the Birds
    "Act Completion/Dead Bird Studio" : 2000311383,
    "Up the Ladder/Yarn" : 2000304874,
    "DJ Grooves Sign Chest/Yarn" : 2000303901,
    "Red Building Top/Yarn" : 2000305024,
    "Behind Water Tower/Yarn" : 2000305248,
    "Side of House/Yarn" : 2000305247,
    "Tightrope Chest/Relic" : 2000303898,
    "Teepee Chest/Relic" : 2000303899,
    "Conductor Chest/Token" : 2000303900,
    # "Act Completion/Time Piece" # Oh boy, is this unique? TODO: ??
    "Cafeteria/Yarn" : 2000305313,
    "Luggage Room Top/Yarn" : 2000305090,
    "Luggage Room Bottom/Yarn" : 2000305091,
    "Raven Suite/Room" : 2000305701,
    "Raven Suite/Top" : 2000305312,
    "Lounge Chest/Token" : 2000303963,
    # TODO: Verify these actually show up
    "Conductor Token: Cafeteria/" : 2001104767,
    "Conductor Token: Recreational Room/" : 2001104768,
    "Picture Perfect/Time Piece" : 2000311587,
    "Picture Perfect - Behind Badge Seller/Yarn" : 2000304307,
    "Picture Perfect - Hats Buy Building/Yarn" : 2000304530,
    "Picture Perfect - DJ Grooves Token: Cardboard Puppy/" : 2001203990,
    "Picture Perfect - DJ Grooves Token: Card Guessing Game/" : 2001203991,
    "Picture Perfect - DJ Grooves Token: Back Alley/" : 2001203992,
    "Picture Perfect - DJ Grooves Token: Cooking Show/" : 2001203993,
    "Picture Perfect - DJ Grooves Token: Pon Cluster/" : 2001203987,
    "Train Rush/Time Piece" : 2000312481,
    "Time Bonus: 1st Room/" : 2001305235,
    "Time Bonus: Falling Platform/" : 2001305189,
    "Time Bonus: Acid Crates/" : 2001305186,
    "Time Bonus: Balloon/" : 2001305239,
    "Time Bonus: Ring of Fire/" : 2001305237,
    "Time Bonus: Blue Panels/" : 2001305236,
    "Time Bonus: Sinking Lava Platform/" : 2001305234,
    "Time Bonus: Lava Panels 1/" : 2001305193,
    "Time Bonus: Lava Panels 2/" : 2001305190,
    "Time Bonus: Lava Panels 3/" : 2001305238,
    "The Big Parade/Time Piece" : 2000311157,
    # TODO: Figure out why the tokens don't show up. Probably the internal
    "The Big Parade - DJ Grooves Tokens (Internal)/Token 1" : 2001400000,
    "The Big Parade - DJ Grooves Tokens (Internal)/Token 2" : 2001400001,
    "The Big Parade - DJ Grooves Tokens (Internal)/Token 3" : 2001400002,
    "The Big Parade - DJ Grooves Tokens (Internal)/Token 4" : 2001400003,
    "The Big Parade - DJ Grooves Tokens (Internal)/Token 5" : 2001400004,
    "The Big Parade - DJ Grooves Tokens (Internal)/Token 6" : 2001400005,
    "The Big Parade - DJ Grooves Tokens (Internal)/Token 7" : 2001400006,
    "The Big Parade - DJ Grooves Tokens (Internal)/Token 8" : 2001400007,
    "Act Completion/Award Ceremony" : 2000311488,
    # "Act Completion/Time Piece" # Yep, not unique... TODO: how?
    "Window Platform/Yarn" : 2000305432,
    "Cardboard Conductor/Yarn" : 2000305059,
    "Above Conductor Sign/Yarn" : 2000305057,
    "Logo Wall/Yarn" : 2000305207,
    "Disco Room/Yarn" : 2000305061,
    "Small Room/Token" : 2000304813,
    "Vent Pipe/Yarn" : 2000305430,
    "Tightrope/Yarn" : 2000305058,
    "Cameras/Yarn" : 2000305431,
    "Locked Room/Relic" : 2000305819,
    "The Owl Express/Time Rift" : 2000312807,
    "The Moon/Time Rift" : 2000312785,
    "Dead Bird Studio (Rift)/Time Piece" : 2000312577,
    # "Dead Bird Studio (Rift)/Pages" TODO: Decide how to handle this
    
    # Subcon Forest
    "Contractual Obligations/Time Piece" : 2000312317,
    "Snatcher/Contract - The Subcon Well" : 2000300200,
    "Cherry Bomb Bone Cage/Yarn" : 2000324761,
    "Subcon Well/Time Piece" : 2000311160,
    "Subcon Well/Hookshot Badge Chest" : 2000324114,
    "Subcon Well/Above Chest" : 2000324612,
    "Subcon Well/On Pipe" : 2000324311,
    "Subcon Well/Mushroom" : 2000325318,
    "Boss Arena/Toilet of Doom" : 2000311984,
    "Queen Vanessa's Manor/Time Piece" : 2000312017,
    "Queen Vanessa's Manor/Cellar" : 2000324841,
    "Queen Vanessa's Manor/Bedroom Chest" : 2000323808,
    "Queen Vanessa's Manor/Hall Chest" : 2000323896,
    "Queen Vanessa's Manor/Chandelier" : 2000325546,
    "Snatcher/Mail Delivery Service" : 2000312032,
    "Boss Arena/Your Contract has Expired" : 2000311390,
    "Pipe/Time Rift" : 2000313069,
    "Village/Time Rift" : 2000313056,
    "Sleepy Subcon/Time Rift" : 2000312086,
    # "Sleepy Subcon/Pages" TODO: decide how to handle
    # "Snatcher/Contracts" : TODO: decide how to handle
    "Tree Top Ice Cube/Yarn" : 2000325469,
    "Graveyard/Ice Cube" : 2000325077,
    "Graveyard/House Top" : 2000325471,
    "Ice Cube House/Relic" : 2000325469,
    "Snatcher Statue Chest/Yarn" : 2000323730,
    "Stump Platform Chest/Yarn" : 2000323729,
    "Giant Mushroom Climb/Don't Fall~" : 2000325470,
    "Swamp Gravestone/Yarn" : 2000326296,
    "Swamp Near Well/Token" : 2000324762,
    "Swamp Tree A/Yarn" : 2000324763,
    "Swamp Tree B/Yarn" : 2000324764,
    "Swamp Ice Wall/Yarn" : 2000324706,
    "Swamp Treehouse/Relic" : 2000325468,
    "Swamp Tree Chest/Yarn" : 2000323728,
    "Dweller Stump/Yarn" : 2000324767,
    "Dweller Floating Rocks/Token" : 2000324464,
    "Dweller Platforming Tree A/Yarn" : 2000324709,
    "Dweller/Platforming Tree B" : 2000324855,
    "Giant Time Piece/Relic" : 2000325473,
    "Gallows/Relic" : 2000325472,
    "Green and Purple Dweller Rocks/Yarn" : 2000325082,
    "Dweller/Shack" : 2000324463,
    "Tall Tree Hookshot Swing/Yarn" : 2000324766,
    "Burning House/Yarn" : 2000324710,
    "Burning Tree Climb/Yarn" : 2000325079,
    "Burning Stump Chest/Token" : 2000323731,
    "Burning Forest Treehouse/Relic" : 2000325467,
    "Spider Bone Cage A/Token" : 2000324462,
    "Spider Bone Cage B/Yarn" : 2000325080,
    "Infinite Yarn Bush/Yarn" : 2000325478,
    "Magnet Badge Bush/Badge" : 2000325479,
    "Triple Spider Bounce/Yarn" : 2000324765,
    "Noose Treehouse/Relic" : 2000324856,
    "Ice Cube Shack/Token" : 2000324465,
    "Long Tree Climb Chest/Yarn" : 2000323734,
    "Boss Arena Chest/Yarn" : 2000323735,
    "Queen Vanessa's Manor/Rooftop" : 2000325466,
    
    # Alpine Skyline
    "Goat Village/Below Hookpoint" : 2000334856,
    "Goat Village/Hidden Branch" : 2000334855,
    "Goat Refinery/Yarn" : 2000333635,
    "Bird House/Time Piece" : 2000311428,
    "Bird Pass Fork/Yarn" : 2000335911,
    "Yellow Band Hills/Yarn" : 2000335756,
    "Purrloined Village: Horned Stone/Token" : 2000335561,
    "Purrloined Village: Chest Reward/Token" : 2000334831,
    "Bird House/Triple Crow Chest" : 2000334758,
    "Bird House/Dweller Platforms Relic" : 2000336497,
    "Bird House/Brewing Crate House" : 2000336496,
    "Bird House/Hay Bale" : 2000335885,
    "Bird House/Alpine Crow Mini-Gauntlet" : 2000335886,
    "Bird House/Outer Edge" : 2000335492,
    "Lava Cake/Time Piece" : 2000312509,
    "Mystifying Time Mesa: Zipline/Token" : 2000337058,
    "Mystifying Time Mesa: Gate Puzzle/Relic" : 2000336052,
    "Ember Summit/Yarn" : 2000336311,
    "Lava Cake/Center Fence Cage" : 2000335448,
    "Lava Cake/Outer Island Chest" : 2000334291,
    "Lava Cake/Dweller Pillars" : 2000335417,
    "Lava Cake/Top Cake" : 2000335418,
    "The Twilight Bell/Time Piece" : 2000311540,
    "The Twilight Path/Token" : 2000334434,
    "The Twilight Bell/Wide Purple Platform" : 2000336478,
    "The Twilight Bell/Ice Platform" : 2000335826,
    "The Windmill/Time Piece" : 2000312263,
    "Goat Outpost Horn/Yarn" : 2000334760,
    "Windy Passage/Yarn" : 2000334776,
    "The Windmill/Inside Pon Cluster" : 2000336395,
    "The Windmill/Entrance" : 2000335783,
    "The Windmill/Dropdown" : 2000335815,
    "The Windmill/House Window" : 2000335389,
    "The Illness has Spread/Time Piece" : 2000312022,
    "The Twilight Bell (Rift)/Time Rift" : 2000312399,
    "Curly Tail Trail/Time Rift" : 2000313335,
    "Alpine Skyline (Rift)/Time Rift" : 2000311777
    # "Alpine Skyline (Rift)/Pages" TODO: ???
    
    # TODO: Continue from overview chapt 6, make sure to add comma above
    # Where is the finale?
    
}

# TODO: Add poptracker_entrance_mapping?

class HatInTimeWorld(World):
    """
    A Hat in Time is a cute-as-peck 3D platformer featuring a little girl who stitches hats for wicked powers!
    Freely explore giant worlds and recover Time Pieces to travel to new heights!
    """

    game = "A Hat in Time"
    item_name_to_id = {name: data.code for name, data in item_table.items()}
    location_name_to_id = get_location_names()
    options_dataclass = AHITOptions
    options: AHITOptions
    item_name_groups = relic_groups
    web = AWebInTime()

    # UT integration
    ut_can_gen_without_yaml = True
    glitches_item_name = "Level Up"
    settings: ClassVar[AHITSettings]
    tracker_world: ClassVar = {
        "nested_pack" : True,
        "map_page_maps" : "maps/maps.json",
        "map_page_locations" : map_page_locations,
        "poptracker_name_mapping" : tracker_name_mapping,
        "map_page_layouts" : "layouts/map_tabs.json",
        "external_pack_key" : "ut_poptracker_path"
    }

    def __init__(self, multiworld: "MultiWorld", player: int):
        super().__init__(multiworld, player)
        self.act_connections: Dict[str, str] = {}
        self.shop_locs: List[str] = []

        self.hat_craft_order: List[HatType] = [HatType.SPRINT, HatType.BREWING, HatType.ICE,
                                               HatType.DWELLER, HatType.TIME_STOP]

        self.hat_yarn_costs: Dict[HatType, int] = {HatType.SPRINT: -1, HatType.BREWING: -1, HatType.ICE: -1,
                                                   HatType.DWELLER: -1, HatType.TIME_STOP: -1}

        self.chapter_timepiece_costs: Dict[ChapterIndex, int] = {ChapterIndex.MAFIA: -1,
                                                                 ChapterIndex.BIRDS: -1,
                                                                 ChapterIndex.SUBCON: -1,
                                                                 ChapterIndex.ALPINE: -1,
                                                                 ChapterIndex.FINALE: -1,
                                                                 ChapterIndex.CRUISE: -1,
                                                                 ChapterIndex.METRO: -1}
        self.excluded_dws: List[str] = []
        self.excluded_bonuses: List[str] = []
        self.dw_shuffle: List[str] = []
        self.nyakuza_thug_items: Dict[str, int] = {}
        self.badge_seller_count: int = 0
        
        # UT generation
        self.fake_gen = getattr(self.multiworld, "generation_is_fake",False)

    def get_filler_item_name(self) -> str:
        return self.random.choices(list(junk_weights.keys()), weights=junk_weights.values(), k=1)[0]

    def generate_early(self):

        # UT Integration
        re_gen_passthrough = getattr(self.multiworld, "re_gen_passthrough", {})
        if re_gen_passthrough and self.game in re_gen_passthrough:
            # Get the passed through slot data from the real generation
            slot_data: dict[str, Any] = re_gen_passthrough[self.game]

            # TODO: Remove
            # print("Slot data:")
            # print(slot_data)

            # Set all your options here instead of getting them from the yaml
            for key, value in slot_data.items():
                opt: Option[Any] | None = getattr(self.options, key, None)
                if opt is not None:
                    # You can also set .value directly but that won't work if you have OptionSets
                    setattr(self.options, key, opt.from_any(value))

            # Set chapter costs from slot data
            self.chapter_timepiece_costs[ChapterIndex.MAFIA] = slot_data["Chapter1Cost"]
            self.chapter_timepiece_costs[ChapterIndex.BIRDS] = slot_data["Chapter2Cost"]
            self.chapter_timepiece_costs[ChapterIndex.SUBCON] = slot_data["Chapter3Cost"]
            self.chapter_timepiece_costs[ChapterIndex.ALPINE] = slot_data["Chapter4Cost"]
            self.chapter_timepiece_costs[ChapterIndex.FINALE] = slot_data["Chapter5Cost"]
            self.chapter_timepiece_costs[ChapterIndex.CRUISE] = slot_data["Chapter6Cost"]
            self.chapter_timepiece_costs[ChapterIndex.METRO] = slot_data["Chapter7Cost"]

            # Set hat yarn costs and craft order from slot data
            if self.has_yarn():
                self.hat_yarn_costs[HatType.SPRINT] = slot_data["SprintYarnCost"]
                self.hat_yarn_costs[HatType.BREWING] = slot_data["BrewingYarnCost"]
                self.hat_yarn_costs[HatType.ICE] = slot_data["IceYarnCost"]
                self.hat_yarn_costs[HatType.DWELLER] = slot_data["DwellerYarnCost"]
                self.hat_yarn_costs[HatType.TIME_STOP] = slot_data["TimeStopYarnCost"]

                self.hat_craft_order[0] = slot_data["Hat1"]
                self.hat_craft_order[1] = slot_data["Hat2"]
                self.hat_craft_order[2] = slot_data["Hat3"]
                self.hat_craft_order[3] = slot_data["Hat4"]
                self.hat_craft_order[4] = slot_data["Hat5"]

            # Get randomized act locations from slot data
            if self.options.ActRandomizer:
                for key, value in chapter_act_info.items():
                    if value in slot_data:
                        self.act_connections[value] = slot_data[value]

            # Set number of badge seller items from slot data
            self.badge_seller_count = slot_data["BadgeSellerItemCount"]

            # Set number of nyakuza thug shop items from slot data
            if self.is_dlc2() and not self.is_dw_only():
                thug_numbers = [0, 1, 2, 4, 5, 6, 7, 12, 13, 14]
                for thug in thug_numbers:
                    thug_name = f"Hat_NPC_NyakuzaShop_{thug}"
                    self.nyakuza_thug_items[thug_name] = slot_data[thug_name]

            # Set deathwish shuffle from slot data
            # Need to get the key from dw_classes because slot data only has dw_classes values
            # dw_shuffle is a list of dw_classes keys
            if self.is_dw() and self.options.DWShuffle:
                dw_count = len(dw_classes)
                for i in range(dw_count):
                    if f"dw_{i}" in slot_data:
                        dw_class = slot_data[f"dw_{i}"]
                        for key, value in dw_classes.items():
                            if value == dw_class:
                                self.dw_shuffle.append(key)
                                break
                    else:
                        # No more dw in slot data
                        break
            
            # TODO: Remove
            # print("Options:")
            # print(vars(self.options))

        # TODO: Verify if this is actually causing issues one way or the other, decide how I want to leave it (doing this seems to have changed nothing in the fuzzer)
        # Options being passed should already be adjusted properly
        if not self.fake_gen:
            adjust_options(self)

        if self.options.StartWithCompassBadge:
            self.multiworld.push_precollected(self.create_item("Compass Badge"))

        if self.is_dw_only():
            return

        # Take care of some extremely restrictive starts in other chapters with act shuffle off
        # TODO: see if the random zipline is an issue for UT
        if not self.options.ActRandomizer:
            start_chapter = self.options.StartingChapter
            if start_chapter == ChapterIndex.ALPINE:
                self.multiworld.push_precollected(self.create_item("Hookshot Badge"))
                if self.options.UmbrellaLogic:
                    self.multiworld.push_precollected(self.create_item("Umbrella"))

                if self.options.ShuffleAlpineZiplines:
                    ziplines = list(alps_hooks.keys())
                    ziplines.remove("Zipline Unlock - The Twilight Bell Path")  # not enough checks from this one
                    self.multiworld.push_precollected(self.create_item(self.random.choice(ziplines)))
            elif start_chapter == ChapterIndex.SUBCON:
                if self.options.ShuffleSubconPaintings:
                    self.multiworld.push_precollected(self.create_item("Progressive Painting Unlock"))
            elif start_chapter == ChapterIndex.BIRDS:
                if self.options.UmbrellaLogic:
                    if self.options.LogicDifficulty < Difficulty.EXPERT:
                        self.multiworld.push_precollected(self.create_item("Umbrella"))
                elif self.options.LogicDifficulty < Difficulty.MODERATE:
                    self.multiworld.push_precollected(self.create_item("Umbrella"))

    def create_regions(self):
        # noinspection PyClassVar
        self.topology_present = bool(self.options.ActRandomizer)

        create_regions(self)
        if self.options.EnableDeathWish:
            create_dw_regions(self)

        if self.is_dw_only():
            return

        create_events(self)
        if self.is_dw():
            if "Snatcher's Hit List" not in self.excluded_dws or "Camera Tourist" not in self.excluded_dws:
                create_enemy_events(self)

        # place vanilla contract locations if contract shuffle is off
        if not self.options.ShuffleActContracts:
            for name in contract_locations.keys():
                loc = self.get_location(name)
                loc.place_locked_item(create_item(self, name))
                if self.options.ShuffleSubconPaintings and loc.name != "Snatcher's Contract - The Subcon Well":
                    add_rule(loc, lambda state: has_paintings(state, self, 1))

    def create_items(self):
        # Don't randomize hat costs and craft order if UT generation
        if self.has_yarn() and not self.fake_gen:
            calculate_yarn_costs(self)

            if self.options.RandomizeHatOrder:
                self.random.shuffle(self.hat_craft_order)
                if self.options.RandomizeHatOrder == RandomizeHatOrder.option_time_stop_last:
                    self.hat_craft_order.remove(HatType.TIME_STOP)
                    self.hat_craft_order.append(HatType.TIME_STOP)

            # move precollected hats to the start of the list
            for i in range(5):
                hat = HatType(i)
                if self.is_hat_precollected(hat):
                    self.hat_craft_order.remove(hat)
                    self.hat_craft_order.insert(0, hat)

        self.multiworld.itempool += create_itempool(self)

    def set_rules(self):
        if self.is_dw_only():
            # we already have all items if this is the case, no need for rules
            self.multiworld.push_precollected(HatInTimeItem("Death Wish Only Mode", ItemClassification.progression,
                                              None, self.player))

            self.multiworld.completion_condition[self.player] = lambda state: state.has("Death Wish Only Mode",
                                                                                        self.player)

            if not self.options.DWEnableBonus:
                for name in death_wishes:
                    if name == "Snatcher Coins in Nyakuza Metro" and not self.is_dlc2():
                        continue

                    if self.options.DWShuffle and name not in self.dw_shuffle:
                        continue

                    full_clear = self.multiworld.get_location(f"{name} - All Clear", self.player)
                    full_clear.address = None
                    full_clear.place_locked_item(HatInTimeItem("Nothing", ItemClassification.filler, None, self.player))
                    full_clear.show_in_spoiler = False

            return

        if self.options.ActRandomizer:
            randomize_act_entrances(self)

        set_rules(self)

        if self.is_dw():
            set_dw_rules(self)

    def create_item(self, name: str) -> Item:
        return create_item(self, name)

    def fill_slot_data(self) -> dict:
        slot_data: dict = {"Chapter1Cost": self.chapter_timepiece_costs[ChapterIndex.MAFIA],
                           "Chapter2Cost": self.chapter_timepiece_costs[ChapterIndex.BIRDS],
                           "Chapter3Cost": self.chapter_timepiece_costs[ChapterIndex.SUBCON],
                           "Chapter4Cost": self.chapter_timepiece_costs[ChapterIndex.ALPINE],
                           "Chapter5Cost": self.chapter_timepiece_costs[ChapterIndex.FINALE],
                           "Chapter6Cost": self.chapter_timepiece_costs[ChapterIndex.CRUISE],
                           "Chapter7Cost": self.chapter_timepiece_costs[ChapterIndex.METRO],
                           "BadgeSellerItemCount": self.badge_seller_count,
                           "SeedNumber": str(self.multiworld.seed),  # For shop prices
                           "SeedName": self.multiworld.seed_name,
                           "TotalLocations": get_total_locations(self)}

        if self.has_yarn():
            slot_data.setdefault("SprintYarnCost", self.hat_yarn_costs[HatType.SPRINT])
            slot_data.setdefault("BrewingYarnCost", self.hat_yarn_costs[HatType.BREWING])
            slot_data.setdefault("IceYarnCost", self.hat_yarn_costs[HatType.ICE])
            slot_data.setdefault("DwellerYarnCost", self.hat_yarn_costs[HatType.DWELLER])
            slot_data.setdefault("TimeStopYarnCost", self.hat_yarn_costs[HatType.TIME_STOP])
            slot_data.setdefault("Hat1", int(self.hat_craft_order[0]))
            slot_data.setdefault("Hat2", int(self.hat_craft_order[1]))
            slot_data.setdefault("Hat3", int(self.hat_craft_order[2]))
            slot_data.setdefault("Hat4", int(self.hat_craft_order[3]))
            slot_data.setdefault("Hat5", int(self.hat_craft_order[4]))

        if self.options.ActRandomizer:
            for name in self.act_connections.keys():
                slot_data[name] = self.act_connections[name]

        if self.is_dlc2() and not self.is_dw_only():
            for name in self.nyakuza_thug_items.keys():
                slot_data[name] = self.nyakuza_thug_items[name]

        if self.is_dw():
            i = 0
            for name in self.excluded_dws:
                if self.options.EndGoal.value == EndGoal.option_seal_the_deal and name == "Seal the Deal":
                    continue

                slot_data[f"excluded_dw{i}"] = dw_classes[name]
                i += 1

            i = 0
            if not self.options.DWAutoCompleteBonuses:
                for name in self.excluded_bonuses:
                    if name in self.excluded_dws:
                        continue

                    slot_data[f"excluded_bonus{i}"] = dw_classes[name]
                    i += 1

            if self.options.DWShuffle:
                shuffled_dws = self.dw_shuffle
                for i in range(len(shuffled_dws)):
                    slot_data[f"dw_{i}"] = dw_classes[shuffled_dws[i]]

        shop_item_names: Dict[str, str] = {}
        for name in self.shop_locs:
            loc: Location = self.multiworld.get_location(name, self.player)
            assert loc.item
            item_name: str
            if loc.item.classification is ItemClassification.trap and loc.item.game == "A Hat in Time":
                item_name = get_shop_trap_name(self)
            else:
                item_name = loc.item.name

            shop_item_names.setdefault(str(loc.address),
                                       f"{item_name} ({self.multiworld.get_player_name(loc.item.player)})")

        slot_data["ShopItemNames"] = shop_item_names
        slot_data.update(self.options.as_dict(*slot_data_options))
        return slot_data

    def extend_hint_information(self, hint_data: Dict[int, Dict[int, str]]):
        if self.is_dw_only() or not self.options.ActRandomizer:
            return

        new_hint_data = {}
        alpine_regions = ["The Birdhouse", "The Lava Cake", "The Windmill",
                          "The Twilight Bell", "Alpine Skyline Area", "Alpine Skyline Area (TIHS)"]

        metro_regions = ["Yellow Overpass Station", "Green Clean Station", "Bluefin Tunnel", "Pink Paw Station"]

        for key, data in location_table.items():
            if not is_location_valid(self, key):
                continue

            location = self.multiworld.get_location(key, self.player)
            region_name: str

            if data.region in alpine_regions:
                region_name = "Alpine Free Roam"
            elif data.region in metro_regions:
                region_name = "Nyakuza Free Roam"
            elif "Dead Bird Studio - " in data.region:
                region_name = "Dead Bird Studio"
            elif data.region in chapter_act_info.keys():
                region_name = location.parent_region.name
            else:
                continue

            new_hint_data[location.address] = get_shuffled_region(self, region_name)

        if self.is_dlc1() and self.options.Tasksanity:
            ship_shape_region = get_shuffled_region(self, "Ship Shape")
            id_start: int = TASKSANITY_START_ID
            for i in range(self.options.TasksanityCheckCount):
                new_hint_data[id_start+i] = ship_shape_region

        hint_data[self.player] = new_hint_data

    def write_spoiler_header(self, spoiler_handle: TextIO):
        for i in self.chapter_timepiece_costs:
            spoiler_handle.write("Chapter %i Cost: %i\n" % (i, self.chapter_timepiece_costs[ChapterIndex(i)]))

        for hat in self.hat_craft_order:
            spoiler_handle.write("Hat Cost: %s: %i\n" % (hat, self.hat_yarn_costs[hat]))

    def collect(self, state: "CollectionState", item: "Item") -> bool:
        old_count: int = state.count(item.name, self.player)
        change = super().collect(state, item)
        if change and old_count == 0:
            if "Stamp" in item.name:
                if "2 Stamp" in item.name:
                    state.prog_items[self.player]["Stamps"] += 2
                else:
                    state.prog_items[self.player]["Stamps"] += 1
            elif "(Zero Jumps)" in item.name:
                state.prog_items[self.player]["Zero Jumps"] += 1
            elif item.name in hit_list.keys():
                if item.name not in bosses:
                    state.prog_items[self.player]["Enemy"] += 1
                else:
                    state.prog_items[self.player]["Boss"] += 1

        return change

    def remove(self, state: "CollectionState", item: "Item") -> bool:
        old_count: int = state.count(item.name, self.player)
        change = super().remove(state, item)
        if change and old_count == 1:
            if "Stamp" in item.name:
                if "2 Stamp" in item.name:
                    state.prog_items[self.player]["Stamps"] -= 2
                else:
                    state.prog_items[self.player]["Stamps"] -= 1
            elif "(Zero Jumps)" in item.name:
                state.prog_items[self.player]["Zero Jumps"] -= 1
            elif item.name in hit_list.keys():
                if item.name not in bosses:
                    state.prog_items[self.player]["Enemy"] -= 1
                else:
                    state.prog_items[self.player]["Boss"] -= 1

        return change

    def has_yarn(self) -> bool:
        return not self.is_dw_only() and not self.options.HatItems

    def is_hat_precollected(self, hat: HatType) -> bool:
        for item in self.multiworld.precollected_items[self.player]:
            if item.name == hat_type_to_item[hat]:
                return True

        return False

    def is_dlc1(self) -> bool:
        return bool(self.options.EnableDLC1)

    def is_dlc2(self) -> bool:
        return bool(self.options.EnableDLC2)

    def is_dw(self) -> bool:
        return bool(self.options.EnableDeathWish)

    def is_dw_only(self) -> bool:
        return self.is_dw() and bool(self.options.DeathWishOnly)

    def is_dw_excluded(self, name: str) -> bool:
        # don't exclude Seal the Deal if it's our goal
        if self.options.EndGoal.value == EndGoal.option_seal_the_deal and name == "Seal the Deal" \
           and f"{name} - Main Objective" not in self.options.exclude_locations:
            return False

        if name in self.excluded_dws:
            return True

        return f"{name} - Main Objective" in self.options.exclude_locations

    def is_bonus_excluded(self, name: str) -> bool:
        if self.is_dw_excluded(name) or name in self.excluded_bonuses:
            return True

        return f"{name} - All Clear" in self.options.exclude_locations

    @staticmethod
    def interpret_slot_data(slot_data: dict[str, Any]) -> dict[str, Any]:
        # Trigger a regen in UT instead of attempting tracker gen with local yaml
        return slot_data

        # TODO: Add UT defered entrances logic. Looks like most of the act logic is in Rules act_connections already? Would need to tie the deferral to those act completions I guess.
        # Likely need to do time rift deferral as well, since those are tied to both act completion and location availability.
        # Would need to potentially look at the deferred logic for deathwish too... is there anything else?

        # TODO: Add "Glitched" logic (partial implementation done, have some stuff left in expert and need to decide if I want to deal with the random scattered difficulty rules without rule builder)
        # Maybe move the glitched logic rules to a separate file referenced and called by rules, keep rules cleaner and make things more separate for a potential RB refactor?

        # TODO: Add Custom Sorting? Could group region checks together. (I likely won't do this)

        # TODO: Add UT map tracker support (integrate with existing poptracker)
        # Looks like the item names don't match, so would also need to build a translation table

        # TODO: Add any Logic explanation overrides desired (I likely won't do this)

        # TODO: Consider optimizations, cleaner code, make sure changes are clean and meet AP style standards
        
        # TODO: Add hint colors to AHIT client UT integration? Is that already there by default?
        
        # TODO: Consider refactor to Rule Builder to greatly improve/streamline glitch logic. (I likely won't do this, but maybe!)
        # Would need core PR 6401 to mostly follow existing logic using add_rule, would allow for an easier but less clean/ideal refactor
        
        # TODO: add more item groups? Like Relics, Hats, Yarn, Timepieces, etc?
