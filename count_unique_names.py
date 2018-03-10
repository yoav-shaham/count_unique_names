#------imports----
import csv
from sys import argv
#----------------

EditDistanceConst = 5

def check_nick(name, nickname):
    """
    :param name: string containing the alleged name
    :param nickname: string containing the alleged nickname
    :type name: str
    :type nickname: str
    :return: returns a list containing the confirmed [name,nickname]
    :rtype: list
    """
    with open('nicknames.csv') as NickNamesList:
        nicknames = []
        csv_reader = csv.reader(NickNamesList)
        for row in csv_reader:
            list_name = row[1][1::]  # removing spaces
            list_nickname = row[2][1::]
            if name == list_name and list_nickname == nickname:
                return True
        return False


def edit_distance(name1, name2,
                  costs=(2, 4, 1)):  # an algorithem that uses a variation of the levenshtein distance algorithem
    """
    an algorithem that uses a variation of the levenshtein distance algorithem and baisically the same except for the fact that this takes into account the distance between keys
    :param name1: The "first" name totally arbitrary just for ease of reading
    :param name2: The "second" name totally arbitrary just for ease of reading
    :param costs: the cost of adding dleteing or inserting
    :return: the cost of turning name1 into name 2
    """

    rows = len(name1) + 1
    cols = len(name2) + 1
    delete_cost, insert_cost, subsitutes = costs
    distances = [[0 for x in range(cols)] for x in range(rows)]
    for row in range(1, rows):
        distances[row][0] = delete_cost * row

    for col in range(1, cols):
        distances[0][col] = insert_cost * col

    for col in range(1, cols):
        for row in range(1, rows):
            if name1[row - 1] == name2[col - 1]:
                cost = 0
            else:
                cost = subsitutes
            distances[row][col] = min(
                distances[row - 1][col] + delete_cost,
                distances[row][col - 1] + insert_cost,
                distances[row - 1][col - 1] + find_key_distance(name1[row - 1], name2[col - 1], cost)
            )

    return distances[rows - 1][cols - 1]


def find_key_distance(letter1, letter2, cost):
    loc_letter1 = get_pos(letter1)
    loc_letter2 = get_pos(letter2)
    return ((loc_letter1[0] - loc_letter2[0]) ** 2 + (loc_letter1[1] - loc_letter2[1]) ** 2) * cost


def get_pos(letter):
    """
    Gets the (x,y)/(row,column) coordinate of the given letter
    :param letter: a char with the letter which the outer function wants to find its location
    :return: the position of the letter
    """
    keyboard = [
        ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '='],
        ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
        ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\''],
        ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/'],
        ['', '', ' ', ' ', ' ', ' ', ' ', '', '']
    ]
    letter = letter.lower()
    for r in keyboard:
        if letter in r:
            row = keyboard.index(r)
            column = r.index(letter)
            return (row, column)
    raise ValueError(letter + " was not found")


def count_unique_names(bill_first_name, bill_last_name, ship_first_name, ship_last_name, bill_name_on_card):
    """
    Uses all of the aid functions to establish to high degree of accuracy the number of unique names
    :param bill_first_name: the name as written in the purchase page of the first name on bill
    :param bill_last_name: the name as written in the purchase page of the last name on bill
    :param ship_first_name: the name as written in the purchase page of the shipping first name
    :param ship_last_name: the name as written in the purchase page of the shipping last name
    :param bill_name_on_card: the name on the card as entered by the user
    :return: returns the number of unique names
    """
    bill_first_name, bill_last_name = cleanup(bill_first_name, bill_last_name)
    ship_first_name, ship_last_name = cleanup(ship_first_name, ship_last_name)
    names = [[bill_first_name, bill_last_name], [ship_first_name, ship_last_name]]
    for full_name in range(0, len(names)):
        for name in range(0, len(names[full_name])):
            for key in bill_name_on_card.split((" ")):
                if check_nick(key, names[full_name][name]):
                    names[full_name][name] = key

    (bill_first_name, bill_last_name) = names[0]
    (ship_first_name, ship_last_name) = names[1]
    info = analyze_billNameOnCard(bill_first_name, bill_last_name, ship_first_name, ship_last_name, bill_name_on_card)
    result=info + analyze_name(names)
    print result
    return info + analyze_name(names)


def cleanup(first_name, last_name):
    """
    takes the first and last name and baisically cleans them up so if the first name contains the first letter of the last name it is earased
    :param first_name: first name
    :param last_name: the last name
    :return: the parsed names
    """
    split_first = first_name.split(" ")
    if len(split_first) > 1:
        if split_first[1] == last_name[0]:
            return (split_first[0], last_name)
        else:
            return (first_name, last_name)
    else:
        return (first_name, last_name)


def analyze_billNameOnCard(bill_first_name, bill_last_name, ship_first_name, ship_last_name, bill_name_on_card):
    """
    This funciton uses several other functions in order to establish if the bill_name_on_card is a unique name or not
    :param bill_first_name: the name as written in the purchase page of the first name on bill
    :param bill_last_name: the name as written in the purchase page of the last name on bill
    :param ship_first_name: the name as written in the purchase page of the shipping first name
    :param ship_last_name: the name as written in the purchase page of the shipping last name
    :param bill_name_on_card: the name on the card as entered by the user
    :return: returns either 1 or 0. 1 if the name is not unique and 0 if it is.
    """
    names = [[bill_first_name, bill_last_name], [ship_first_name, ship_last_name]]
    card_names = bill_name_on_card.split(" ")
    for name in card_names:
        data = analyze_name_on_card(name, names)
        changed_dict = 0

        for x in data.keys():
            if data[x]["nickname"] or data[x]["price_to_change"] < EditDistanceConst or data[x]["letter"]:
                changed_dict = 1
        if changed_dict == 0:
            return 1
    return 0


def analyze_name_on_card(checking_name, other_names):
    """
    analyzing the name on the card and returns a dictionarry full of helpful information for the above function to be
    able to tell if its a unique name or not
    :param checking_name:
    :param other_names:
    :return:
    """
    # ---------constants---------------
    FirstNamePos = 0
    LastNamePos = 1
    LastPosInfo = 3
    # ---------------------------------
    information = {}
    for other in other_names:
        for x in other:
            holder = x.split(" ")
            for name in holder:
                position = other.index(x)
                if position == LastNamePos:
                    position = LastPosInfo
                elif position == FirstNamePos:
                    position += holder.index(name) + 1
                if len(name) == 1 or len(checking_name) == 1:
                    is_letter = name[0] == checking_name[0]
                    information[name] = {
                        "price_to_change": edit_distance(checking_name, name),
                        "nickname": is_letter,
                        "place": position,
                        "letter": is_letter
                    }
                else:
                    information[name] = {
                        "price_to_change": edit_distance(checking_name, name),
                        "nickname": check_nick(name, checking_name),
                        "place": position,
                        "letter": False
                    }
    return information


def analyze_name(names):
    """
    Takes a list of two full names split into two then again two to be able to distinguis the names apart and tells
    whether they are the same or not.
    :param names: a list of names [[first,last],[first,last]]
    :return: returns either 1 or 2 depending on the answer if they are the same then 1 cus only one unique name
    otherwise 2
    """
    # ----------contants------
    FirstName = 0
    LastName = 1
    MiddleName = 1
    # ------------------------
    first = names[0]
    middle1=None
    middle2=None
    if len(first[FirstName].split(" ")) > 1:
        middle1 = first[FirstName].split(" ")[MiddleName]
        first = [first[FirstName].split(" ")[FirstName], first[LastName]]
    second = names[1]
    if len(second[FirstName].split(" ")) > 1:
        middle2 = second[FirstName].split(" ")[MiddleName]
        second = [second[FirstName].split(" ")[FirstName], second[LastName]]
    if (first[FirstName].lower() == second[FirstName].lower() or check_nick(first[FirstName].title(),
                                                                            second[FirstName].title()) or edit_distance(
            first[FirstName], second[FirstName]) < EditDistanceConst or check_nick(second[FirstName].title(),
                                                                                   first[FirstName].title())):
        if (first[LastName].lower() == second[LastName].lower() or edit_distance(first[LastName],
                                                                                 second[LastName]) < EditDistanceConst):
            if middle1!=None and middle2!=None:
                if (middle1.lower() == middle2.lower() or middle1[0] == middle2[0]) or (
                            len(middle1) > 1 and 1 < len(middle2) and edit_distance(middle1, middle2) < EditDistanceConst):
                    return 1
            else:
                return 1
    return 2


def main():
    test = False
    if test:
        print count_unique_names( "Deborah",  "Egli",  "Deborah",  "Egli",  "Deborah Egli")
        print count_unique_names( "Deborah",  "Egli",  "Debbie",  "Egli",  "Debbie Egli")
        print count_unique_names( "Deborah",  "Egni",  "Deborah",  "Egli",  "Deborah Egli")
        print count_unique_names( "Deborah S",  "Egli",  "Deborah",  "Egli",  "Egli Deborah")
        print count_unique_names( "Michele",  "Egli",  "Deborah",  "Egli",  "Michele Egli")
        print count_unique_names( "Daniel Iron","Rand","Danny I","Ranf","Luke Cage") # here due to the fact that "f"
    #here you can see aswell that it recognises the I as the first letter of Iron    # and "d" it is sean as a typo
                                                                                     # unlike "k" and "n"
    try:
        count_unique_names(argv[1],argv[2],argv[3],argv[4],argv[5])
    except:
        print "Please enter the input correctly i.e. \"Daniel Iron\",\"Rand\",\"Danny I\",\"Ranf\",\"Luke Cage\""
if __name__ == '__main__':
    main()
