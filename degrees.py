import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])
    
    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }
    
    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass
    # print("Rows of peoples ", len(people))
    # print("Rows of names: ", len(names))
    # print("Rows of movies: ", len(movies))

def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")
    source = person_id_for_name(input("Name: ").title())
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    import time
    frontier = StackFrontier()
    # Identify the start nodes
    print("Source :", source)
    print("Source neighbors:", neighbors_for_person(source))
    print(people)
    for movie_id, person_id in neighbors_for_person(source):
        if person_id == source:
            start = Node(state=(movie_id, person_id), parent=None, step=0)
            # count_start += 1
            # print(start.state)
            frontier.add(start)

    #Identify the goals
    goals = []
    # count_goal = 0
    # print("Goal points are:")
    for movie_id, person_id in neighbors_for_person(target):
        if person_id == target:
            goals.append((movie_id, person_id))
            # count_goal += 1
            # print((movie_id, person_id))

    # count = count_start * count_goal
    # print('Count is ', count)
    explored_nodes = set()
    solution = None
    hit_count = 0
    start_time = time.time()
    while True:
        if frontier.empty():
            print("Hit count: ", hit_count)
            print("Time cost: ", time.time()-start_time)
            return None if solution == None else solution[0]
        
        node = frontier.remove()
        explored_nodes.add(node.state)
        
        
        person_id = node.state[1]

        for state in neighbors_for_person(person_id):
            if node.step > 6:
                break
            # print("node.step", node.step)
            if not frontier.contains_state(state) and state not in explored_nodes:
                child = Node(state=state, parent=node, step=node.step+1)
                if child.state in goals:
                    hit_count += 1
                    explored_nodes.add(node.state)
                    step = child.step
                    links = []
                    while child.parent is not None:
                        links.append(child.state)
                        child = child.parent
                    links.reverse()
                    # count -= 1
                    if solution == None or solution[1] > step:
                        solution = (links, step)
                else:
                    frontier.add(child)

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    print(person_ids)
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
