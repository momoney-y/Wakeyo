import random
from datetime import datetime

WORD = { "hello": "Used for greeting", "world": "Description of universe" }

values_list = list(WORD.values())
keys_list = list(WORD.keys())

def puzzle_word():
    running = True

    while running:
        i = random.randint(0, len(WORD))
        word = keys_list[i];
        des = values_list[i];
        user_input = input(f"Guess the word {des}: ")
        print(user_input)
        if word == user_input:
            running = False
            print("U guessed the word correctly")
        else:
            print("You guessed the word incorrectly")

def get_time_from_user():
    hour = int(input("Enter Hour range(0..24): "))
    if hour > 24 or hour < 0:
        print("You entered an invalid hour go back and renter")
        return -1
    min = int(input("Enter Minute range(0..60): "))
    if min > 60 or min < 0:
        print("You entered an invalid minute go back and renter")
        return -1
    sec = int(input("Enter second range(0..60): "))
    if sec > 60 or sec < 0:
        print("You entered an invalid minute go back and renter")
        return -1
    return (hour,min, sec)

def get_current_time():
    now = datetime.now()

    hour = now.hour
    minute = now.minute
    second = now.second

    return (hour,minute, second)

def set_alarm(current_time, user_time):
    for current_time[2] - user_time[2] > 0:
        hour_left   = current_time[0] - user_time[0]
        minute_left = current_time[1] - user_time[1]
        user_time[2]    -= 1
        current_time[2] -= 1
        if current_time[2] - user_time[2] < 0:
            current_time[2] = 60
            user_time[2] = 60

if __main__ == "__name__":
    user_time = get_time_from_user()
    current_time = get_current_time()
    set_alarm(current_time, user_time)
    # TODO: Add the puzzel and finish it
