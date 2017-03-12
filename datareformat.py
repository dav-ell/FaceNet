from utility import *
from os import walk

files = []
for (dirpath, dirnames, filenames) in walk("friends/"):
    files.extend(filenames)
    break

for file_name in files:
    content = None
    with open("friends/" + file_name, "r") as f:
        content = [x.strip() for x in f.readlines()]
    with open("friends-reformat/" + file_name, "w") as nf:
        for line in content:
            friend_id = get_friend_id_from_link(line)
            nf.write(friend_id + "\n")
