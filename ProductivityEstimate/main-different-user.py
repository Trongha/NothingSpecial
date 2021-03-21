import csv

input_file_path = "resource/MOCK_DATA_2.csv"
# input_file_path = "resource/Mock_easy.csv"
input_file_delimiter = ','
output_file_path = "output_{username}.csv"
i_col_date_time = 0
i_col_duration_sec = 1
i_col_os_user = 2
i_col_category = 3
i_col_type_num = 4
i_col_mouse_move = 5

# --------------- configure for output ---------------#
# output_typing_num = [[0, 0, 0, 0] for i in range(0, 24)]
# # --> meaning: output_typing_num[hour][index of quarter of a hour] = productivity at this time
# output_mouse_move = [[0, 0, 0, 0] for i in range(0, 24)]
users = set()
output_typing_num = dict()
output_mouse_move = dict()


def add_new_user(username):
    users.add(username)
    new_output_typing_num = [[0, 0, 0, 0] for i in range(0, 24)]
    new_output_mouse_move = [[0, 0, 0, 0] for i in range(0, 24)]
    output_typing_num[username] = new_output_typing_num
    # --> meaning: output_typing_num[hour][index of quarter of a hour] = productivity at this time
    output_mouse_move[username] = new_output_mouse_move


# ----- Configure for interval -----#
interval_min = 15
interval_sec = 60 * interval_min
quarter_points = [0, 15, 30, 45, 60]
max_i_quarter_of_hour = 3
max_hour = 24


def increase_index_quarter_of_hour(hour, i_quarter_of_hour):
    i_quarter_of_hour += 1
    if i_quarter_of_hour > max_i_quarter_of_hour:
        i_quarter_of_hour = 0
        hour = (hour + 1) % max_hour
    return hour, i_quarter_of_hour


def add_productivity_at_time(username, hour, i_quarter_of_hour, typing_num_added, mouse_move_added):
    output_typing_num[username][hour][i_quarter_of_hour] += typing_num_added
    output_mouse_move[username][hour][i_quarter_of_hour] += mouse_move_added


def convert_input_to_output(username, start_hour, start_minute, duration_sec, typing_num, mouse_move):
    typing_num_per_sec = typing_num / duration_sec
    mouse_move_per_sec = mouse_move / duration_sec
    i_quarter_of_hour = start_minute // interval_min
    if (start_minute % interval_min != 0):
        remain_in_this_quarter_sec = 60 * (quarter_points[i_quarter_of_hour + 1] - start_minute)
        if (remain_in_this_quarter_sec >= duration_sec):
            add_productivity_at_time(username, start_hour, i_quarter_of_hour, typing_num, mouse_move)
            duration_sec = 0
        else:
            add_productivity_at_time(username, start_hour, i_quarter_of_hour,
                                     typing_num_added=typing_num_per_sec * remain_in_this_quarter_sec,
                                     mouse_move_added=mouse_move_per_sec * remain_in_this_quarter_sec)
            duration_sec -= remain_in_this_quarter_sec
        start_hour, i_quarter_of_hour = increase_index_quarter_of_hour(start_hour, i_quarter_of_hour)

    while duration_sec > 0:
        delta_sec = interval_sec if duration_sec > interval_sec else duration_sec
        add_productivity_at_time(username, start_hour, i_quarter_of_hour,
                                 typing_num_added=typing_num_per_sec * delta_sec,
                                 mouse_move_added=mouse_move_per_sec * delta_sec)
        duration_sec -= delta_sec
        start_hour, i_quarter_of_hour = increase_index_quarter_of_hour(start_hour, i_quarter_of_hour)


def output_to_csv(username):
    print("write to csv")
    output_typing_num_person = output_typing_num[username]
    output_mouse_move_person = output_mouse_move[username]
    output_content = ""
    for hour in range(max_hour):
        for i_quarter in range(4):
            line = ""
            line += '\'' + str(hour) + ':' + str(quarter_points[i_quarter]) + ','
            line += '\'' + str(hour) + ':' + str(quarter_points[i_quarter + 1]) + ','
            line += str(output_typing_num_person[hour][i_quarter]) + "," + str(
                output_mouse_move_person[hour][i_quarter])
            line += '\n'
            output_content += line
    f = open(output_file_path.format(username=username), "w")
    f.write(output_content)
    f.close()


if __name__ == '__main__':
    print('run main')
    with open(input_file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        is_header = True
        hour = 0
        minute = 0
        for row in csv_reader:
            if is_header:
                is_header = False
            else:
                username = row[i_col_os_user]
                if (username not in users):
                    add_new_user(username)

                hour, minute = row[i_col_date_time].split(' ')[-1].split(':')
                convert_input_to_output(username, int(hour), int(minute), int(row[i_col_duration_sec]),
                                        int(row[i_col_type_num]),
                                        int(row[i_col_mouse_move]))

    for username in users:
        output_to_csv(username)
    print("done")
