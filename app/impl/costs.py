from .model import *


def subjects_order_cost(filedetails: FileDetail):
    """
    Calculates percentage of soft constraints - order of subjects (P, V, L).
    """
    # number of subjects not in right order
    cost = 0
    # number of all orders of subjects
    total = 0

    for (subject, group_index), times in filedetails.subjects_order.items():

        if times[0] != -1 and times[1] != -1:
            total += 1
            # P after V
            if times[0] > times[1]:
                cost += 1

        if times[0] != -1 and times[2] != -1:
            total += 1
            # P after L
            if times[0] > times[2]:
                cost += 1

        if times[1] != -1 and times[2] != -1:
            total += 1
            # V after L
            if times[1] > times[2]:
                cost += 1

    return 100 * (total - cost) / total


def empty_space_groups_cost(filedetails: FileDetail):
    """
    Calculates total empty space of all groups for week, maximum empty space in day and average empty space for whole
    week per group.
    """
    # total empty space of all groups for the whole week
    cost = 0
    # max empty space in one day for some group
    max_empty = 0

    for group_index, times in filedetails.groups_empty_space.items():
        times.sort()
        # empty space for each day for current group
        empty_per_day = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}

        for i in range(1, len(times) - 1):
            a = times[i - 1]
            b = times[i]
            diff = b - a
            # classes are in the same day if their time div 12 is the same
            if a // 12 == b // 12 and diff > 1:
                empty_per_day[a // 12] += diff - 1
                cost += diff - 1

        # compare current max with empty spaces per day for current group
        for key, value in empty_per_day.items():
            if max_empty < value:
                max_empty = value

    filedetails.empty_groups = cost
    filedetails.max_empty_group = max_empty
    filedetails.average_empty_groups = cost / len(filedetails.groups_empty_space)


def empty_space_teachers_cost(filedetails: FileDetail):
    """
    Calculates total empty space of all teachers for week, maximum empty space in day and average empty space for whole
    week per teacher.
    """
    # total empty space of all teachers for the whole week
    cost = 0
    # max empty space in one day for some teacher
    max_empty = 0

    for teacher_name, times in filedetails.teachers_empty_space.items():
        times.sort()
        # empty space for each day for current teacher
        empty_per_day = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}

        for i in range(1, len(times) - 1):
            a = times[i - 1]
            b = times[i]
            diff = b - a
            # classes are in the same day if their time div 12 is the same
            if a // 12 == b // 12 and diff > 1:
                empty_per_day[a // 12] += diff - 1
                cost += diff - 1

        # compare current max with empty spaces per day for current teacher
        for key, value in empty_per_day.items():
            if max_empty < value:
                max_empty = value

    filedetails.empty_teachers = cost
    filedetails.max_empty_teacher = max_empty
    filedetails.average_empty_teachers = cost / len(filedetails.teachers_empty_space)


def free_hour(filedetails: FileDetail):
    """
    Checks if there is an hour without classes. If so, returns it in format 'day: hour', otherwise -1.
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    hours = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

    for i in range(len(filedetails.matrix)):
        exists = True
        for j in range(len(filedetails.matrix[i])):
            field = filedetails.matrix[i][j]
            if field is not None:
                exists = False

        if exists:
            filedetails.free_hours = "{}: {}".format(days[i // 12], hours[i % 12])

    filedetails.free_hours = -1


def hard_constraints_cost(filedetails: FileDetail):
    """
    Calculates total cost of hard constraints: in every classroom is at most one class at a time, every class is in one
    of his possible classrooms, every teacher holds at most one class at a time and every group attends at most one
    class at a time.
    For everything that does not satisfy these constraints, one is added to the cost.
    """
    # cost_class: dictionary where key = index of a class, value = total cost of that class
    cost_class = {}
    for c in filedetails.classes:
        cost_class[c] = 0

    cost_classrooms = 0
    cost_teacher = 0
    cost_group = 0
    for i in range(len(filedetails.matrix)):
        for j in range(len(filedetails.matrix[i])):
            field = filedetails.matrix[i][j]  # for every field in matrix
            if field is not None:
                c1 = filedetails.classes[field]  # take class from that field

                # calculate loss for classroom
                if j not in c1.classrooms:
                    cost_classrooms += 1
                    cost_class[field] += 1

                for k in range(
                    j + 1, len(filedetails.matrix[i])
                ):  # go through the end of row
                    next_field = filedetails.matrix[i][k]
                    if next_field is not None:
                        c2 = filedetails.classes[next_field]  # take class of that field

                        # calculate loss for teachers
                        if c1.teacher == c2.teacher:
                            cost_teacher += 1
                            cost_class[field] += 1

                        # calculate loss for groups
                        g1 = c1.groups
                        g2 = c2.groups
                        for g in g1:
                            if g in g2:
                                cost_group += 1
                                cost_class[field] += 1

    filedetails.total_cost = cost_teacher + cost_classrooms + cost_group
    filedetails.cost_class = cost_class
    filedetails.cost_teacher = cost_teacher
    filedetails.cost_classrooms = cost_classrooms
    filedetails.cost_group = cost_group


def check_hard_constraints(filedetails: FileDetail):
    """
    Checks if all hard constraints are satisfied, returns number of overlaps with classes, classrooms, teachers and
    groups.
    """
    overlaps = 0
    for i in range(len(filedetails.matrix)):
        for j in range(len(filedetails.matrix[i])):
            field = filedetails.matrix[i][j]  # for every field in matrix
            if field is not None:
                c1 = filedetails.classes[field]  # take class from that field

                # calculate loss for classroom
                if j not in c1.classrooms:
                    overlaps += 1

                for k in range(len(filedetails.matrix[i])):  # go through the end of row
                    if k != j:
                        next_field = filedetails.matrix[i][k]
                        if next_field is not None:
                            c2 = filedetails.classes[
                                next_field
                            ]  # take class of that field

                            # calculate loss for teachers
                            if c1.teacher == c2.teacher:
                                overlaps += 1

                            # calculate loss for groups
                            g1 = c1.groups
                            g2 = c2.groups
                            for g in g1:
                                if g in g2:
                                    overlaps += 1

    return overlaps
