""" Cities. version 1.2 with graphs. Life simulation. """

from re import split as slt  # for parsing values while creating a new city

# random is everywhere
from random import weibullvariate as wb, gammavariate as gm, randrange as rdr, \
    random as rdm, choice as chc

from json import load, dump  # loading and saving data for running a script
from time import time as tm  # how long does it take to make 1 year
from math import sqrt  # counting root of something
from prettytable import PrettyTable  # printing information by using tables


class World:
    """ This is a place, where everything exists. The __str__ representation is
        a general information about each city. The __len__ representation is a number
        of alive people in each city, which exist in this world
        (Environment.__len__() must exist).

        1 World() -> few Environment() -> more ResourceFacility()
        and more House() -> a lot of Human() """

    world = []  # [Environment(), ...]
    year = 0  # world time

    data = {"years": 0, "seconds per year": []}  # general data for building graphs

    def __init__(self, name):
        self.name = name  # str : name of an object of the class World

    def __len__(self):
        """ for 1 000 000 iterations :::
            sum of an lengths array >>> ~ 3.4 - 3.5 s
            looping >>> ~ 3.85 - 3.9 s
            functools.reduce() >>> ~ 4.9 - 5 s """
        return sum([len(city) for city in self.world])

    def __str__(self):
        return "-" * 22 + f" Object: '{self.name}' (class " \
                          f"'{self.__class__.__name__}'), Residents: {len(self)}. " \
                          f"Year: {self.year} " + "-" * 22

    def cities_creator(self, number):
        print("\nDefault settings for city creation:\nname=input(), people=250, "
              "water~1500, food~1500, wood~1000, ore=0, metal=0, stone=0\nYou can "
              "print a name with any register.\n\nIf you want to create a city with "
              "a default settings, just print: \nname=input()\n\nFor creating a city "
              "with a unique settings, print:\nparameter (people, food, wood, etc.) "
              "and value.\nFor example: name=input(), people=100, metal=1000, ore=500")

        iteration = 0
        while iteration != number:
            name, people, water, food = None, 250, None, None
            wood, ore, metal, stone = None, None, None, None

            city_data = input(f"City : {iteration + 1} / {number}\nData : ")
            reorganized_data = [data for data in slt(r"[=|, |~]", city_data) if data]

            if len(reorganized_data) % 2 != 0:
                print(f"{reorganized_data}\nProbably, you made a mistake. "
                      f"Please, try again.")
            else:
                for index in range(0, len(reorganized_data), 2):
                    parameter = reorganized_data[index].lower()
                    value = reorganized_data[index + 1]

                    if parameter == "name":
                        name = self.city_name_parser(name=value, message="Name")
                    elif parameter == "people":
                        people = integer_checker(value=value, message="People")
                    elif parameter == "water":
                        water = integer_checker(value=value, message="Water")
                    elif parameter == "food":
                        food = integer_checker(value=value, message="Food")
                    elif parameter == "wood":
                        wood = integer_checker(value=value, message="Wood")
                    elif parameter == "ore":
                        ore = integer_checker(value=value, message="Ore")
                    elif parameter == "metal":
                        metal = integer_checker(value=value, message="Metal")
                    elif parameter == "stone":
                        stone = integer_checker(value=value, message="Stone")

                city = Environment(name, water, food, wood, ore, metal, stone)
                for _ in range(people + 1):
                    city.adults.append(
                        Human(age=int(wb(25, 50)), wish_attr=round(wb(2.5, 7.5), 2)))

                self.world.append(city)
                iteration += 1

    def city_name_parser(self, name=None, message=None):
        name = name or input()
        while True:
            if name == "":
                if message:
                    print(f"{message} >>> you can't pass a space blanked name. "
                          "Please, try again.")
                else:
                    print("You can't pass a space blanked name. Please, try again.")

            elif name.title() in [city.name for city in self.world]:
                if message:
                    print(f"{message} >>> this city is already exist. "
                          "Please, try again.")
                else:
                    print("This city is already exist. Please, try again.")
            else:
                return name.title()

            name = input("name=")

    def year_maker(self):
        for city in self.world:
            h_c, p_s, c_s = city.first_block_functions()
            # a first block of functions counting all resources and make dictionaries
            # for other blocks ::: h_c = human costs, p_s = products, c_s = costs.

            f_l = city.second_block_functions(p_s, c_s)
            # a second block of functions, using the city.requests dictionary,
            # checking if a request is true, than appending it to the city.queue.
            # returning f_l = maximum forge level of the city for other blocks.

            city.third_block_functions(h_c, p_s, c_s, f_l)
            # a third block of functions takes all requests from city.queue and
            # placing them into two different arrays => city.alert or city.non_urgent.
            # After it, it makes a plan (city.plan) of deeds people should do.

            city.fourth_block_functions(f_l)
            # a fourth block of functions making all requests from city.plan and
            # try to make all of it. After, finishing the hole building cycle.

            city.fifth_block_functions()
            # a fifth block of functions managing all people changes.


class Environment:
    """ Environment, basically, is a city or a village, depends on the environment
        population. All cities have a unique name. The __str__ representation is
        a general information about quantity of people overall, kids, adults, elders,
        dead people, information about each resource and building with its level.
        (ResourceFacility.__str__() must exist). The __len__ representation is a number
        of alive people in the environment ([kids], [adults] and [elders] must exist).

        All adults can make a new family and append themselves into the
        family dictionary with a unique family index.

        Each city has resources. People can use resources for building or
        upgrading facilities, eating, drinking and etc.

        {requests} dictionary used for sending codes for the life management. """

    requests = {
        "water is out": 1, "food is out": 2, "wood is out": 3, "ore is out": 4,
        "water is out next year": 11, "water trend is strong": 13,
        "water is up too slow": 14, "water is too much": 15,
        "food is out next year": 21, "food trend is strong": 23,
        "food is up too slow": 24, "food is too much": 25,
        "wood is out next year": 31, "wood trend is strong": 33,
        "wood is up too slow": 34, "wood is too much": 35,
        "ore is out next year": 41, "ore trend is strong": 43,
        "ore is up too slow": 44, "ore is too much": 45,
        "metal is out next year": 51, "metal trend is strong": 53,
        "metal is up too slow": 54, "metal is too much": 55,
        "stone is out next year": 61, "stone trend is strong": 63,
        "stone is up too slow": 64, "stone is too much": 65,
        "build the family house": 91, "upgrade the family house": 92,
        "build a house for a human": 93, "no well": 111, "no farm": 121,
        "no hunting house": 122, "no port": 123, "no sawmill": 131, "no mine": 141,
        "no forge": 151, "no quarry": 161, "build well": 211, "upgrade well": 212,
        "build farm": 221, "upgrade farm": 222, "build hunting house": 223,
        "upgrade hunting house": 224, "build port": 225, "upgrade port": 226,
        "build sawmill": 231, "upgrade sawmill": 232, "build mine": 241,
        "upgrade mine": 242, "build forge": 251, "upgrade forge": 252,
        "build quarry": 261, "upgrade quarry": 262, "water need forge": 311,
        "food need forge": 321, "wood need forge": 331, "ore need forge": 341,
        "stone need forge": 361, "stop farm": 421, "stop forge": 451
    }

    def __init__(self, name, water, food, wood, ore, metal, stone):
        self.name = name  # str : name of an object of the class Environment

        # attributes for people ::: class - Human()
        self.kids, self.adults, self.elders = [], [], []  # alive people are here
        self.family_index = 1  # int : a unique family number-key in {families}
        self.families = {}  # {family_index: {"house": house_index,
        #                      "parents": [], "children": []}}
        self.grave = []  # dead people are here

        # attributes for resources
        self.water = water or gm(1500, 1)  # user input or ~ 1500 units
        self.food = food or gm(1500, 1)  # user input or ~ 1500 units
        self.wood = wood or gm(1000, 1)  # user input or ~ 1000 units
        self.ore = ore or 0  # user input or 0
        self.metal = metal or 0  # user input or 0
        self.stone = stone or 0  # user input or 0

        self.resources = {"water": self.water, "food": self.food, "wood": self.wood,
                          "ore": self.ore, "metal": self.metal, "stone": self.stone}

        # attributes for buildings and houses
        self.building_index = 1  # int : a unique building number-key in {buildings}
        self.buildings = {}  # {building_index: ResourceFacility()}

        self.house_index = 1  # int : a unique house number-key in {houses}
        self.houses = {}  # {house_index: House()}

        self.brigades = []  # people, that build any facility in a current year

        # resource_trend, requests and management
        self.queue = []  # an array of requests for making alert and non_urgent
        self.alert = []  # an array of the most important problems to solve
        self.non_urgent = []  # an array of problems that are non-urgent
        self.plan = []  # step by step maker

        # general data for building graphs
        self.data = {
            "kids": [], "adults": [], "elders": [], "people in the city": [],
            "families": [], "grave": [], "average life": None, "water": [],
            "food": [], "wood": [], "ore": [], "metal": [], "stone": [],
            "buildings": [], "houses": []}

    def __len__(self):
        return len(self.kids) + len(self.adults) + len(self.elders)

    def __str__(self):
        return f"{self.name} of the class '{self.__class__.__name__}' with " \
               f"{len(self)} alive people:\n[People -> families = " \
               f"{len(self.families)}; kids = {len(self.kids)}; adults = " \
               f"{len(self.adults)}; elders = {len(self.elders)}; grave = " \
               f"{len(self.grave)}]\n[Resources -> water = {round(self.water, 2)}" \
               f"; food = {round(self.food, 2)}; wood = {round(self.wood, 2)}; " \
               f"ore = {round(self.ore, 2)}; metal = {round(self.metal, 2)}" \
               f"; stone = {round(self.stone, 2)}]\n[Buildings -> houses = " \
               f"{len(self.houses)}, facilities = {len(self.buildings)}]\n" + \
               "\n".join(f"{hs}" for hs in self.houses.values()) + "\n\n" + \
               "\n".join(f"{bg}" for bg in self.buildings.values()) + "\n"

    def first_block_functions(self):
        self.queue = []
        self.alert, self.non_urgent = [], []
        self.plan = []

        h_c = self.costs_of_human_life_counter()
        p_s, c_s, result, account_flag = self.production_counter()

        if account_flag:
            self.finishing_first_block(result)
            return h_c, p_s, c_s
        else:
            self.accounting_function(p_s, c_s, result)
            self.finishing_first_block(result)
            return h_c, p_s, c_s

    def costs_of_human_life_counter(self):
        h_costs = {"water": len(self), "food": len(self), "wood": 0}

        for array in (self.kids, self.adults, self.elders):
            for human in array:
                if not human.house_index:
                    h_costs["wood"] += 1

        for house in self.houses.values():
            h_costs["wood"] += house.info[house.level]["cost: wood"]

        for res, value in h_costs.items():
            self.resources[res] -= value
        return h_costs

    def production_counter(self):
        p_s = {"water": 0, "food": 0, "wood": 0, "ore": 0, "metal": 0, "stone": 0}
        c_s = {"water": 0, "food": 0, "wood": 0, "ore": 0}

        for building in self.buildings.values():
            building.assets_and_liabilities_counter(p_s, c_s)
            building.more_experience_workers()

        result = {"water": 0, "food": 0, "wood": 0, "ore": 0, "metal": 0, "stone": 0}
        for res in result:
            result[res] = self.resources[res] + p_s[res] - c_s.get(res, 0)

        if all(x >= 0 for x in result.values()):
            return p_s, c_s, result, True
        return p_s, c_s, result, False

    def finishing_first_block(self, result):
        for res, value in result.items():
            self.resources[res] = value

        self.water, self.food = self.resources["water"], self.resources["food"]
        self.wood, self.ore = self.resources["wood"], self.resources["ore"]
        self.metal, self.stone = self.resources["metal"], self.resources["stone"]

    def accounting_function(self, p_s, c_s, result):
        if result["water"] < 0:
            self.queue.append(self.requests["water is out"])
            result["water"] = 0

        if result["food"] < 0:
            self.queue.append(self.requests["food is out"])
            result["food"] = 0

        if result["wood"] < 0:
            self.queue.append(self.requests["wood is out"])
            result["wood"] = 0

        if result["ore"] < 0:
            self.queue.append(self.requests["ore is out"])
            coefficient = c_s["ore"] / p_s["metal"]
            while result["ore"] < 0:
                p_s["metal"] -= 1
                c_s["ore"] -= coefficient
                result["metal"] -= 1
                result["ore"] += coefficient

    def second_block_functions(self, p_s, c_s):
        self.slow_growing_up_resource_requests_parser(p_s)
        self.most_of_resource_requests_parser(p_s, c_s)
        self.people_requests_parser()
        self.people_making_brigades_for_building_new_facilities()
        f_l = self.forge_level_parser()
        return f_l

    def slow_growing_up_resource_requests_parser(self, p_s):
        income = 0
        for product in p_s.values():
            income += product

        if income != 0:
            for res, value in p_s.items():
                if value / income <= 0.05:
                    self.queue.append(self.requests[f"{res} is up too slow"])
                elif value / income >= 0.5:
                    self.queue.append(self.requests[f"{res} is too much"])

    def most_of_resource_requests_parser(self, p_s, c_s):
        for res, value in self.resources.items():
            if self.resources[res] + p_s[res] - c_s.get(res, 0) < 0:
                self.queue.append(self.requests[f"{res} is out next year"])
            else:
                trend = self.resources[res] + 10 * (p_s[res] - c_s.get(res, 0))

                if trend <= 0 or self.resources[res] > 10 * trend:
                    self.queue.append(self.requests[f"{res} trend is strong"])

        for bld, class_ in {"well": Well, "farm": Farm, "hunting house": HuntingHouse,
                            "port": Port, "sawmill": Sawmill, "mine": Mine,
                            "quarry": Quarry, "forge": Forge}.items():
            if class_ not in [type(clb) for clb in self.buildings.values()]:
                self.queue.append(self.requests[f"no {bld}"])

    def people_requests_parser(self):
        for family in self.families.values():
            if not family["house"]:
                self.queue.append(self.requests["build the family house"])
            else:
                house = self.houses[family["house"]]
                if len(house.tenants) >= House.info[house.level]["max p_l"]:
                    self.queue.append(self.requests["upgrade the family house"])

        for array in (self.adults, self.elders):
            for human in array:
                if not human.house_index and not human.family_index:
                    self.queue.append(self.requests["build a house for a human"])

    def people_making_brigades_for_building_new_facilities(self):
        for array in (self.kids, self.adults, self.elders):
            for human in array:
                if 14 <= human.age <= 70 and not human.builder_status:
                    self.brigades.append(human)
                    human.builder_status = True

    def forge_level_parser(self):
        forge_level = 0
        for building in self.buildings.values():
            if "Forge" in building.name and forge_level < building.level:
                forge_level = building.level
        return forge_level

    def third_block_functions(self, h_c, p_s, c_s, f_l):
        ch_s = {"water": 0, "food": 0, "wood": 0, "ore": 0, "metal": 0, "stone": 0}
        copy = {k: v for k, v in self.resources.items()}

        self.alert_or_non_urgent_parser()
        self.result_of_the_year_for_people()
        self.the_most_important_alerts_parser(h_c, p_s, c_s, f_l, ch_s, copy)
        self.all_other_alerts_parser(f_l, ch_s, copy)
        self.all_non_urgent_parser(h_c, p_s, c_s, f_l, ch_s, copy)

    def alert_or_non_urgent_parser(self):
        for request in (1, 2, 3, 4, 11, 21, 31, 41):
            if request in self.queue:
                self.alert.append(request)

        self.request_humans_houses_parser(self.alert, 5)

        for request in (111, 121, 122, 123, 131, 141, 151, 161):
            if request in self.queue:
                self.alert.append(request)

        for request in (14, 24, 34, 44, 54, 64):
            if request in self.queue:
                self.non_urgent.append(request)

        self.request_humans_houses_parser(self.non_urgent, 3)

        for request in (13, 23, 33, 43, 53, 63):
            if request in self.queue:
                self.non_urgent.append(request)

    def request_humans_houses_parser(self, sending, number):
        if len(self.families) > 0:
            if self.requests["wood is too much"] in self.queue:
                for _ in range(self.queue.count(91)):
                    sending.append(self.requests["build the family house"])
                for _ in range(self.queue.count(92)):
                    sending.append(self.requests["upgrade the family house"])

            else:
                for _ in range(self.queue.count(91) // number):
                    sending.append(self.requests["build the family house"])
                for _ in range(self.queue.count(92) // number):
                    sending.append(self.requests["upgrade the family house"])

        if self.requests["wood is too much"] in self.queue:
            for _ in range(self.queue.count(93)):
                sending.append(self.requests["build a house for a human"])
        else:
            add = 1
            if self.queue.count(91) >= 15:
                add = 5
            for _ in range(self.queue.count(93) // (number * add)):
                sending.append(self.requests["build a house for a human"])

    def result_of_the_year_for_people(self):
        if 1 not in self.queue and 2 not in self.queue and 3 not in self.queue:
            for array in (self.kids, self.adults, self.elders):
                for human in array:
                    human.death = 0.75

        for elem in (1, 2, 3):
            if elem in self.queue:
                for array in (self.kids, self.adults, self.elders):
                    for human in array:
                        human.death -= 0.000025

    def the_most_important_alerts_parser(self, h_c, p_s, c_s, f_l, ch_s, copy):
        """ 1, 2, 3, 4, 11, 21, 31, 41 """
        self.sawmill_builder_template(ch_s, copy)
        self.well_builder_template(ch_s, copy)
        self.farm_builder_template(ch_s, copy)
        self.hunting_house_builder_template(ch_s, copy)
        self.port_builder_template(ch_s, copy)

        if self.requests["water is out"] in self.alert:
            self.plan.append(self.requests["stop farm"])
            self.water_template(h_c, p_s, c_s, f_l, ch_s, copy, 50)

        if self.requests["food is out"] in self.alert:
            self.food_template(h_c, p_s, c_s, f_l, ch_s, copy, 50)

        if self.requests["wood is out"] in self.alert:
            self.wood_template(h_c, p_s, c_s, f_l, ch_s, copy, 50)

        if self.requests["ore is out"] in self.alert:
            self.plan.append(self.requests["stop forge"])
            self.ore_template(h_c, p_s, c_s, f_l, ch_s, copy, 25)

        if self.requests["water is out next year"] in self.alert:
            self.plan.append(self.requests["stop farm"])
            self.water_template(h_c, p_s, c_s, f_l, ch_s, copy, 25)

        if self.requests["food is out next year"] in self.alert:
            self.food_template(h_c, p_s, c_s, f_l, ch_s, copy, 25)

        if self.requests["wood is out next year"] in self.alert:
            self.wood_template(h_c, p_s, c_s, f_l, ch_s, copy, 25)

        if self.requests["ore is out next year"] in self.alert:
            self.plan.append(self.requests["stop forge"])
            self.ore_template(h_c, p_s, c_s, f_l, ch_s, copy, 25)

        self.people_are_soo_people()

    def sawmill_builder_template(self, ch_s, copy):
        if self.requests["no sawmill"] in self.alert:
            self.building_planer("build sawmill", ch_s, "wood", Sawmill, copy,
                                 else_status=True)

    def building_planer(self, request, ch_s, res, obj, copy, else_status=False):
        if copy["wood"] - obj.info[1]["build"]["wood"] >= 0:
            copy["wood"] -= obj.info[1]["build"]["wood"]
            ch_s[res] += (obj.info[1]["max w_s"] * obj.info[1]["jun"])
            self.plan.append(self.requests[request])
        elif else_status and copy["wood"] < 0:
            copy["wood"] = 0
            ch_s[res] += (obj.info[1]["max w_s"] * obj.info[1]["jun"])
            self.plan.append(self.requests[request])

    def well_builder_template(self, ch_s, copy):
        if self.requests["no well"] in self.alert:
            self.building_planer("build well", ch_s, "water", Well, copy,
                                 else_status=True)

    def farm_builder_template(self, ch_s, copy):
        if self.requests["no farm"] in self.alert:
            self.building_planer("build farm", ch_s, "food", Farm, copy,
                                 else_status=True)

    def hunting_house_builder_template(self, ch_s, copy):
        if self.requests["no hunting house"] in self.alert:
            self.building_planer("build hunting house", ch_s, "food",
                                 HuntingHouse, copy, else_status=True)

    def port_builder_template(self, ch_s, copy):
        if self.requests["no port"] in self.alert:
            self.building_planer("build port", ch_s, "food", Port, copy,
                                 else_status=True)

    def water_template(self, h_c, p_s, c_s, f_l, ch_s, copy, plus):
        for index in self.an_array_of_indexes_for_upgrade(Well):
            well = self.buildings[index]
            if well.level != 15:
                if self.upgrading_planer(well, f_l, ch_s, "upgrade well", copy, "water"):
                    if self.resource_checker(h_c, p_s, c_s, "water", ch_s, plus):
                        break
                else:
                    if well.info[well.level + 1]["build"]["Forge"] > f_l:
                        self.plan.append(self.requests["water need forge"])
        else:
            if not self.resource_checker(h_c, p_s, c_s, "water", ch_s, plus):
                if copy["wood"] >= Well.info[1]["build"]["wood"]:
                    self.building_planer("build well", ch_s, "water", Well, copy)

        self.random_behaviour(10, "build well", "build well", "upgrade well",
                              "upgrade well", "upgrade well", "build sawmill",
                              "upgrade sawmill")
        self.resource_navigation_template("water")

    def an_array_of_indexes_for_upgrade(self, obj):
        indexes = [i for i, b in self.buildings.items() if b is type(obj)]
        return indexes[::-1]

    def upgrading_planer(self, obj, forge_level, ch_s, request, copy, resource):
        upgrade_flag = True

        for res, value in obj.info[obj.level + 1]["build"].items():
            if res == "Forge" and forge_level < value:
                upgrade_flag = False
            elif copy[res] - value < 0:
                upgrade_flag = False

        if upgrade_flag:
            for res, value in obj.info[obj.level + 1]["build"].items():
                if res != "Forge":
                    copy[res] -= value

            ch_s[resource] -= \
                (obj.info[obj.level]["max w_s"] * obj.info[obj.level]["jun"])
            ch_s[resource] += \
                (obj.info[obj.level + 1]["max w_s"] * obj.info[obj.level + 1]["jun"])

            self.plan.append(self.requests[request])
            return True
        return False

    @staticmethod
    def resource_checker(h_c, p_s, c_s, res, ch_s, limit):
        if (p_s[res] - c_s.get(res, 0) - h_c.get(res, 0) + ch_s[res]) >= limit:
            return True
        return False

    def random_behaviour(self, limit, *args):
        for _ in range(rdr(0, limit + 1)):
            if rdm() >= 0.6:
                self.plan.append(self.requests[chc([*args])])

    def resource_navigation_template(self, res):
        if self.requests[f"{res} is out next year"] in self.alert:
            self.alert.remove(self.requests[f"{res} is out next year"])

        for request in (f"{res} trend is strong", f"{res} is up too slow"):
            if self.requests[request] in self.non_urgent:
                self.non_urgent.remove(self.requests[request])

    def food_template(self, h_c, p_s, c_s, f_l, ch_s, copy, plus):
        if self.farm_parser_template(ch_s, copy, h_c, p_s, c_s, f_l, plus):
            if self.hunting_house_parser_template(ch_s, copy, h_c, p_s, c_s, f_l, plus):
                self.port_parser_template(ch_s, copy, h_c, p_s, c_s, f_l, plus)

        self.random_behaviour(20, "build farm", "build hunting house", "build port",
                              "upgrade farm", "upgrade hunting house", "upgrade port",
                              "upgrade hunting house", "upgrade port", "build sawmill",
                              "upgrade sawmill")
        self.resource_navigation_template("food")

    def farm_parser_template(self, ch_s, copy, h_c, p_s, c_s, f_l, plus):
        if self.requests["stop farm"] in self.plan:
            return True

        for index in self.an_array_of_indexes_for_upgrade(Farm):
            farm = self.buildings[index]
            if farm.level != 15:
                if self.upgrading_planer(farm, f_l, ch_s, "upgrade farm", copy, "food"):
                    if self.resource_checker(h_c, p_s, c_s, "food", ch_s, plus):
                        return False
                else:
                    if farm.info[farm.level + 1]["build"]["Forge"] > f_l:
                        self.plan.append(self.requests["food need forge"])
        else:
            if not self.resource_checker(h_c, p_s, c_s, "food", ch_s, plus):
                if copy["wood"] >= Farm.info[1]["build"]["wood"]:
                    self.building_planer("build farm", ch_s, "food", Farm, copy)

        if self.resource_checker(h_c, p_s, c_s, "food", ch_s, plus):
            return False
        return True

    def hunting_house_parser_template(self, ch_s, copy, h_c, p_s, c_s, f_l, plus):
        for index in self.an_array_of_indexes_for_upgrade(HuntingHouse):
            hunt = self.buildings[index]
            if hunt.level != 10:
                if self.upgrading_planer(hunt, f_l, ch_s, "upgrade hunting house",
                                         copy, "food"):
                    if self.resource_checker(h_c, p_s, c_s, "food", ch_s, plus):
                        return False
                else:
                    if hunt.info[hunt.level + 1]["build"]["Forge"] > f_l:
                        self.plan.append(self.requests["food need forge"])
        else:
            if not self.resource_checker(h_c, p_s, c_s, "food", ch_s, plus):
                if copy["wood"] >= HuntingHouse.info[1]["build"]["wood"]:
                    self.building_planer("build hunting house", ch_s,
                                         "food", HuntingHouse, copy)

        if self.resource_checker(h_c, p_s, c_s, "food", ch_s, plus):
            return False
        return True

    def port_parser_template(self, ch_s, copy, h_c, p_s, c_s, f_l, plus):
        for index in self.an_array_of_indexes_for_upgrade(Port):
            port = self.buildings[index]
            if port.level != 12:
                if self.upgrading_planer(port, f_l, ch_s, "upgrade port", copy, "food"):
                    if self.resource_checker(h_c, p_s, c_s, "food", ch_s, plus):
                        break
                else:
                    if port.info[port.level + 1]["build"]["Forge"] > f_l:
                        self.plan.append(self.requests["food need forge"])
        else:
            if not self.resource_checker(h_c, p_s, c_s, "food", ch_s, plus):
                if copy["wood"] >= Port.info[1]["build"]["wood"]:
                    self.building_planer("build port", ch_s, "food", Port, copy)

    def wood_template(self, h_c, p_s, c_s, f_l, ch_s, copy, plus):
        for index in self.an_array_of_indexes_for_upgrade(Sawmill):
            sawmill = self.buildings[index]
            if sawmill.level != 15:
                if self.upgrading_planer(sawmill, f_l, ch_s, "upgrade sawmill",
                                         copy, "wood"):
                    if self.resource_checker(h_c, p_s, c_s, "wood", ch_s, plus):
                        break
                else:
                    if sawmill.info[sawmill.level + 1]["build"]["Forge"] > f_l:
                        self.plan.append(self.requests["wood need forge"])
        else:
            if not self.resource_checker(h_c, p_s, c_s, "wood", ch_s, plus):
                if copy["wood"] >= Sawmill.info[1]["build"]["wood"]:
                    self.building_planer("build sawmill", ch_s, "wood", Sawmill, copy)

        self.random_behaviour(10, "build sawmill", "upgrade sawmill", "upgrade sawmill")
        self.resource_navigation_template("wood")

    def ore_template(self, h_c, p_s, c_s, f_l, ch_s, copy, plus):
        for index in self.an_array_of_indexes_for_upgrade(Mine):
            mine = self.buildings[index]
            if mine.level != 10:
                if self.upgrading_planer(mine, f_l, ch_s, "upgrade mine", copy, "ore"):
                    if self.resource_checker(h_c, p_s, c_s, "ore", ch_s, plus):
                        break
                else:
                    if mine.info[mine.level + 1]["build"]["Forge"] > f_l:
                        self.plan.append(self.requests["ore need forge"])
        else:
            if not self.resource_checker(h_c, p_s, c_s, "ore", ch_s, plus):
                if copy["wood"] >= Mine.info[1]["build"]["wood"]:
                    self.building_planer("build mine", ch_s, "ore", Mine, copy)

        self.random_behaviour(10, "build mine", "upgrade mine", "upgrade mine",
                              "build sawmill", "upgrade sawmill")
        self.resource_navigation_template("ore")

    def people_are_soo_people(self):
        for _ in range(10):
            if rdm() >= 0.65:
                self.plan.append(self.requests[chc([
                    "build well", "build well", "upgrade well", "upgrade well",
                    "upgrade well", "upgrade well", "build farm", "build farm",
                    "upgrade farm", "upgrade farm", "upgrade farm",
                    "build hunting house", "build hunting house",
                    "upgrade hunting house", "upgrade hunting house",
                    "upgrade hunting house", "upgrade hunting house", "build port",
                    "build port", "upgrade port", "upgrade port", "upgrade port",
                    "upgrade port", "build sawmill", "build sawmill",
                    "upgrade sawmill", "upgrade sawmill", "upgrade sawmill",
                    "upgrade sawmill", "upgrade sawmill", "build mine", "upgrade mine",
                    "upgrade mine", "build quarry", "upgrade quarry", "upgrade quarry",
                    "build forge", "upgrade forge", "upgrade forge"])])

    def all_other_alerts_parser(self, f_l, ch_s, copy):
        """ 91, 92, 93, 111, 121, 122, 123, 131, 141, 151, 161 """
        if self.requests["build the family house"] in self.alert:
            self.house_building_planer("build the family house", copy, self.alert)

        if self.requests["upgrade the family house"] in self.alert:
            self.house_upgrading_planer(self.alert, f_l, copy,
                                        "upgrade the family house")

        if self.requests["build a house for a human"] in self.alert:
            self.house_building_planer("build a house for a human", copy, self.alert)

        self.mine_builder_template(ch_s, copy)
        self.quarry_builder_template(ch_s, copy)
        self.forge_builder_template(ch_s, copy)

        self.people_are_soo_people()

    def house_building_planer(self, request, copy, place):
        for _ in range(place.count(self.requests[request])):
            if copy["wood"] - House.info[1]["build"]["wood"] >= 0:
                self.plan.append(self.requests[request])
                copy["wood"] -= House.info[1]["build"]["wood"]

    def house_upgrading_planer(self, place, forge_level, copy, request):
        for _ in range(place.count(self.requests[request])):
            for house in self.houses.values():
                if house.level != 5:
                    if len(house.tenants) >= house.info[house.level]["max p_l"]:
                        upgrade_flag = True

                        for res, val in house.info[house.level + 1]["build"].items():
                            if res == "Forge":
                                if forge_level < val:
                                    upgrade_flag = False
                            elif copy[res] - val < 0:
                                upgrade_flag = False

                        if upgrade_flag:
                            for res, val in house.info[house.level + 1]["build"].items():
                                if res != "Forge":
                                    copy[res] -= val
                            self.plan.append(self.requests[request])

    def mine_builder_template(self, ch_s, copy):
        if self.requests["no mine"] in self.alert:
            self.building_planer("build mine", ch_s, "ore", Mine, copy)

    def quarry_builder_template(self, ch_s, copy):
        if self.requests["no quarry"] in self.alert:
            self.building_planer("build quarry", ch_s, "stone", Quarry, copy)

    def forge_builder_template(self, ch_s, copy):
        if self.requests["no forge"] in self.alert:
            self.building_planer("build forge", ch_s, "metal", Forge, copy)

    def all_non_urgent_parser(self, h_c, p_s, c_s, f_l, ch_s, copy):
        """ 14, 24, 34, 44, 54, 64, 91, 92, 93, 13, 23, 33, 43 """
        self.people_are_soo_people()

        if self.requests["water is up too slow"] in self.non_urgent:
            self.water_template(h_c, p_s, c_s, f_l, ch_s, copy, 0)

        if self.requests["food is up too slow"] in self.non_urgent:
            self.food_template(h_c, p_s, c_s, f_l, ch_s, copy, 0)

        if self.requests["wood is up too slow"] in self.non_urgent:
            self.wood_template(h_c, p_s, c_s, f_l, ch_s, copy, 0)

        if self.requests["ore is up too slow"] in self.non_urgent:
            self.ore_template(h_c, p_s, c_s, f_l, ch_s, copy, 0)

        if self.requests["metal is up too slow"] in self.non_urgent:
            self.metal_template(h_c, p_s, c_s, f_l, ch_s, copy, 0)

        if self.requests["stone is up too slow"] in self.non_urgent:
            self.stone_template(h_c, p_s, c_s, f_l, ch_s, copy, 0)

        if self.requests["build the family house"] in self.non_urgent:
            self.house_building_planer("build the family house", copy, self.non_urgent)

        if self.requests["upgrade the family house"] in self.non_urgent:
            self.house_upgrading_planer(self.non_urgent, f_l, copy,
                                        "upgrade the family house")

        if self.requests["build a house for a human"] in self.non_urgent:
            self.house_building_planer("build a house for a human",
                                       copy, self.non_urgent)

        if self.requests["water trend is strong"] in self.non_urgent:
            self.water_template(h_c, p_s, c_s, f_l, ch_s, copy, -50)

        if self.requests["food trend is strong"] in self.non_urgent:
            self.food_template(h_c, p_s, c_s, f_l, ch_s, copy, -50)

        if self.requests["wood trend is strong"] in self.non_urgent:
            self.wood_template(h_c, p_s, c_s, f_l, ch_s, copy, -50)

        if self.requests["ore trend is strong"] in self.non_urgent:
            self.ore_template(h_c, p_s, c_s, f_l, ch_s, copy, -50)

        self.people_are_soo_people()

    def metal_template(self, h_c, p_s, c_s, f_l, ch_s, copy, plus):
        for index in self.an_array_of_indexes_for_upgrade(Forge):
            forge = self.buildings[index]
            if forge.level != 15:
                if self.upgrading_planer(forge, f_l, ch_s, "upgrade forge",
                                         copy, "metal"):
                    if self.resource_checker(h_c, p_s, c_s, "metal", ch_s, plus):
                        break
        else:
            if not self.resource_checker(h_c, p_s, c_s, "metal", ch_s, plus):
                if copy["wood"] >= Forge.info[1]["build"]["wood"]:
                    self.building_planer("build forge", ch_s, "metal", Forge, copy)

        self.random_behaviour(10, "build forge", "upgrade forge", "upgrade forge",
                              "build mine", "upgrade mine")
        self.resource_navigation_template("metal")

    def stone_template(self, h_c, p_s, c_s, f_l, ch_s, copy, plus):
        for index in self.an_array_of_indexes_for_upgrade(Quarry):
            quarry = self.buildings[index]
            if quarry.level != 10:
                if self.upgrading_planer(quarry, f_l, ch_s, "upgrade quarry",
                                         copy, "stone"):
                    if self.resource_checker(h_c, p_s, c_s, "stone", ch_s, plus):
                        break
                else:
                    if quarry.info[quarry.level + 1]["build"]["Forge"] > f_l:
                        self.plan.append(self.requests["stone need forge"])
        else:
            if not self.resource_checker(h_c, p_s, c_s, "stone", ch_s, plus):
                if copy["wood"] >= Quarry.info[1]["build"]["wood"]:
                    self.building_planer("build quarry", ch_s, "stone", Quarry, copy)

        self.random_behaviour(5, "build quarry", "upgrade quarry", "upgrade quarry")
        self.resource_navigation_template("stone")

    def fourth_block_functions(self, f_l):
        self.empty_facilities_parser()
        ore_flag = self.ore_is_too_much()
        self.plan_maker(f_l)
        Human.people_did_not_build_any_buildings(self)
        self.buildings_need_more_workers(ore_flag)
        self.house_management()

    def empty_facilities_parser(self):
        if len(self.buildings) == 0:
            return None

        counter = \
            [len(bg.workers) for bg in self.buildings.values() if len(bg.workers) == 0]
        if len(counter) / len(self.buildings) >= 0.15:

            commands = [15, 25, 35, 45, 55, 65, 91, 92, 93, 212, 222, 224, 226,
                        232, 242, 252, 262, 311, 321, 331, 341, 361, 421, 451]
            self.plan = [cmd for cmd in self.plan if cmd in commands]

    def ore_is_too_much(self):
        if self.resources["ore"] >= 5000 and self.resources["metal"] <= 1000:
            return True
        return False

    def plan_maker(self, f_l):
        for element in self.plan:
            if element == self.requests["build the family house"]:
                if Human.people_want_to_build_new_facilities(self, 5):
                    house = House.a_house_builder(self)
                    if house:
                        self.houses[self.house_index] = house
                        self.house_index += 1

            if element == self.requests["upgrade the family house"]:
                for value in self.families.values():
                    if value["house"]:
                        house = self.houses[value["house"]]
                        if house.level != 5:
                            if len(house.tenants) >= house.info[house.level]["max p_l"]:

                                if Human.people_want_to_build_new_facilities(
                                        self, house.level + 2):
                                    house.upgrade_the_house(self, f_l)
                                    break

            if element == self.requests["build a house for a human"]:
                if Human.people_want_to_build_new_facilities(self, 5):
                    house = House.a_house_builder(self, family_flag=False,
                                                  human_flag=True)
                    if house:
                        self.houses[self.house_index] = house
                        self.house_index += 1

            if element == self.requests["build well"]:
                if Human.people_want_to_build_new_facilities(self, 4):
                    well = Well.building_a_new_facility(self)
                    if well:
                        self.buildings[self.building_index] = well
                        self.building_index += 1

            if element == self.requests["upgrade well"]:
                for value in self.buildings.values():
                    if type(value) is Well:
                        if Human.people_want_to_build_new_facilities(
                                self, value.level):
                            if value.upgrade_the_facility(self, f_l):
                                break

            if element == self.requests["build farm"]:
                if self.requests["stop farm"] not in self.plan:
                    if Human.people_want_to_build_new_facilities(self, 4):
                        farm = Farm.building_a_new_facility(self)
                        if farm:
                            self.buildings[self.building_index] = farm
                            self.building_index += 1

            if element == self.requests["upgrade farm"]:
                for value in self.buildings.values():
                    if type(value) is Farm:
                        if Human.people_want_to_build_new_facilities(
                                self, value.level):
                            if value.upgrade_the_facility(self, f_l):
                                break

            if element == self.requests["build hunting house"]:
                if Human.people_want_to_build_new_facilities(self, 4):
                    hunting_house = HuntingHouse.building_a_new_facility(self)
                    if hunting_house:
                        self.buildings[self.building_index] = hunting_house
                        self.building_index += 1

            if element == self.requests["upgrade hunting house"]:
                for value in self.buildings.values():
                    if type(value) is HuntingHouse:
                        if Human.people_want_to_build_new_facilities(
                                self, value.level):
                            if value.upgrade_the_facility(self, f_l):
                                break

            if element == self.requests["build port"]:
                if Human.people_want_to_build_new_facilities(self, 4):
                    port = Port.building_a_new_facility(self)
                    if port:
                        self.buildings[self.building_index] = port
                        self.building_index += 1

            if element == self.requests["upgrade port"]:
                for value in self.buildings.values():
                    if type(value) is Port:
                        if Human.people_want_to_build_new_facilities(
                                self, value.level):
                            if value.upgrade_the_facility(self, f_l):
                                break

            if element == self.requests["build sawmill"]:
                if Human.people_want_to_build_new_facilities(self, 4):
                    sawmill = Sawmill.building_a_new_facility(self)
                    if sawmill:
                        self.buildings[self.building_index] = sawmill
                        self.building_index += 1

            if element == self.requests["upgrade sawmill"]:
                for value in self.buildings.values():
                    if type(value) is Sawmill:
                        if Human.people_want_to_build_new_facilities(
                                self, value.level):
                            if value.upgrade_the_facility(self, f_l):
                                break

            if element == self.requests["build mine"]:
                if Human.people_want_to_build_new_facilities(self, 4):
                    mine = Mine.building_a_new_facility(self)
                    if mine:
                        self.buildings[self.building_index] = mine
                        self.building_index += 1

            if element == self.requests["upgrade mine"]:
                for value in self.buildings.values():
                    if type(value) is Mine:
                        if Human.people_want_to_build_new_facilities(
                                self, value.level):
                            if value.upgrade_the_facility(self, f_l):
                                break

            if element == self.requests["build quarry"]:
                if Human.people_want_to_build_new_facilities(self, 4):
                    quarry = Quarry.building_a_new_facility(self)
                    if quarry:
                        self.buildings[self.building_index] = quarry
                        self.building_index += 1

            if element == self.requests["upgrade quarry"]:
                for value in self.buildings.values():
                    if type(value) is Quarry:
                        if Human.people_want_to_build_new_facilities(
                                self, value.level):
                            if value.upgrade_the_facility(self, f_l):
                                break

            if element == self.requests["build forge"]:
                if self.requests["stop forge"] not in self.plan:
                    if Human.people_want_to_build_new_facilities(self, 4):
                        forge = Forge.building_a_new_facility(self)
                        if forge:
                            self.buildings[self.building_index] = forge
                            self.building_index += 1

            if element in (self.requests["upgrade forge"],
                           self.requests["water need forge"],
                           self.requests["food need forge"],
                           self.requests["wood need forge"],
                           self.requests["ore need forge"],
                           self.requests["stone need forge"]):
                for value in self.buildings.values():
                    if type(value) is Forge:
                        if Human.people_want_to_build_new_facilities(
                                self, value.level):
                            if value.upgrade_the_facility(self, f_l):
                                break

    def buildings_need_more_workers(self, ore_flag):
        for index, building in self.buildings.items():
            for worker in building.workers:
                worker.job_status = None
            building.workers = []

        for index, building in self.buildings.items():
            if type(building) is Mine and ore_flag:
                continue

            limit = self.resource_is_too_much_parser(building) or \
                building.info[building.level]["max w_s"]

            if len(building.workers) < limit:
                for array in (self.adults, self.elders):
                    for human in array:
                        if not human.job_status:
                            if len(building.workers) < limit:
                                building.workers.append(human)
                                human.job_status = index
                            else:
                                break

    def resource_is_too_much_parser(self, building):
        for request, obj in {"water is too much": Well,
                             "food is too much": [Farm, HuntingHouse, Port],
                             "wood is too much": Sawmill, "ore is too much": Mine,
                             "metal is too much": Forge,
                             "stone is too much": Quarry}.items():

            if request == "food is too much":
                for oj in obj:
                    if building is type(oj) and self.requests[request] in self.plan:
                        return building.info[building.level]["max w_s"] // 2
            else:
                if building is type(obj) and self.requests[request] in self.plan:
                    return building.info[building.level]["max w_s"] // 2

    def house_management(self):
        for index, house in self.houses.items():
            if len(house.tenants) == 0:
                for family in self.families.values():
                    if not family["house"]:
                        family["house"] = index
                        for human in ([*family["parents"], *family["children"]]):
                            human.house_index = index
                            house.tenants.append(human)
                        break

    def fifth_block_functions(self):
        for array in (self.kids, self.adults, self.elders):
            for human in array:
                human.age += 1
                human.attractiveness = human.attractiveness_parameter_changer()
                human.wish_attr = human.wish_attractiveness_parameter_changer()

            Human.moving_people_from_array_to_array(self)
            Human.people_want_to_make_families(self)
            Human.people_want_to_make_new_people(self)
            Human.dead_function_by_age(self)
            Human.removing_all_families_without_parents(self)


class ResourceFacility:
    """ Core class for inheriting for other facilities that bring resources. Objects
        of this class stored inside of [Environment.buildings]. The __str__
        representation is a general information about level and quantity of workers.

        Every object of class "ResourceFacility" has its own dictionary with all
        necessary information inside of it. Dictionary consists of:

        "max w_s" = int : maximum amount of workers on this level.
        "jun" = float : how many resources will make 1 non-professional worker.
        "pro" = float : how many resources will make 1 professional worker.
        "build" = {} : {"resource" or "facility": (amount of resources or level) = int}.

        All : [Farm, HuntingHouse, Port, Well, Sawmill, Mine, Quarry, Forge]. """

    def __init__(self, name, index, level=1):
        self.name = name  # str : name of an object of the class ResourceFacility
        self.index = index  # int : is a Environment.building_index
        self.level = level  # int : level of the facility
        self.workers = []  # amount of current workers

    def __str__(self):
        return f"{self.name} ({self.level}), amount of workers = {len(self.workers)}"

    def assets_and_liabilities_counter(self, assets, liabilities, costs, profession,
                                       years, place, minimum, maximum, resource):
        """ random.randrange ~~~ random.choice ~~< random.randint """
        for worker in self.workers:
            if worker.employment_history[profession] >= years:
                assets[resource] += place[self.level]["pro"] \
                                    * rdr(minimum, maximum) / 100
                assets[resource] = round(assets[resource], 2)

                if profession in ("farmer", "blacksmith"):
                    for res, value in costs.items():
                        liabilities[res] += place[self.level]["pro"] * value \
                                            * rdr(75, 126) / 100
                        liabilities[res] = round(liabilities[res], 2)

            else:
                assets[resource] += place[self.level]["jun"] * rdr(minimum, 101) / 100
                assets[resource] = round(assets[resource], 2)

                if profession in ("farmer", "blacksmith"):
                    for res, value in costs.items():
                        liabilities[res] += place[self.level]["jun"] * value \
                                            * rdr(85, 136) / 100
                        liabilities[res] = round(liabilities[res], 2)

    def more_experience_workers(self, profession):
        for worker in self.workers:
            worker.employment_history[profession] += 1

    @staticmethod
    def building_a_new_facility(place, i_n, obj, name):
        if all(place.resources[res] - v >= 0 for res, v in i_n[1]["build"].items()):
            for res, value in i_n[1]["build"].items():
                place.resources[res] -= value
            return obj(f"{name} {place.building_index}", place.building_index)

    def upgrade_the_facility(self, place, forge_level, i_n):
        upgrade_flag = True

        for res, value in i_n[self.level + 1]["build"].items():
            if res == "Forge":
                if forge_level < value:
                    upgrade_flag = False
            elif place.resources[res] - value < 0:
                upgrade_flag = False

        if upgrade_flag:
            self.level += 1
            for res, value in i_n[self.level]["build"].items():
                if res != "Forge":
                    place.resources[res] -= value
            return True
        return False


class Well(ResourceFacility):
    """ Making water by extraction. All information about wells are in the
        {info} {level: {information}}.

        def production_and_costs() ::: total production of water and
        total costs of metal from 1 well.

        Worker :: engineer, "pro" if worker.employment_history["engineer"] >= 10. """

    info = {
        1: {"max w_s": 1, "jun": 15, "pro": 15, "build": {"wood": 25}},
        2: {"max w_s": 1, "jun": 25, "pro": 25, "build": {"wood": 35}},
        3: {"max w_s": 1, "jun": 40, "pro": 40, "build": {"wood": 50}},
        4: {"max w_s": 1, "jun": 65, "pro": 65, "build": {"wood": 75}},
        5: {"max w_s": 2, "jun": 100, "pro": 100, "build": {"wood": 100, "stone": 500}},
        6: {"max w_s": 2, "jun": 150, "pro": 150, "build": {"wood": 150, "stone": 300}},
        7: {"max w_s": 2, "jun": 200, "pro": 200, "build": {"wood": 200, "stone": 400}},
        8: {"max w_s": 2, "jun": 250, "pro": 250, "build": {"wood": 250, "stone": 500}},
        9: {"max w_s": 2, "jun": 350, "pro": 350, "build": {"wood": 500, "stone": 500}},
        10: {"max w_s": 3, "jun": 500, "pro": 550,
             "build": {"wood": 2500, "metal": 2500, "stone": 5000, "Forge": 10}},
        11: {"max w_s": 4, "jun": 500, "pro": 550,
             "build": {"wood": 750, "metal": 250}},
        12: {"max w_s": 5, "jun": 500, "pro": 550,
             "build": {"wood": 850, "metal": 400}},
        13: {"max w_s": 6, "jun": 500, "pro": 550,
             "build": {"wood": 1000, "metal": 600}},
        14: {"max w_s": 7, "jun": 500, "pro": 550,
             "build": {"wood": 1500, "metal": 1000}},
        15: {"max w_s": 10, "jun": 500, "pro": 600,
             "build": {"wood": 7500, "metal": 5000, "stone": 10000, "Forge": 15}}
    }

    def __init__(self, *args):
        super().__init__(*args)

    def assets_and_liabilities_counter(self, assets, liabilities, costs=None,
                                       profession="engineer", years=10, place=None,
                                       minimum=85, maximum=106, resource="water"):

        super().assets_and_liabilities_counter(assets, liabilities, costs,
                                               profession, years, self.info,
                                               minimum, maximum, resource)

    def more_experience_workers(self, profession="engineer"):
        super().more_experience_workers(profession)

    @staticmethod
    def building_a_new_facility(place, i_n=None, obj=None, name=None):
        return ResourceFacility.building_a_new_facility(place, i_n=Well.info,
                                                        obj=Well, name="Well")

    def upgrade_the_facility(self, place, forge_level, i_n=None):
        return ResourceFacility.upgrade_the_facility(
            self, place, forge_level, i_n=Well.info)


class Farm(ResourceFacility):
    """ Making food by seeding and harvesting. All information about farms are in
        the {info} {level: {information}}.

        def production_and_costs() ::: total production of food and total costs of
        water, wood and metal from 1 farm.

        Worker :: farmer, "pro" if worker.employment_history["farmer"] >= 5. """

    info = {
        1: {"max w_s": 3, "jun": 6, "pro": 10, "build": {"wood": 25}},
        2: {"max w_s": 4, "jun": 7, "pro": 11, "build": {"wood": 35}},
        3: {"max w_s": 5, "jun": 8, "pro": 12, "build": {"wood": 50}},
        4: {"max w_s": 7, "jun": 9, "pro": 13, "build": {"wood": 100}},
        5: {"max w_s": 10, "jun": 11, "pro": 15,
            "build": {"wood": 150, "metal": 150, "Forge": 3}},
        6: {"max w_s": 15, "jun": 12, "pro": 16, "build": {"wood": 150, "metal": 100}},
        7: {"max w_s": 20, "jun": 13, "pro": 17, "build": {"wood": 200, "metal": 150}},
        8: {"max w_s": 25, "jun": 14, "pro": 18, "build": {"wood": 250, "metal": 200}},
        9: {"max w_s": 30, "jun": 15, "pro": 19, "build": {"wood": 350, "metal": 250}},
        10: {"max w_s": 50, "jun": 20, "pro": 30,
             "build": {"wood": 2500, "metal": 1500, "stone": 2500, "Forge": 8}},
        11: {"max w_s": 60, "jun": 20, "pro": 30,
             "build": {"wood": 500, "metal": 750}},
        12: {"max w_s": 70, "jun": 20, "pro": 30, "build": {"wood": 500, "metal": 800}},
        13: {"max w_s": 85, "jun": 20, "pro": 30,
             "build": {"wood": 550, "metal": 900}},
        14: {"max w_s": 100, "jun": 20, "pro": 30,
             "build": {"wood": 750, "metal": 1000}},
        15: {"max w_s": 125, "jun": 25, "pro": 40,
             "build": {"wood": 5000, "metal": 3000, "stone": 5000, "Forge": 15}}
    }

    def __init__(self, *args):
        super().__init__(*args)

    def assets_and_liabilities_counter(self, assets, liabilities, costs=None,
                                       profession="farmer", years=5, place=None,
                                       minimum=50, maximum=151, resource="food"):

        super().assets_and_liabilities_counter(assets, liabilities, {"water": 1},
                                               profession, years, self.info,
                                               minimum, maximum, resource)

    def more_experience_workers(self, profession="farmer"):
        super().more_experience_workers(profession)

    @staticmethod
    def building_a_new_facility(place, i_n=None, obj=None, name=None):
        return ResourceFacility.building_a_new_facility(place, i_n=Farm.info,
                                                        obj=Farm, name="Farm")

    def upgrade_the_facility(self, place, forge_level, i_n=None):
        return ResourceFacility.upgrade_the_facility(
            self, place, forge_level, i_n=Farm.info)


class HuntingHouse(ResourceFacility):
    """ Making food by hunting prey. All information about hunting houses are in
        the {info} {level: {information}}.

        def production_and_costs() ::: total production of food and total costs of
        wood and metal from 1 hunting house.

        Worker :: hunter, "pro" if worker.employment_history["hunter"] >= 5. """

    info = {
        1: {"max w_s": 2, "jun": 2.5, "pro": 5, "build": {"wood": 50}},
        2: {"max w_s": 3, "jun": 2.5, "pro": 5.3, "build": {"wood": 100}},
        3: {"max w_s": 4, "jun": 2.5, "pro": 5.6, "build": {"wood": 150}},
        4: {"max w_s": 5, "jun": 2.5, "pro": 6, "build": {"wood": 200}},
        5: {"max w_s": 10, "jun": 5, "pro": 10,
            "build": {"wood": 500, "metal": 250, "stone": 250, "Forge": 3}},
        6: {"max w_s": 15, "jun": 5, "pro": 10.5, "build": {"wood": 500, "metal": 150}},
        7: {"max w_s": 20, "jun": 5, "pro": 11, "build": {"wood": 500, "metal": 200}},
        8: {"max w_s": 25, "jun": 5, "pro": 11.5, "build": {"wood": 500, "metal": 250}},
        9: {"max w_s": 35, "jun": 5, "pro": 12, "build": {"wood": 600, "metal": 300}},
        10: {"max w_s": 50, "jun": 7.5, "pro": 15,
             "build": {"wood": 1000, "metal": 500, "stone": 500, "Forge": 8}}
    }

    def __init__(self, *args):
        super().__init__(*args)

    def assets_and_liabilities_counter(self, assets, liabilities, costs=None,
                                       profession="hunter", years=5, place=None,
                                       minimum=70, maximum=131, resource="food"):

        super().assets_and_liabilities_counter(assets, liabilities, costs,
                                               profession, years, self.info,
                                               minimum, maximum, resource)

    def more_experience_workers(self, profession="hunter"):
        super().more_experience_workers(profession)

    @staticmethod
    def building_a_new_facility(place, i_n=None, obj=None, name=None):
        return ResourceFacility.building_a_new_facility(place, i_n=HuntingHouse.info,
                                                        obj=HuntingHouse,
                                                        name="Hunting house")

    def upgrade_the_facility(self, place, forge_level, i_n=None):
        return ResourceFacility.upgrade_the_facility(
            self, place, forge_level, i_n=HuntingHouse.info)


class Port(ResourceFacility):
    """ Making food by fishing. All information about ports are in the
        {info} {level: {information}}.

        def production_and_costs() ::: total production of food and total costs of
        wood and metal from 1 port.

        Worker :: fisher, "pro" if worker.employment_history["fisher"] >= 3. """

    info = {
        1: {"max w_s": 3, "jun": 3, "pro": 5, "build": {"wood": 250}},
        2: {"max w_s": 4, "jun": 3, "pro": 5.2, "build": {"wood": 100}},
        3: {"max w_s": 5, "jun": 3, "pro": 5.4, "build": {"wood": 150}},
        4: {"max w_s": 7, "jun": 3, "pro": 5.7, "build": {"wood": 250}},
        5: {"max w_s": 10, "jun": 5, "pro": 10,
            "build": {"wood": 1000, "metal": 500, "stone": 1000, "Forge": 5}},
        6: {"max w_s": 15, "jun": 5, "pro": 10.5, "build": {"wood": 500, "metal": 50}},
        7: {"max w_s": 20, "jun": 5, "pro": 11, "build": {"wood": 500, "metal": 50}},
        8: {"max w_s": 25, "jun": 5, "pro": 11.5, "build": {"wood": 600, "metal": 75}},
        9: {"max w_s": 35, "jun": 5, "pro": 12, "build": {"wood": 600, "metal": 75}},
        10: {"max w_s": 50, "jun": 8, "pro": 19,
             "build": {"wood": 2000, "metal": 1000, "stone": 2500, "Forge": 10}},
        11: {"max w_s": 70, "jun": 8, "pro": 20, "build": {"wood": 750, "metal": 100}},
        12: {"max w_s": 100, "jun": 10, "pro": 25,
             "build": {"wood": 2500, "metal": 1500, "stone": 500, "Forge": 12}}
    }

    def __init__(self, *args):
        super().__init__(*args)

    def assets_and_liabilities_counter(self, assets, liabilities, costs=None,
                                       profession="fisher", years=3, place=None,
                                       minimum=85, maximum=116, resource="food"):

        super().assets_and_liabilities_counter(assets, liabilities, costs,
                                               profession, years, self.info,
                                               minimum, maximum, resource)

    def more_experience_workers(self, profession="fisher"):
        super().more_experience_workers(profession)

    @staticmethod
    def building_a_new_facility(place, i_n=None, obj=None, name=None):
        return ResourceFacility.building_a_new_facility(place, i_n=Port.info,
                                                        obj=Port, name="Port")

    def upgrade_the_facility(self, place, forge_level, i_n=None):
        return ResourceFacility.upgrade_the_facility(
            self, place, forge_level, i_n=Port.info)


class Sawmill(ResourceFacility):
    """ Making wood by chopping forest. All information about sawmills are
        in the {info} {level: {information}}.

        def production_and_costs() ::: total production of wood and total costs of
        metal from 1 sawmill.

        Worker :: chopper, "pro" if worker.employment_history["chopper"] >= 8. """

    info = {
        1: {"max w_s": 5, "jun": 5, "pro": 7.5, "build": {"wood": 50}},
        2: {"max w_s": 7, "jun": 5.2, "pro": 8, "build": {"wood": 75}},
        3: {"max w_s": 9, "jun": 5.4, "pro": 8.5, "build": {"wood": 100}},
        4: {"max w_s": 12, "jun": 5.7, "pro": 9,
            "build": {"wood": 100, "metal": 100, "Forge": 1}},
        5: {"max w_s": 20, "jun": 6, "pro": 10, "build": {"wood": 150, "metal": 50}},
        6: {"max w_s": 30, "jun": 6.3, "pro": 11, "build": {"wood": 200, "metal": 100}},
        7: {"max w_s": 40, "jun": 6.7, "pro": 12, "build": {"wood": 250, "metal": 150}},
        8: {"max w_s": 50, "jun": 7.1, "pro": 13, "build": {"wood": 250, "metal": 250}},
        9: {"max w_s": 60, "jun": 7.5, "pro": 14, "build": {"wood": 250, "metal": 500}},
        10: {"max w_s": 70, "jun": 10, "pro": 20,
             "build": {"wood": 1000, "metal": 2500, "stone": 2500, "Forge": 8}},
        11: {"max w_s": 80, "jun": 10.5, "pro": 22,
             "build": {"metal": 400, "stone": 250}},
        12: {"max w_s": 90, "jun": 11, "pro": 24,
             "build": {"metal": 500, "stone": 250}},
        13: {"max w_s": 100, "jun": 11.5, "pro": 26,
             "build": {"metal": 650, "stone": 250}},
        14: {"max w_s": 125, "jun": 12, "pro": 28,
             "build": {"metal": 750, "stone": 500}},
        15: {"max w_s": 150, "jun": 20, "pro": 40,
             "build": {"wood": 2500, "metal": 5000, "stone": 5000, "Forge": 15}}
    }

    def __init__(self, *args):
        super().__init__(*args)

    def assets_and_liabilities_counter(self, assets, liabilities, costs=None,
                                       profession="chopper", years=8, place=None,
                                       minimum=95, maximum=106, resource="wood"):

        super().assets_and_liabilities_counter(assets, liabilities, costs,
                                               profession, years, self.info,
                                               minimum, maximum, resource)

    def more_experience_workers(self, profession="chopper"):
        super().more_experience_workers(profession)

    @staticmethod
    def building_a_new_facility(place, i_n=None, obj=None, name=None):
        return ResourceFacility.building_a_new_facility(
            place=place, i_n=Sawmill.info, obj=Sawmill, name="Sawmill")

    def upgrade_the_facility(self, place, forge_level, i_n=None):
        return ResourceFacility.upgrade_the_facility(
            self, place, forge_level, i_n=Sawmill.info)


class Mine(ResourceFacility):
    """ Extracting ore by mining. All information about mines are in
        the {info} {level: {information}}.

        def production_and_costs() ::: total production of ore and total costs of
        metal from 1 mine.

        Worker :: miner, "pro" if worker.employment_history["miner"] >= 10. """

    info = {
        1: {"max w_s": 5, "jun": 5, "pro": 10, "build": {"wood": 150}},
        2: {"max w_s": 7, "jun": 5, "pro": 10, "build": {"wood": 200}},
        3: {"max w_s": 10, "jun": 5, "pro": 10,
            "build": {"wood": 250, "metal": 50, "Forge": 1}},
        4: {"max w_s": 15, "jun": 5, "pro": 10, "build": {"wood": 250, "metal": 100}},
        5: {"max w_s": 20, "jun": 10, "pro": 15,
            "build": {"wood": 500, "metal": 250, "stone": 250, "Forge": 2}},
        6: {"max w_s": 25, "jun": 10, "pro": 15, "build": {"wood": 300, "metal": 300}},
        7: {"max w_s": 35, "jun": 10, "pro": 15, "build": {"wood": 300, "metal": 300}},
        8: {"max w_s": 50, "jun": 10, "pro": 15, "build": {"wood": 350, "metal": 350}},
        9: {"max w_s": 75, "jun": 10, "pro": 15, "build": {"wood": 500, "metal": 500}},
        10: {"max w_s": 100, "jun": 15, "pro": 30,
             "build": {"wood": 2500, "metal": 2000, "stone": 2000, "Forge": 10}}
    }

    def __init__(self, *args):
        super().__init__(*args)

    def assets_and_liabilities_counter(self, assets, liabilities, costs=None,
                                       profession="miner", years=10, place=None,
                                       minimum=95, maximum=106, resource="ore"):

        super().assets_and_liabilities_counter(assets, liabilities, costs,
                                               profession, years, self.info,
                                               minimum, maximum, resource)

    def more_experience_workers(self, profession="miner"):
        super().more_experience_workers(profession)

    @staticmethod
    def building_a_new_facility(place, i_n=None, obj=None, name=None):
        return ResourceFacility.building_a_new_facility(place, i_n=Mine.info,
                                                        obj=Mine, name="Mine")

    def upgrade_the_facility(self, place, forge_level, i_n=None):
        return ResourceFacility.upgrade_the_facility(
            self, place, forge_level, i_n=Mine.info)


class Quarry(ResourceFacility):
    """ Extracting stone by mining. All information about quarries are in
        the {info} {level: {information}}.

        def production_and_costs() ::: total production of stone and total costs of
        metal from 1 quarry.

        Worker :: miner, "pro" if worker.employment_history["miner"] >= 10. """

    info = {
        1: {"max w_s": 5, "jun": 5, "pro": 10, "build": {"wood": 150}},
        2: {"max w_s": 7, "jun": 5, "pro": 10, "build": {"wood": 200}},
        3: {"max w_s": 10, "jun": 5, "pro": 10,
            "build": {"wood": 250, "metal": 50, "Forge": 1}},
        4: {"max w_s": 15, "jun": 5, "pro": 10, "build": {"wood": 250, "metal": 200}},
        5: {"max w_s": 20, "jun": 10, "pro": 15,
            "build": {"wood": 500, "metal": 250, "stone": 250, "Forge": 2}},
        6: {"max w_s": 25, "jun": 10, "pro": 15, "build": {"wood": 300, "metal": 300}},
        7: {"max w_s": 35, "jun": 10, "pro": 15, "build": {"wood": 300, "metal": 300}},
        8: {"max w_s": 50, "jun": 10, "pro": 15, "build": {"wood": 350, "metal": 350}},
        9: {"max w_s": 75, "jun": 10, "pro": 15, "build": {"wood": 500, "metal": 500}},
        10: {"max w_s": 100, "jun": 15, "pro": 30,
             "build": {"wood": 2500, "metal": 2000, "stone": 2000, "Forge": 10}}
    }

    def __init__(self, *args):
        super().__init__(*args)

    def assets_and_liabilities_counter(self, assets, liabilities, costs=None,
                                       profession="miner", years=10, place=None,
                                       minimum=95, maximum=106, resource="stone"):

        super().assets_and_liabilities_counter(assets, liabilities, costs,
                                               profession, years, self.info,
                                               minimum, maximum, resource)

    def more_experience_workers(self, profession="miner"):
        super().more_experience_workers(profession)

    @staticmethod
    def building_a_new_facility(place, i_n=None, obj=None, name=None):
        return ResourceFacility.building_a_new_facility(place, i_n=Quarry.info,
                                                        obj=Quarry, name="Quarry")

    def upgrade_the_facility(self, place, forge_level, i_n=None):
        return ResourceFacility.upgrade_the_facility(
            self, place, forge_level, i_n=Quarry.info)


class Forge(ResourceFacility):
    """ Forge are used for getting metal from ore, upgrading facilities,
        making and repairing new equipment. It takes 2 ore for making 1 metal.
        All information about forges are in the {info} {level: {information}}.

        def production_and_costs() ::: total production of metal and total costs of
        ore, wood and metal from 1 forge.

        Worker :: blacksmith, "pro" if worker.employment_history["blacksmith"] >= 15. """

    info = {
        1: {"max w_s": 2, "jun": 1, "pro": 2.5, "build": {"wood": 500}},
        2: {"max w_s": 3, "jun": 1, "pro": 2.8, "build": {"wood": 100}},
        3: {"max w_s": 5, "jun": 1, "pro": 3.1, "build": {"wood": 150}},
        4: {"max w_s": 7, "jun": 1, "pro": 3.5, "build": {"wood": 200}},
        5: {"max w_s": 10, "jun": 5, "pro": 10,
            "build": {"wood": 1000, "metal": 150, "stone": 250}},
        6: {"max w_s": 15, "jun": 5, "pro": 10.5, "build": {"wood": 250, "metal": 100}},
        7: {"max w_s": 20, "jun": 5, "pro": 11, "build": {"wood": 250, "metal": 150}},
        8: {"max w_s": 25, "jun": 5, "pro": 11.5, "build": {"wood": 250, "metal": 200}},
        9: {"max w_s": 35, "jun": 5, "pro": 12, "build": {"wood": 250, "metal": 250}},
        10: {"max w_s": 50, "jun": 10, "pro": 20,
             "build": {"wood": 2500, "metal": 1500, "stone": 2500}},
        11: {"max w_s": 65, "jun": 10, "pro": 21,
             "build": {"wood": 500, "metal": 500, "stone": 750}},
        12: {"max w_s": 80, "jun": 10, "pro": 22,
             "build": {"wood": 500, "metal": 500, "stone": 1000}},
        13: {"max w_s": 100, "jun": 10, "pro": 23,
             "build": {"wood": 750, "metal": 1000, "stone": 1500}},
        14: {"max w_s": 125, "jun": 10, "pro": 24,
             "build": {"wood": 1000, "metal": 1500, "stone": 2000}},
        15: {"max w_s": 150, "jun": 15, "pro": 30,
             "build": {"wood": 5000, "metal": 5000, "stone": 10000}}
    }

    def __init__(self, *args):
        super().__init__(*args)

    def assets_and_liabilities_counter(self, assets, liabilities, costs=None,
                                       profession="blacksmith", years=15, place=None,
                                       minimum=95, maximum=106, resource="metal"):

        super().assets_and_liabilities_counter(assets, liabilities, {"ore": 2},
                                               profession, years, self.info,
                                               minimum, maximum, resource)

    def more_experience_workers(self, profession="blacksmith"):
        super().more_experience_workers(profession)

    @staticmethod
    def building_a_new_facility(place, i_n=None, obj=None, name=None):
        return ResourceFacility.building_a_new_facility(place, i_n=Forge.info,
                                                        obj=Forge, name="Forge")

    def upgrade_the_facility(self, place, forge_level, i_n=None):
        return ResourceFacility.upgrade_the_facility(
            self, place, forge_level, i_n=Forge.info)


class House:
    """ House is a place, where people live. All houses have a unique number-key
        which is Environment.house_index. The __len__ representation is a number
        of alive people, living in the house. All information about houses are in
        the {info} {level: {information}}. """

    info = {
        1: {"max p_l": 4, "cost: wood": 0.9, "build": {"wood": 50}},
        2: {"max p_l": 8, "cost: wood": 0.8,
            "build": {"wood": 300, "metal": 50, "Forge": 1}},
        3: {"max p_l": 14, "cost: wood": 0.7,
            "build": {"wood": 750, "metal": 150, "Forge": 3}},
        4: {"max p_l": 22, "cost: wood": 0.6,
            "build": {"wood": 1000, "metal": 250, "stone": 1000, "Forge": 5}},
        5: {"max p_l": 32, "cost: wood": 0.5,
            "build": {"wood": 1500, "metal": 500, "stone": 2000, "Forge": 8}}
    }

    def __init__(self, index, level=1):
        self.index = index  # int : is a Environment.house_index
        self.level = level  # int : level of a facility
        self.tenants = []  # an array of people, who live in this house

    def __len__(self):
        return len(self.tenants)

    def __str__(self):
        return f"house {self.index} ({self.level}), amount of tenants = {len(self)}"

    @staticmethod
    def a_house_builder(place, family_flag=True, human_flag=False):
        wood = place.resources["wood"] - House.info[1]["build"]["wood"]
        if wood >= 0:
            place.resources["wood"] -= House.info[1]["build"]["wood"]
            house = House(place.house_index)

            if family_flag:
                for index, family in place.families.items():
                    if not family["house"]:
                        family["house"] = house.index
                        for array in (family["parents"], family["children"]):
                            for human in array:
                                human.house_index = house.index
                                house.tenants.append(human)
                        break

            elif human_flag:
                for array in (place.adults, place.elders):
                    for human in array:
                        if not human.house_index:
                            human.house_index = house.index
                            house.tenants.append(human)
                            break

            return house

    def upgrade_the_house(self, place, f_l):
        upgrade_flag = True

        for res, value in self.info[self.level + 1]["build"].items():
            if res == "Forge":
                if f_l < value:
                    upgrade_flag = False
            elif place.resources[res] - value < 0:
                upgrade_flag = False

        if upgrade_flag:
            self.level += 1
            for res, value in self.info[self.level]["build"].items():
                if res != "Forge":
                    place.resources[res] -= value


class Human:
    """ Human is a alive create, who is trying to make his / her life. They try to
        make new families and children. They have resources for building facilities,
        like houses, where they can live, or buildings, where they can make other
        resources. For there life, they need 1 water, 1 food and, depends on the
        level of the house they are living in, 1 - 0.5 wood. """

    def __init__(self, genome=None, surname=None, age=0, wish_attr=0.5,
                 family_parent_index=None, family_history="", house_index=None):
        # base human attributes
        self.genome = genome or "".join([chr(rdr(65, 91)) for _ in range(46)])
        # str : 46 upper letters value as a unique human code
        self.sex = "M" if rdm() >= 0.5 else "F"  # str : Male or Female
        self.age = age  # int : human years, 0 when was born
        self.death = 0.75  # int : number, which used in dead_function_by_age() function

        with open("list_of_names.json", "r") as names_dict:
            names = load(names_dict)
            self.name = names["name_man"][rdr(0, 340)] if self.sex == "M" \
                else names["name_woman"][rdr(0, 204)]  # str : human name
            self.surname = surname or names["surname"][rdr(0, 60)]  # str : human surname

        # attributes for family
        self.attr = float("{:.2f}".format(wb(2.5, 2.5)))  # float : attractiveness
        self.wish_attr = wish_attr  # float : wish attractiveness

        self.marriage = None  # Human() : None if not marriage else husband or wife
        self.family_index = None  # int : is a Environment.family_index
        self.family_parent_index = family_parent_index  # int : an index of the family
        # where human() is a child
        self.family_history = family_history  # str : family history of the human
        self.indexes = []  # all family_indexes of a human

        # attributes for profession
        self.employment_history = {"builder": 0, "farmer": 0, "hunter": 0,
                                   "fisher": 0, "engineer": 0, "chopper": 0,
                                   "miner": 0, "blacksmith": 0}

        self.builder_status = False  # bool : True if in Environment.brigades
        self.job_status = None  # int : if ResourceFacility.index, else None

        # attribute for houses
        self.house_index = house_index  # int : index of the human house

    def __str__(self):
        return f"{self.surname} {self.name}, {self.sex}, {self.age}, family = " \
               f"{self.family_index}, house = {self.house_index}, history = " \
               f"'{self.family_history}', genome = {self.genome}"

    @staticmethod
    def dead_function_by_age(place):
        for copies in (place.kids[:], place.adults[:], place.elders[:]):

            counter = 0
            for number, human in enumerate(copies):
                if human.age < 25:
                    bones = abs(2.626225 * rdm() - (human.age / 24950)) / 3.5

                elif human.age < 61:
                    bones = (2.3252332 * rdm() + ((human.age - 26) / 16250)) / 3.1

                else:
                    bones = (1.726726 * rdm() + ((human.age - 61) / 75)) / 2.3

                if bones >= human.death:
                    if human.age < 18:
                        place.grave.append(place.kids.pop(number - counter))

                    elif human.age < 55:
                        place.grave.append(place.adults.pop(number - counter))

                    elif human.age >= 55:
                        place.grave.append(place.elders.pop(number - counter))

                    counter += 1

        for corpse in place.grave:
            if corpse.family_parent_index:
                place.families[corpse.family_parent_index]["children"].remove(corpse)
                corpse.family_parent_index = None

            if corpse.marriage:

                for family in corpse.indexes:
                    place.families[family]["parents"].remove(corpse)

                corpse.marriage.marriage = None
                corpse.marriage, corpse.indexes, corpse.family_index = None, [], None

            if not corpse.marriage and corpse.indexes:

                for family in corpse.indexes:
                    place.families[family]["parents"].remove(corpse)

                corpse.indexes, corpse.family_index = [], None

            if corpse.house_index:
                place.houses[corpse.house_index].tenants.remove(corpse)
                corpse.house_index = None

            if corpse.job_status:
                if type(corpse.job_status) is int:
                    place.buildings[corpse.job_status].workers.remove(corpse)
                    corpse.job_status = None

                elif type(corpse.job_status) is bool:
                    place.brigades.remove(corpse)
                    corpse.job_status = None

    @staticmethod
    def removing_all_families_without_parents(place):
        for number, family in place.families.copy().items():
            if len(family["parents"]) == 0:
                for child in family["children"]:
                    child.family_parent_index = None
                del place.families[number]

    def attractiveness_parameter_changer(self):
        return float("{:.2f}".format(self.attr +
                                     ((rdm() / 2) * ((50 - self.age) / 100))))

    def wish_attractiveness_parameter_changer(self):
        if self.age > 35 and not self.marriage:

            wish = float("{:.2f}".format(self.wish_attr +
                                         (rdm() * ((35 - self.age) / 200))))

        else:
            wish = float("{:.2f}".format(self.wish_attr +
                                         (rdm() * ((50 - self.age) / 200))))

        if wish < 0:
            return 0
        return wish

    @staticmethod
    def genome_checker(genome_1, genome_2):
        counter, same = 0, 0
        for _ in range(23):

            if genome_1[counter:counter + 2] == genome_2[counter:counter + 2]:
                same += 2
            counter += 2

        if same / 46 >= 0.15:
            return False
        return True

    @staticmethod
    def people_want_to_make_families(place):
        for human in place.adults:
            if not human.marriage:

                for challenger in place.adults:
                    if not challenger.marriage and challenger.sex != human.sex \
                            and Human.genome_checker(human.genome, challenger.genome) \
                            and human.attr >= challenger.wish_attr \
                            and challenger.attr >= human.wish_attr:

                        if rdm() >= (0.6 + (abs(human.age - challenger.age) / 100)):

                            place.families[place.family_index] = {
                                "house": None, "parents": [human, challenger],
                                "children": []}

                            human.marriage, challenger.marriage = challenger, human

                            for parent in (human, challenger):
                                parent.indexes.append(place.family_index)

                            human.family_index = place.family_index
                            challenger.family_index = place.family_index
                            human.family_history += f"{place.family_index} "
                            challenger.family_history += f"{place.family_index} "
                            Human.new_house_for_a_new_family(place, human, challenger)

                            place.family_index += 1
                            break
                continue

    @staticmethod
    def genome_parameter_for_making_a_new_human_via_a_family(genome_1, genome_2):
        genome, counter = "", 0
        for _ in range(23):
            genome += chc([genome_1[counter:counter + 2], genome_2[counter:counter + 2]])
            counter += 2
        return genome

    @staticmethod
    def new_house_for_a_new_family(place, human, challenger):
        if human.house_index and len(place.houses[human.house_index].tenants) == 1:
            challenger.house_index = human.house_index
            place.houses[human.house_index].tenants.append(challenger)
            place.families[place.family_index]["house"] = human.house_index
            return

        if challenger.house_index and \
                len(place.houses[challenger.house_index].tenants) == 1:
            human.house_index = challenger.house_index
            place.houses[challenger.house_index].tenants.append(human)
            place.families[place.family_index]["house"] = challenger.house_index
            return

    @staticmethod
    def baby_maker_function_via_a_family(gen_1, gen_2, surname, index, family_history,
                                         house_index, place):

        genome = Human.genome_parameter_for_making_a_new_human_via_a_family(gen_1, gen_2)
        baby = Human(genome=genome, surname=surname, family_parent_index=index,
                     family_history=family_history, house_index=house_index)

        place.kids.append(baby)
        place.families[index]["children"].append(baby)
        if house_index:
            place.houses[house_index].tenants.append(baby)

    @staticmethod
    def people_want_to_make_new_people(place):
        for index, fml in place.families.items():
            if len(fml["parents"]) == 2 and rdm() \
                    >= (0.8 + (sqrt(len(fml["children"])) * 5 / 100)):

                if fml["parents"][0].age in range(18, 56) and \
                        fml["parents"][1].age in range(18, 56):

                    gen_1, gen_2, surname, family_history = None, None, None, None

                    for parent in fml["parents"]:
                        if parent.sex == "M":
                            gen_1 = parent.genome
                            surname = parent.surname
                            family_history = parent.family_history
                        else:
                            gen_2 = parent.genome

                    Human.baby_maker_function_via_a_family(gen_1, gen_2, surname, index,
                                                           family_history, fml["house"],
                                                           place)

                    if rdm() >= 0.99:
                        Human.baby_maker_function_via_a_family(gen_1, gen_2, surname,
                                                               index, family_history,
                                                               fml["house"], place)

    @staticmethod
    def moving_people_from_array_to_array(place):
        counter = 0
        for number, child in enumerate(place.kids[:]):
            if child.age >= 18:
                place.adults.append(place.kids.pop(number - counter))
                counter += 1

        counter = 0
        for number, adult in enumerate(place.adults[:]):
            if adult.age >= 55:
                place.elders.append(place.adults.pop(number - counter))
                counter += 1

    @staticmethod
    def people_want_to_build_new_facilities(place, need):
        have = 0
        for builder in place.brigades:
            have += 2 if builder.employment_history["builder"] >= 10 else 1
            builder.employment_history["builder"] += 1
            place.brigades.remove(builder)
            builder.builder_status = False

            if have >= need:
                return True
        return False

    @staticmethod
    def people_did_not_build_any_buildings(place):
        for builder in place.brigades:
            builder.builder_status = False
            place.brigades.remove(builder)


def integer_checker(question=None, value=None, message=None):
    if question:
        print(question)

    text = value or input()
    while True:
        try:
            number = int(text)
            if number < 0:
                if message:
                    print(f"'{message}' >>> '{number}' is not acceptable. "
                          f"Should be at least equal to 0. Please, try again.")
                else:
                    print(f"'{number}' is not acceptable. "
                          f"Should be at least equal to 0. Please, try again.")
            else:
                return number

        except ValueError:
            if message:
                print(f"'{message}' >>> '{text}' is not acceptable. "
                      f"Please, print a number (int).")
            else:
                print(f"'{text}' is not acceptable. Please, print a number (int).")

        text = input()


def average_life_function(place):
    if not place.grave:
        return 0
    else:
        average_life = 0
        for dead_bodies in place.grave:
            average_life += dead_bodies.age

    return float("{:.2f}".format(average_life / len(place.grave)))


def data_collecting_function(seconds):
    global Earth

    Earth.data["years"] = Earth.year
    Earth.data["seconds per year"].append(seconds)

    for city in Earth.world:
        city.data["kids"].append(len(city.kids))
        city.data["adults"].append(len(city.adults))
        city.data["elders"].append(len(city.elders))
        city.data["people in the city"].append(len(city))
        city.data["families"].append(len(city.families))
        city.data["grave"].append(len(city.grave))
        city.data["average life"] = average_life_function(city)
        city.data["water"].append(round(city.water, 2))
        city.data["food"].append(round(city.food, 2))
        city.data["wood"].append(round(city.wood, 2))
        city.data["ore"].append(round(city.ore, 2))
        city.data["metal"].append(round(city.metal, 2))
        city.data["stone"].append(round(city.stone, 2))
        city.data["buildings"].append(len(city.buildings))
        city.data["houses"].append(len(city.houses))


def printing():
    global Earth
    print(Earth)
    print(f"It took {Earth.data['seconds per year'][-1]} seconds "
          f"for making {Earth.year} year.")

    table = PrettyTable(padding_width=2)
    table.add_column("", ["People", "Families", "Elders", "Adults", "Kids", "Corpses",
                          "Average life", "Water", "Food", "Wood", "Ore", "Metal",
                          "Stone", "Buildings", "Houses"])

    for v in Earth.world:
        table.add_column(v.name, [str(v.data["people in the city"][-1]),
                                  str(v.data["families"][-1]),
                                  str(v.data["elders"][-1]),
                                  str(v.data["adults"][-1]),
                                  str(v.data["kids"][-1]),
                                  str(v.data["grave"][-1]),
                                  str(v.data["average life"]),
                                  str(v.data["water"][-1]),
                                  str(v.data["food"][-1]),
                                  str(v.data["wood"][-1]),
                                  str(v.data["ore"][-1]),
                                  str(v.data["metal"][-1]),
                                  str(v.data["stone"][-1]),
                                  str(v.data["buildings"][-1]),
                                  str(v.data["houses"][-1])])
    print(table, end="\n\n")


def city_picker_for_more_info(message):
    global Earth

    names = [rr_rr.name for rr_rr in Earth.world]
    print(f"'{message}' Please, choose a city (any register) : {', '.join(names)}")

    while True:
        city_pick = str(input()).title()
        if city_pick == "":
            print("You can't pass a space blanked name. Please, try again.")
        elif city_pick not in names:
            print(f"{city_pick} city doesn't exist. Please, try again.")
        else:
            index = names.index(city_pick)
            return Earth.world[index]


if __name__ == "__main__":

    Earth = World("Earth")  # creating the World Object with "Earth" name
    print(f"The world with the name '{Earth.name}' was created ...\n")

    Earth.cities_creator(integer_checker(
        question="Please, print how much cities do you want to have."))

    looping = False  # bool : if False -> press <enter> button for making a new year,
    # if True -> passing years depends on loop_ration
    loop_ratio = 0  # int : if looping = True, showing how much years computer
    # automatically will count

    while True:

        while looping:
            for _ in range(loop_ratio):

                start = tm()
                Earth.year += 1
                Earth.year_maker()
                data_collecting_function(tm() - start)
                printing()
            else:
                looping = False

        start = tm()
        Earth.year += 1
        Earth.year_maker()
        data_collecting_function(tm() - start)
        printing()
        flag = True

        while flag:
            print("Commands: city, kid, adult, elder, "
                  "family, corpse, history, request, save, exit, (int).")
            command = input("Your command ..........................").lower()

            if command == "city":
                if len(Earth.world) == 1:
                    city_city = Earth.world[0]
                else:
                    city_city = city_picker_for_more_info("city")
                print(city_city)

            if command == "kid":
                if len(Earth.world) == 1:
                    kids_from_the_city = Earth.world[0]
                else:
                    kids_from_the_city = city_picker_for_more_info("kid")

                for xx_xx in kids_from_the_city.kids:
                    print(xx_xx)
                print()

            if command == "adult":
                if len(Earth.world) == 1:
                    adults_from_the_city = Earth.world[0]
                else:
                    adults_from_the_city = city_picker_for_more_info("adult")

                for xx_xx in adults_from_the_city.adults:
                    print(xx_xx)
                print()

            if command == "elder":
                if len(Earth.world) == 1:
                    elders_from_the_city = Earth.world[0]
                else:
                    elders_from_the_city = city_picker_for_more_info("elder")
                for xx_xx in elders_from_the_city.elders:
                    print(xx_xx)
                print()

            if command == "family":
                if len(Earth.world) == 1:
                    family_from_the_city = Earth.world[0]
                else:
                    family_from_the_city = city_picker_for_more_info("family")

                if len(family_from_the_city.families) > 0:
                    print("Families : ", end="\n\n")
                    for ind, fam in family_from_the_city.families.items():
                        print(f"Family with {ind} index")
                        print("Parents")
                        for par in fam["parents"]:
                            print(par)
                        if len(fam["children"]) > 0:
                            print("Children")
                            for cld in fam["children"]:
                                print(cld)
                        print()

            if command == "corpse":
                if len(Earth.world) == 1:
                    dead_from_the_city = Earth.world[0]
                else:
                    dead_from_the_city = city_picker_for_more_info("corpse")

                if len(dead_from_the_city.grave) > 0:
                    print("Grave")
                    for dead_b in dead_from_the_city.grave:
                        print(dead_b)
                print()

            if command == "history":
                if len(Earth.world) == 1:
                    the_city_history = Earth.world[0]
                else:
                    the_city_history = city_picker_for_more_info("history")

                for h in the_city_history.kids:
                    print(f"{h.surname} {h.name}, {h.sex}, {h.age}, parent index = "
                          f"{h.family_parent_index}, family history = "
                          f"{h.family_history}")

                for ooo in (the_city_history.adults, the_city_history.elders):
                    for o in ooo:
                        if o.marriage:
                            print(f"{o.surname} {o.name}, {o.sex}, {o.age}, marriage = "
                                  f"{o.marriage.surname} {o.marriage.name}, "
                                  f"parent index = {o.family_parent_index}, "
                                  f"family history = {o.family_history}")
                        else:
                            print(f"{o.surname} {o.name}, {o.sex}, {o.age}, "
                                  f"parent index = {o.family_parent_index}, "
                                  f"family history = {o.family_history}")
                print()

            if command == "request":
                for dd_ss in Earth.world:
                    print(f"City : {dd_ss.name}\n")
                    print(f"Queues : \n[{', '.join(map(str, dd_ss.queue))}]")
                    print(f"Alerts : \n[{', '.join(map(str, dd_ss.alert))}]")
                    print(f"Non_urgent : \n[{', '.join(map(str, dd_ss.non_urgent))}]")
                    print(f"Plan : \n[{', '.join(map(str, dd_ss.plan))}]")
                    print("-" * 103)

            if command == "save":
                with open("data_for_graph.json", "w") as file:
                    temporary_dict = {"years": Earth.data["years"],
                                      "seconds per year": Earth.data["seconds per year"]}

                    for jj_jj in Earth.world:
                        temporary_dict[jj_jj.name] = jj_jj.data
                    dump(temporary_dict, file)

            if command.isdigit():
                looping, loop_ratio, flag = True, int(command), False

            if command == "":
                flag = False

            if command == "exit":
                exit()
