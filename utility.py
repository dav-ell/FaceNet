import os.path
from urllib.parse import urlparse
from os import walk

friend_links_list_file = "friendlist.txt"


def load_personal_friend_profiles_dict():
    with open(friend_links_list_file, "r") as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        result_dict = {}
        for line in content:
            line_split = line.split("|")
            profile = line_split[0]
            friend_link = line_split[1]

            # Filter out possible bad input
            friend_id = get_friend_id_from_link(friend_link)
            if friend_id == "profilephp":
                continue

            result_dict[profile] = friend_link
        return result_dict


def load_friend_profiles(friend_file_name):
    with open(friend_file_name, "r") as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        return content


def get_friend_id_from_link(link):
    parsed_link = urlparse(link)
    friend_id = parsed_link.path.split('?', 1)[0].replace('.', '')[1:]
    return friend_id


def get_previously_search_friend_files():
    """
    :return: list of friend ids corresponding to those friends that have been searched and have files stored in the
    friends/ directory.
    """
    files = []
    for (dirpath, dirnames, filenames) in walk("friends/"):
        files.extend(filenames)
        break
    return files


def write_network(network, name):
    network.write(f="graphmls/" + name + ".graphml", format="graphml")