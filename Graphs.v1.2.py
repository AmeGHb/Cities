import json
import matplotlib.pyplot as plt


with open("data_for_graph.json", "r") as file:
    data = json.load(file)


def graph_maker_function___seconds_of_making_a_one_year_to_years():
    global data

    if len(range(data["years"])) != len(data["seconds per year"]):
        print("Something wrong with the data\n"
              f"length of ['years'] is {len(range(data['years']))}\n"
              f"length of ['seconds per year'] is {len(data['seconds per year'])}")
        return

    seconds = 0
    for sec in data["seconds per year"]:
        seconds += sec

    plt.plot(range(1, data["years"] + 1), data["seconds per year"], "-")
    plt.legend()
    plt.title("Сколько секунд нужно чтобы выполнить функцию в зависимости от года\n"
              f"Общее количество затраченных секунд: {round(seconds, 2)}\n"
              f"Среднее количество секунд в год: "
              f"{round((seconds / data['years']), 2)}",
              fontsize=14)
    plt.ylabel("Seconds / Year", fontsize=14)
    plt.xlabel("Year", fontsize=14)
    plt.grid(which="major", linestyle="-", linewidth=0.5)
    plt.get_current_fig_manager().window.state('zoomed')
    plt.show()


def graph_maker_function___cities_parameters(item, title):
    global data

    city_data = {k: v for k, v in data.items() if k != "seconds per year"}
    fig, ax = plt.subplots()

    for key, value in city_data.items():
        if key == "years":
            continue

        ax.plot(range(1, city_data["years"] + 1), value[item],
                label=f"{key} : ({value['average life']})")

    ax.legend(fontsize=14, ncol=1, loc="upper left")
    plt.ylabel("Amount", fontsize=14)
    plt.xlabel("Year", fontsize=14)
    plt.title(title, fontsize=14)
    plt.grid(linestyle="-", linewidth=0.5)
    plt.get_current_fig_manager().window.state('zoomed')
    plt.show()


if __name__ == "__main__":
    graph_maker_function___seconds_of_making_a_one_year_to_years()

    items_titles = {"people in the city": "Amount of people",
                    "families": "Amount of families",
                    "elders": "Amount of elders", "adults": "Amount of adults",
                    "kids": "Amount of kids", "grave": "Amount of corpses",
                    "water": "Amount of water", "food": "Amount of food",
                    "wood": "Amount of wood", "ore": "Amount of ore",
                    "metal": "Amount of metal", "stone": "Amount of stone",
                    "buildings": "Amount of buildings", "houses": "Amount of houses"}

    for first, second in items_titles.items():
        graph_maker_function___cities_parameters(first, second)
