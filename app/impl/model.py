class Class:
    def __init__(self, groups, teacher, subject, type, duration, classrooms):
        self.groups = groups
        self.teacher = teacher
        self.subject = subject
        self.type = type
        self.duration = duration
        self.classrooms = classrooms

    def __str__(self):
        return "Groups {} | Teacher '{}' | Subject '{}' | Type {} | {} hours | Classrooms {} \n".format(
            self.groups,
            self.teacher,
            self.subject,
            self.type,
            self.duration,
            self.classrooms,
        )

    def __repr__(self):
        return str(self)


class Classroom:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __str__(self):
        return "{} - {} \n".format(self.name, self.type)

    def __repr__(self):
        return str(self)


class FileDetail:
    def __init__(self) -> None:
        self.source_file_name = None
        self.source_file_path = None
        self.source_file_contents = None

        self.target_file_name = None
        self.scheduled_file_contents = None
        self.solution_file_contents = None

        self.classes = None
        self.classrooms = None
        self.teachers = None
        self.groups = None
        self.class_list = None

        self.matrix = None
        self.free = None

        self.filled = {}
        self.subjects_order = {}
        self.groups_empty_space = {}
        self.teachers_empty_space = {}

        self.total_cost = None
        self.cost_class = None
        self.cost_teacher = None
        self.cost_classrooms = None
        self.cost_group = None

        self.empty_groups = None
        self.max_empty_group = None
        self.average_empty_groups = None

        self.empty_teachers = None
        self.max_empty_teacher = None
        self.average_empty_teachers = None

        self.free_hours = None
