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
    """
    if len(path) == 0:
        print("Not connected.")
    else:
        for p1 in path:
            degrees = len(p1)
            print(f"{degrees} degrees of separation.")
            p1 = [(None, source)] + p1
            for i in range(degrees):
                person1 = people[p1[i][1]]["name"]
                person2 = people[p1[i + 1][1]]["name"]
                movie = movies[p1[i + 1][0]]["title"]
                print(f"{i + 1}: {person1} and {person2} starred in {movie}")
"""
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
    # frontier = QueueFrontier()
    start = Node(state=source, action=None, parent=None, step=0)
    frontier.add(start)

  
    explored_nodes = dict()
    explored_num = 0
    solution = None
    hit_count = dict()
    start_time = time.time()

    # List all options which step is 3 for Emma and Jeniffer
    # solutions = []

    while True:
        if frontier.empty():
            print("Hit count: ", hit_count)
            print("Time cost: ", time.time()-start_time)
            print("Num of explored nodes: ", explored_num)
            return None if solution == None else solution[0]
            # return None if len(solutions)==0 else solutions
        
        node = frontier.remove()
        
        # Explored {person_id:(step, movie_id)} is recorded
        explored_nodes[node.state] = node.step
        explored_num += 1
        
        
        parent_id = node.state

        for neighbor in neighbors_for_person(parent_id):
            # If the person is 5 steps away (or even more) from the source, give it up because of Six Degrees of Kevin Bacon, and it can definitely improve the performance
            if node.step > 5:
                break
            
            # If can find a shorter path/step than the explored (person_id, step) for the certain person, explore it, otherwise, give it up to improve performance
            if neighbor[1] != parent_id and not frontier.contains_state(neighbor[1]) and (neighbor[1] not in explored_nodes.keys() or node.step+1 < explored_nodes[neighbor[1]]):
                child = Node(state=neighbor[1], action=neighbor[0], parent=node, step=node.step+1)
                
                if child.state == target:
                    
                    step = child.step
                    # Recode the hit count for different steps/length of the path
                    if step in hit_count.keys():
                        hit_count[step] += 1
                    else:
                        hit_count[step] = 1

                    # Organize the being returned result via the node's parent link 
                    links = []
                    while child.parent is not None:
                        links.append((child.action, child.state))
                        child = child.parent
                    links.reverse()
                    
                    # Always fetch the shortest path if have.!!!!
                    if solution == None or solution[1] > step:
                        solution = (links, step)
                    
                    # if step == 3:
                    #    solutions.append(links)    

                    # If the child is the target, not explore other neighbors any more.
                    break
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
