import sys
import random
from collections import deque
import numpy as np

class Wikipedia:

    # Load the file to initialize the graph
    def __init__(self, pages_file, links_file):

        # dict {ID : integer, page title : String}
        self.idToTitle = {}

        # dict {title : String, ID : integer}
        self.titleToId = {}

        # dict {sorce ID : integer, destination ID : String}
        self.links = {}

        # Initialise self.idToTitle and self.titleToId
        # with open(pages_file) as file:
        with open(pages_file, mode='r', encoding='utf-8') as file:
            for line in file:
                (id, title) = line.rstrip().split(" ")
                id = int(id)
                assert not id in self.idToTitle
                self.idToTitle[id] = title
                assert not title in self.titleToId
                self.titleToId[title] = id
                self.links[id] = []
        print("Finished reading %s" % pages_file)

        # Initialise self.links
        with open(links_file) as file:
            for line in file:
                (src, dst) = line.rstrip().split(" ")
                (src, dst) = (int(src), int(dst))
                assert src in self.idToTitle, src
                assert dst in self.idToTitle, dst
                self.links[src].append(dst)
        print("Finished reading %s" % links_file)
        print()

    # Find the longest title
    def find_longest_title(self):
        titles = sorted(self.idToTitle.values(), key=len, reverse=True)
        print("The longest title is:")
        index = 0
        max_len_title = 0
        while index < len(titles):
            if titles[index].find("_") == -1:
                print(titles[index])
                max_len_title = len(titles[index])
                index += 1
                break
            index += 1
        while index < len(titles):
            if len(titles[index]) < max_len_title:
                break
            if titles[index].find("_") == -1:
                print(titles[index])
            index += 1
        print()

    # Find the most linked page
    def find_most_linked_page(self):
        link_count = {}
        for id in self.idToTitle.keys():
            link_count[id] = 0
        for id in self.idToTitle.keys():
            for dst in self.links[id]:
                link_count[dst] += 1

        print("The most linked page is:")
        link_count_max = max(link_count.values())
        for dst in link_count.keys():
            if link_count[dst] == link_count_max:
                print(self.idToTitle[dst], link_count_max)
        print()

    # Find the shortest path
    # |start|: String, the title of the start page
    # |goal|: String, the title of the goal page
    def find_shortest_path(self, start, goal):
        start_id = self.titleToId.get(start)
        goal_id = self.titleToId.get(goal)
        if not (start_id and goal_id):
            print("Page Not Found")
            return
        bfs_queue = deque()
        bfs_queue.append([start_id])
        visited = set()
        while bfs_queue:
            ids = bfs_queue.popleft()
            print(ids)
            dsts = self.links[ids[-1]]
            for dst in dsts:
                if dst == goal_id:
                    print("The shortest path from " + start + " to " + goal + " is:")
                    path = ""
                    for id in ids:
                        path += self.idToTitle[id] + " -> "
                    path += goal
                    print(path)
                    print()
                    return
                if dst not in visited:
                    new_ids = ids.copy()
                    new_ids.append(dst)
                    bfs_queue.append(new_ids)
        print("Path Not Found")

    # The following function using numpy fails for medium and large databases
    # This is an eroor message when trying to run using the medium database
    # numpy.core._exceptions._ArrayMemoryError: Unable to allocate 2.90 TiB for an array with shape (631853, 631853) and data type float64

    # Find the page with the highest page rank
    def find_most_popular_page(self):
        num_pages = len(self.idToTitle)

        # ratio of distributing the rank to all nodes
        r = 0.15

        # dict {id : Integer, index of the matrix : Integer}
        idToIndex = {}
        count = 0
        for id in self.idToTitle:
            idToIndex[id] = count
            count += 1
        assert count == num_pages

        # matrix of num_pages x num_pages
        # row    : destination page
        # column : source page
        # If there is a link from j to i, link_matrix[j][i] = 1 / (#links from j)
        link_matrix = np.zeros((num_pages , num_pages))
        for src_id, src_index in idToIndex.items():
            num_dsts = len(self.links[src_id]) or num_pages
            for dst_id in self.links[src_id]:
                link_matrix[idToIndex[dst_id]][src_index] = (1 - r) / num_dsts
        
        # vector of num_pages
        page_ranks = np.ones(num_pages)

        # Iteratavely calculate page ranks until they converge
        while True:
            page_ranks_pre = page_ranks.copy()
            page_ranks = r + link_matrix.dot(page_ranks)
            page_ranks_progress = np.abs(page_ranks - page_ranks_pre)
            if np.all(page_ranks_progress < 1e-6):
                print("The most popular page is")
                max_index = np.argmax(page_ranks)
                for id, index in idToIndex.items():
                    if max_index == index:
                        print(self.idToTitle[id])
                        return

def analyse_runner(db_name) :
    page_file = "database/pages_" + db_name + ".txt"
    link_file = "database/links_" + db_name + ".txt"
    wikipedia = Wikipedia(page_file, link_file)
    wikipedia.find_longest_title()
    wikipedia.find_most_linked_page()
    titles = list(wikipedia.idToTitle.values())
    for _ in range(5):
        src = random.choice(titles)
        dst = random.choice(titles)
        wikipedia.find_shortest_path(src, dst)
    wikipedia.find_most_popular_page()

# Takes the name of the database (e.g) 'small', 'medium', 'large')
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: %s pages_file links_file" % sys.argv[0])
        exit(1)
    analyse_runner(sys.argv[1])
