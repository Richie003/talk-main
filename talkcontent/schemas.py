class CollegeCourses:
    courses_offered = {
        "Sciences": [
            "Computer Science",
            "Mathematics",
            "Statistics",
            "Biochemistry",
            "Microbiology",
            "Physics",
            "Chemistry",
            "Botany",
            "Zoology"
        ],
        "Engineering": [
            "Civil Engineering",
            "Electrical and Electronics Engineering",
            "Electrical/Electronics Engineering",
            "Chemical Engineering",
            "Computer Engineering",
            "Petroleum Engineering",
            "Agricultural Engineering",
            "Metallurgical and Materials Engineering"
        ],
        "Medicine and Health Sciences": [
            "Medicine and Surgery",
            "Nursing Science",
            "Dentistry",
            "Medical Laboratory Science",
            "Pharmacy",
            "Anatomy",
            "Physiology",
            "Public Health"
        ],
        "Social Sciences": [
            "Economics",
            "Political Science",
            "Sociology",
            "Psychology",
            "Geography",
            "Criminology and Security Studies",
            "Peace and Conflict Resolution"
        ],
        "Arts and Humanities": [
            "English Language",
            "History and International Studies",
            "Linguistics",
            "Philosophy",
            "Religious Studies",
            "Theatre Arts",
            "Fine and Applied Arts"
        ],
        "Law": [
            "Law"
        ],
        "Education": [
            "Education and Mathematics",
            "Education and English Language",
            "Education and Physics",
            "Education and Biology",
            "Education and Computer Science",
            "Educational Administration and Planning",
            "Guidance and Counselling"
        ],
        "Management and Administration": [
            "Accounting",
            "Business Administration",
            "Banking and Finance",
            "Marketing",
            "Public Administration",
            "Insurance",
            "Entrepreneurship"
        ],
        "Environmental Sciences": [
            "Architecture",
            "Estate Management",
            "Urban and Regional Planning",
            "Quantity Surveying",
            "Environmental Management",
            "Surveying and Geoinformatics",
            "Building Technology"
        ],
        "Agricultural Sciences": [
            "Agronomy",
            "Animal Science",
            "Crop Science",
            "Fisheries",
            "Forestry and Wildlife Management",
            "Soil Science",
            "Agricultural Economics and Extension"
        ]
    }

    def __init__(self):
        self.courses = self.courses_offered

    def get_courses_offered(self):
        return self.courses

    def get_courses_by_category(self, category):
        return self.courses.get(category, [])

    def get_all_courses(self):
        all_courses = [course for courses in self.courses.values()
                       for course in courses]
        return all_courses

    def get_all_categories(self):
        return list(self.courses.keys())
