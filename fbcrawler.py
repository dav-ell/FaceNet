from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from colorama import Fore, Back, Style
import time
import sys
import threading
import numpy as np
from utility import *

friend_links_list_file = "friendlist.txt"
# Links are of the form: facebook_url + user_id + friends_url_extension
facebook_url = "https://www.facebook.com/"
friends_url_extension = "/friends"

# TODO: auto-set this
personal_profile_id = "profile_id_here"


def facebook_login(driver, username, password):
    print("\n\n\nLogin to Facebook...."),
    sys.stdout.flush()
    url = "http://www.facebook.com"
    driver.get(url)
    elem = driver.find_element_by_id("email")
    elem.send_keys(username)
    elem = driver.find_element_by_id("pass")
    elem.send_keys(password)
    elem.send_keys(Keys.RETURN)
    time.sleep(1)
    html_source = driver.page_source
    if "Please re-enter your password" in html_source or "Incorrect Email" in html_source:
        print(Fore.RED + "Incorrect Username or Password")
        driver.close()
        exit()
    else:
        print(Fore.GREEN + "Success\n")
    return driver.get_cookies()


def scroll_to_bottom(driver):
    ticks_at_bottom = 0
    while True:
        js_scroll_code = "if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight) {return true;} else {return false;}"
        if driver.execute_script(js_scroll_code):
            if ticks_at_bottom > 1000:
                break
            else:
                ticks_at_bottom += 1
        else:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            ticks_at_bottom = 0
    print("At bottom of page.")


def get_friends_profiles_dict(driver):
    """
    Gets the list of friends starting from a user's homepage.

    :return: array of friend profile links
    """
    scroll_to_bottom(driver)

    friend_profiles_dict = {}
    # friend_profiles = []
    # Iterate through list of friends
    friend_containers = driver.find_elements_by_xpath("//ul")
    for container in friend_containers:
        try:
            friend_elem_list = container.find_elements_by_xpath(".//li[@class='_698']")
            #    print("Found a friend list... I think: ", friend_list)
            for friend in friend_elem_list:
                # Try and get the name
                friend_box = friend.find_element_by_xpath(".//div[@class='fsl fwb fcb']")
                friend_box_parent = friend_box.find_element_by_xpath("..")

                friend_profile_link_tag = friend_box_parent.find_elements_by_xpath(".//a")[0]
                friend_profile_link = friend_profile_link_tag.get_attribute("href")

                friend_id = get_friend_id_from_link(friend_profile_link)
                if friend_id == "profilephp":
                    continue

                friend_friends_link_tag = friend_box_parent.find_elements_by_xpath(".//a")[1]
                friend_friends_link = friend_friends_link_tag.get_attribute("href")

                friend_profiles_dict[friend_profile_link] = friend_friends_link
                # friend_profiles.append(friend_profile_link)
                print(friend_profile_link)
        except:
            print("Not a friend container")
            continue
    # return friend_profiles
    return friend_profiles_dict


def get_friend_profiles(driver):
    """
    Gets the list of friends starting from a user's homepage.

    :return: array of friend profile ids
    """
    scroll_to_bottom(driver)

    friend_profiles_ids = []
    # Iterate through list of friends
    friend_containers = driver.find_elements_by_xpath("//ul")
    for container in friend_containers:
        # Note that this try-except section will take a much longer time to execute if a driver.implicit_wait() has been
        # called at any time prior to running this method. If you require an implicit_wait(), then call implicit_wait(0)
        # before entering this function.
        try:
            friend_elem_list = container.find_elements_by_xpath(".//li[@class='_698']")
            #    print("Found a friend list... I think: ", friend_list)
            for friend in friend_elem_list:
                # Try and get the name
                friend_box = friend.find_element_by_xpath(".//div[@class='fsl fwb fcb']")
                friend_box_parent = friend_box.find_element_by_xpath("..")

                friend_profile_link_tag = friend_box_parent.find_elements_by_xpath(".//a")[0]
                friend_profile_link = friend_profile_link_tag.get_attribute("href")

                friend_id = get_friend_id_from_link(friend_profile_link)
                if friend_id == "profilephp":
                    # TODO: allow unnamed profiles such as these to be processed; also figure out why FB uses this id in some cases
                    continue

                friend_profiles_ids.append(friend_id)
                print(friend_id)
        except:
            print("Not a friend container")
            continue
    # return friend_profiles
    return friend_profiles_ids


def write_friend_profiles_dict(profiles_dict):
    with open(friend_links_list_file, "w") as f:
        for key in profiles_dict:
            f.write(key + "|" + profiles_dict[key] + "\n")


def write_friend_profiles(file_name, profiles):
    with open("friends/" + file_name, "w") as f:
        for friend in profiles:
            f.write(friend + "\n")


def load_friend_profiles():
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


def wait():
    # driver.implicitly_wait(1)
    time.sleep(1)


def get_username_password():
    with open("login.txt", "r") as f:
        content = f.readline().strip().split(",")
        return content


def do_fb_crawl(driver, login_info, friend_profiles):
    facebook_login(driver, login_info[0], login_info[1])
    # For each friend, get the list of friends from their friend page
    for key in friend_profiles:
        friend_id = get_friend_id_from_link(key)
        if not os.path.isfile("friends/" + friend_id + ".txt"):
            print("Crawling friends page of", friend_id)
            friend_page = friend_profiles[key]
            # Go to page, get list of friends
            driver.get(friend_page)
            wait()
            friend_list = get_friend_profiles(driver)
            print("Got ", len(friend_list), " friends from ", friend_id)
            write_friend_profiles(friend_id + ".txt", friend_list)


def split_dict_equally(input_dict, chunks=2):
    "Splits dict by keys. Returns a list of dictionaries."
    # prep with empty dicts
    return_list = [dict() for _ in range(chunks)]
    idx = 0
    for k, v in input_dict.items():
        return_list[idx][k] = v
        if idx < chunks - 1:  # indexes start at 0
            idx += 1
        else:
            idx = 0
    return return_list


# Get friend profiles
base_driver = webdriver.Firefox()
login_info = get_username_password()

facebook_login(base_driver, login_info[0], login_info[1])
friend_profiles = None
if not os.path.isfile(friend_links_list_file):
    print("Friends profiles file (", friend_links_list_file, ") does not exist. Crawling friend page to create.")
    base_driver.get(facebook_url + personal_profile_id + friends_url_extension)
    wait()
    friend_profiles = get_friends_profiles_dict(base_driver)
    write_friend_profiles_dict(friend_profiles)
else:
    print("Loaded friend profiles from file.")
    friend_profiles = load_friend_profiles()

# Split profiles into separate files based on number of threads
num_threads = 4
# print("BEFORE SPLIT:", friend_profiles)
split_profiles = split_dict_equally(friend_profiles, num_threads)
# print("AFTER SPLIT:", split_profiles)

threads = []
for i in range(num_threads):
    driver = webdriver.PhantomJS("phantomjs/bin/phantomjs.exe")
    login_info = get_username_password()
    t = threading.Thread(target=do_fb_crawl, args=(driver, login_info, split_profiles[i]))
    t.daemon = True
    threads.append(t)

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()


# WARNING: this next section takes an extremely long time to run. What this section is doing is computing the friends
# of friends of friends (3 levels deep), which is many millions of people. Do not expect this section to finish.
