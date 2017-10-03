import igraph as ig
from utility import *

personal_user_id = "user_id_here"

network = ig.Graph(directed=True)
print(network)

# Store every node in the network for checks and preventing duplicates
all_nodes = {}
all_edges = {}

# Read through personal friends list, create nodes for each person
friend_dict = load_personal_friend_profiles_dict()
node_list = []
for key in friend_dict:
    # Create a node
    friend_id = get_friend_id_from_link(key)
    if friend_id not in all_nodes:
        node_list.append(friend_id)
        all_nodes[friend_id] = 1
    else:
        print("Duplicate friend: " + friend_id)
# Don't forget yourself
node_list.append(personal_user_id)
all_nodes[personal_user_id] = 1

network.add_vertices(node_list)
# print(network)

# Get every friend that you have stored
files = []
for (dirpath, dirnames, filenames) in walk("friends/"):
    files.extend(filenames)
    break

# Add any people who weren't in your friend's list to the network -- this accounts for public friends in case
# we ever decide to crawl them too.
node_list = []
for friend_file_name in files:
    friend_name = friend_file_name.split('.', 1)[0]
    if friend_name not in all_nodes:
        node_list.append(friend_name)
        all_nodes[friend_name] = 1
network.add_vertices(node_list)

# Now create connections between the user and their friends
edge_list = []
for key in friend_dict:
    friend_id = get_friend_id_from_link(key)
    if friend_id not in all_edges:
        edge = (personal_user_id, friend_id)
        edge_list.append(edge)
        all_edges[personal_user_id] = friend_id
network.add_edges(edge_list)
print(network)

# Make connections between friends and nodes in network
index = 0
for friend_file_name in files:
    friend_name = friend_file_name.split('.', 1)[0]
    # if index == 10:
    #     break
    edge_list = []
    node_list = []
    friend_list = load_friend_profiles("friends/" + friend_file_name)
    for friend_link in friend_list:
        friend_id = get_friend_id_from_link(friend_link)
        if friend_id in all_nodes:
            if friend_name in all_edges and all_edges[friend_name] == friend_id or \
                                    friend_id in all_edges and all_edges[friend_id] == friend_name:
                print("Edge already exists. Skipping.")
            else:
                # The friend is one that we already know of. Add an edge between the current friend and this one.
                # print(friend_id + " already exists")
                # Remember that friend_file_name is also the id of the current friend we're looking at
                edge = (friend_name, friend_id)
                edge_list.append(edge)
                all_edges[friend_name] = friend_id
        else:
            # We haven't seen this person before. Create a new node and edge
            node_list.append(friend_id)
            all_nodes[friend_id] = 1
            edge = (friend_name, friend_id)
            edge_list.append(edge)
            all_edges[friend_name] = friend_id
    network.add_vertices(node_list)
    network.add_edges(edge_list)
    index += 1
write_network(network, "network")
