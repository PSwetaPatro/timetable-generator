import json
import random
from .costs import *
from .model import *


def load_data(filedetails: FileDetail):
    with open(filedetails.source_file_path) as file:
        filedetails.source_file_contents = file.read()
        data = json.loads(filedetails.source_file_contents)

    # classes: dictionary where key = index of a class, value = class
    filedetails.classes = {}
    # classrooms: dictionary where key = index, value = classroom name
    filedetails.classrooms = {}
    # teachers: dictionary where key = teachers' name, value = index
    filedetails.teachers = {}
    # groups: dictionary where key = name of the group, value = index
    filedetails.groups = {}
    filedetails.class_list = []

    for cl in data["Classes"]:
        new_group = cl["Groups"]
        new_teacher = cl["Mentor"]

        # initialise for empty space of teachers
        if new_teacher not in filedetails.teachers_empty_space:
            filedetails.teachers_empty_space[new_teacher] = []

        new = Class(
            new_group,
            new_teacher,
            cl["Subject"],
            cl["Tip"],
            cl["Duration"],
            cl["Classroom"],
        )
        # add groups
        for group in new_group:
            if group not in filedetails.groups:
                filedetails.groups[group] = len(filedetails.groups)
                # initialise for empty space of groups
                filedetails.groups_empty_space[filedetails.groups[group]] = []

        # add teacher
        if new_teacher not in filedetails.teachers:
            filedetails.teachers[new_teacher] = len(filedetails.teachers)
        filedetails.class_list.append(new)

    # shuffle mostly because of teachers
    random.shuffle(filedetails.class_list)
    # add classrooms
    for cl in filedetails.class_list:
        filedetails.classes[len(filedetails.classes)] = cl

    # every class is assigned a list of classrooms he can be in as indexes (later columns of matrix)
    for type in data["Classrooms"]:
        for name in data["Classrooms"][type]:
            new = Classroom(name, type)
            filedetails.classrooms[len(filedetails.classrooms)] = new

    # every class has a list of groups marked by its index, same for classrooms
    for i in filedetails.classes:
        cl = filedetails.classes[i]

        classroom = cl.classrooms
        index_classrooms = []
        # add classrooms
        for index, c in filedetails.classrooms.items():
            if c.type == classroom:
                index_classrooms.append(index)
        cl.classrooms = index_classrooms

        class_groups = cl.groups
        index_groups = []
        for name, index in filedetails.groups.items():
            if name in class_groups:
                # initialise order of subjects
                if (cl.subject, index) not in filedetails.subjects_order:
                    filedetails.subjects_order[(cl.subject, index)] = [-1, -1, -1]
                index_groups.append(index)
        cl.groups = index_groups


def set_up(filedetails: FileDetail):
    num_of_columns = len(filedetails.classrooms)
    w, h = num_of_columns, 60  # 5 (workdays) * 12 (work hours) = 60
    matrix = [[None for x in range(w)] for y in range(h)]
    free = []

    # initialise free dict as all the fields from matrix
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            free.append((i, j))
    filedetails.matrix = matrix
    filedetails.free = free


def show_timetable(filedetails: FileDetail):
    """
    Prints timetable matrix.
    """
    with open(f"scheduled_files/{filedetails.target_file_name}", "w") as f:
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        hours = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

        # print heading for classrooms
        for i in range(len(filedetails.matrix[0])):
            if i == 0:
                string = "{:17s} C{:6s}".format("", "0")
                f.write(string)
            else:
                string = "C{:6s}".format(str(i))
                f.write(string)
        f.write("\n")

        d_cnt = 0
        h_cnt = 0
        for i in range(len(filedetails.matrix)):
            day = days[d_cnt]
            hour = hours[h_cnt]
            string = "{:10s} {:2d} ->  ".format(day, hour)
            f.write(string)
            for j in range(len(filedetails.matrix[i])):
                string = "{:6s} ".format(
                    str(filedetails.matrix[i][j]) if filedetails.matrix[i][j] else ""
                )
                f.write(string)
            f.write("\n")
            h_cnt += 1
            if h_cnt == 12:
                h_cnt = 0
                d_cnt += 1
                f.write("\n")

    with open(f"scheduled_files/{filedetails.target_file_name}") as f:
        filedetails.scheduled_file_contents = f.read()


def write_solution_to_file(filedetails: FileDetail):
    """
    Writes statistics and schedule to file.
    """
    with open("solution_files/" + filedetails.target_file_name, "w") as f:
        f.write("-------------------------- STATISTICS --------------------------\n")
        cost_hard = check_hard_constraints(filedetails)
        if cost_hard == 0:
            f.write("\nHard constraints satisfied: 100.00 %\n")
        else:
            f.write("Hard constraints NOT satisfied, cost: {}\n".format(cost_hard))
        f.write(
            "Soft constraints satisfied: {:.02f} %\n\n".format(
                subjects_order_cost(filedetails)
            )
        )

        empty_space_groups_cost(filedetails)
        f.write(
            "TOTAL empty space for all GROUPS and all days: {}\n".format(
                filedetails.empty_groups
            )
        )
        f.write(
            "MAX empty space for GROUP in day: {}\n".format(filedetails.max_empty_group)
        )
        f.write(
            "AVERAGE empty space for GROUPS per week: {:.02f}\n\n".format(
                filedetails.average_empty_groups
            )
        )

        empty_space_teachers_cost(filedetails)
        f.write(
            "TOTAL empty space for all TEACHERS and all days: {}\n".format(
                filedetails.empty_teachers
            )
        )
        f.write(
            "MAX empty space for TEACHER in day: {}\n".format(
                filedetails.max_empty_teacher
            )
        )
        f.write(
            "AVERAGE empty space for TEACHERS per week: {:.02f}\n\n".format(
                filedetails.average_empty_teachers
            )
        )

        free_hour(filedetails)
        if filedetails.free_hours != -1:
            f.write("Free term -> {}\n".format(filedetails.free_hours))
        else:
            f.write("NO hours without classes.\n")

        groups_dict = {}
        for group_name, group_index in filedetails.groups.items():
            if group_index not in groups_dict:
                groups_dict[group_index] = group_name
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        hours = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

        f.write("\n--------------------------- SCHEDULE ---------------------------")
        for class_index, times in filedetails.filled.items():
            c = filedetails.classes[class_index]
            groups = " "
            for g in c.groups:
                groups += groups_dict[g] + ", "
            f.write("\n\nClass {}\n".format(class_index))
            f.write(
                "Teacher: {} \nSubject: {} \nGroups:{} \nType: {} \nDuration: {} hour(s)".format(
                    c.teacher, c.subject, groups[: len(groups) - 2], c.type, c.duration
                )
            )
            room = str(filedetails.classrooms[times[0][1]])
            f.write(
                "\nClassroom: {:2s}\nTime: {}".format(
                    room[: room.rfind("-")], days[times[0][0] // 12]
                )
            )
            for time in times:
                f.write(" {}".format(hours[time[0] % 12]))

    with open("solution_files/" + filedetails.target_file_name) as f:
        filedetails.solution_file_contents = f.read()


def show_statistics(filedetails: FileDetail):
    """
    Prints statistics.
    """
    cost_hard = check_hard_constraints(filedetails)
    if cost_hard == 0:
        print("Hard constraints satisfied: 100.00 %")
    else:
        print("Hard constraints NOT satisfied, cost: {}".format(cost_hard))
    print(
        "Soft constraints satisfied: {:.02f} %\n".format(
            subjects_order_cost(filedetails)
        )
    )

    empty_space_groups_cost(filedetails)
    print("TOTAL empty space for all GROUPS and all days: ", filedetails.empty_groups)
    print("MAX empty space for GROUP in day: ", filedetails.max_empty_group)
    print(
        "AVERAGE empty space for GROUPS per week: {:.02f}\n".format(
            filedetails.average_empty_groups
        )
    )

    empty_space_teachers_cost(filedetails)
    print(
        "TOTAL empty space for all TEACHERS and all days: ", filedetails.empty_teachers
    )
    print("MAX empty space for TEACHER in day: ", filedetails.max_empty_teacher)
    print(
        "AVERAGE empty space for TEACHERS per week: {:.02f}\n".format(
            filedetails.average_empty_teachers
        )
    )

    free_hour(filedetails)
    if filedetails.free_hours != -1:
        print("Free term ->", filedetails.free_hours)
    else:
        print("NO hours without classes.")
