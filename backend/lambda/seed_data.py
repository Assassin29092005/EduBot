"""Seed DynamoDB EduBot-Courses table with sample course data.

Usage:
    python seed_data.py
"""

import boto3

TABLE_NAME = "EduBot-Courses"
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table(TABLE_NAME)

COURSES = [
    {
        "course_id": "CS101",
        "course_name": "Introduction to Computer Science",
        "professor": "Dr. Alice Chen",
        "professor_email": "achen@university.edu",
        "office_hours": "Mon & Wed 2:00 PM - 4:00 PM, Room 305",
        "schedule": "Mon/Wed/Fri 10:00 AM - 11:00 AM",
        "location": "Science Building, Room 210",
        "syllabus": (
            "Week 1-3: Programming fundamentals (variables, loops, conditionals)\n"
            "Week 4-6: Data structures (arrays, lists, dictionaries)\n"
            "Week 7-9: Object-oriented programming\n"
            "Week 10-12: Algorithms and complexity\n"
            "Week 13-15: Final project and review"
        ),
        "assignments": [
            {"name": "Homework 1 - Python Basics", "due_date": "2026-04-05"},
            {"name": "Homework 2 - Data Structures", "due_date": "2026-04-19"},
            {"name": "Midterm Project", "due_date": "2026-05-03"},
            {"name": "Final Project", "due_date": "2026-06-01"},
        ],
    },
    {
        "course_id": "MATH201",
        "course_name": "Calculus II",
        "professor": "Dr. Robert Martinez",
        "professor_email": "rmartinez@university.edu",
        "office_hours": "Tue & Thu 1:00 PM - 3:00 PM, Room 412",
        "schedule": "Tue/Thu 9:00 AM - 10:30 AM",
        "location": "Mathematics Hall, Room 101",
        "syllabus": (
            "Week 1-3: Techniques of integration\n"
            "Week 4-6: Applications of integration\n"
            "Week 7-9: Sequences and series\n"
            "Week 10-12: Power series and Taylor series\n"
            "Week 13-15: Review and final exam prep"
        ),
        "assignments": [
            {"name": "Problem Set 1 - Integration Techniques", "due_date": "2026-04-07"},
            {"name": "Problem Set 2 - Applications", "due_date": "2026-04-21"},
            {"name": "Midterm Exam", "due_date": "2026-05-05"},
            {"name": "Final Exam", "due_date": "2026-06-05"},
        ],
    },
    {
        "course_id": "ENG110",
        "course_name": "English Composition",
        "professor": "Prof. Sarah Johnson",
        "professor_email": "sjohnson@university.edu",
        "office_hours": "Mon & Fri 11:00 AM - 1:00 PM, Room 208",
        "schedule": "Mon/Wed 1:00 PM - 2:30 PM",
        "location": "Humanities Building, Room 305",
        "syllabus": (
            "Week 1-3: Essay structure and thesis development\n"
            "Week 4-6: Research methods and source evaluation\n"
            "Week 7-9: Argumentative writing\n"
            "Week 10-12: Revision and peer review techniques\n"
            "Week 13-15: Portfolio compilation and presentation"
        ),
        "assignments": [
            {"name": "Essay 1 - Personal Narrative", "due_date": "2026-04-10"},
            {"name": "Essay 2 - Research Paper Draft", "due_date": "2026-04-28"},
            {"name": "Essay 3 - Argumentative Essay", "due_date": "2026-05-15"},
            {"name": "Final Portfolio", "due_date": "2026-06-03"},
        ],
    },
    {
        "course_id": "PHYS150",
        "course_name": "Physics I - Mechanics",
        "professor": "Dr. James Park",
        "professor_email": "jpark@university.edu",
        "office_hours": "Wed & Fri 3:00 PM - 5:00 PM, Room 118",
        "schedule": "Tue/Thu 11:00 AM - 12:30 PM",
        "location": "Physics Lab, Room 102",
        "syllabus": (
            "Week 1-3: Kinematics and vectors\n"
            "Week 4-6: Newton's laws and applications\n"
            "Week 7-9: Work, energy, and momentum\n"
            "Week 10-12: Rotational motion\n"
            "Week 13-15: Oscillations and review"
        ),
        "assignments": [
            {"name": "Lab Report 1 - Motion", "due_date": "2026-04-08"},
            {"name": "Lab Report 2 - Forces", "due_date": "2026-04-22"},
            {"name": "Midterm Exam", "due_date": "2026-05-06"},
            {"name": "Lab Report 3 - Energy", "due_date": "2026-05-20"},
            {"name": "Final Exam", "due_date": "2026-06-04"},
        ],
    },
    {
        "course_id": "HIST220",
        "course_name": "World History: Modern Era",
        "professor": "Dr. Maria Rodriguez",
        "professor_email": "mrodriguez@university.edu",
        "office_hours": "Tue 2:00 PM - 4:00 PM, Room 310",
        "schedule": "Mon/Wed/Fri 11:00 AM - 12:00 PM",
        "location": "Liberal Arts Building, Room 201",
        "syllabus": (
            "Week 1-3: The Enlightenment and revolutions\n"
            "Week 4-6: Industrialization and imperialism\n"
            "Week 7-9: World Wars and global conflict\n"
            "Week 10-12: Cold War and decolonization\n"
            "Week 13-15: Globalization and the modern world"
        ),
        "assignments": [
            {"name": "Reading Response 1", "due_date": "2026-04-06"},
            {"name": "Primary Source Analysis", "due_date": "2026-04-20"},
            {"name": "Midterm Essay", "due_date": "2026-05-04"},
            {"name": "Research Paper", "due_date": "2026-05-25"},
            {"name": "Final Exam", "due_date": "2026-06-06"},
        ],
    },
    {
        "course_id": "BIO101",
        "course_name": "Introduction to Biology",
        "professor": "Dr. Emily Watson",
        "professor_email": "ewatson@university.edu",
        "office_hours": "Mon & Thu 10:00 AM - 12:00 PM, Room 415",
        "schedule": "Tue/Thu 2:00 PM - 3:30 PM",
        "location": "Life Sciences Building, Room 150",
        "syllabus": (
            "Week 1-3: Cell biology and biochemistry\n"
            "Week 4-6: Genetics and molecular biology\n"
            "Week 7-9: Evolution and biodiversity\n"
            "Week 10-12: Ecology and ecosystems\n"
            "Week 13-15: Human biology and review"
        ),
        "assignments": [
            {"name": "Lab Report 1 - Cell Observation", "due_date": "2026-04-09"},
            {"name": "Genetics Problem Set", "due_date": "2026-04-23"},
            {"name": "Midterm Exam", "due_date": "2026-05-07"},
            {"name": "Ecology Field Report", "due_date": "2026-05-21"},
            {"name": "Final Exam", "due_date": "2026-06-05"},
        ],
    },
    {
        "course_id": "ECON300",
        "course_name": "Microeconomics",
        "professor": "Dr. David Kim",
        "professor_email": "dkim@university.edu",
        "office_hours": "Wed 1:00 PM - 3:00 PM, Room 220",
        "schedule": "Mon/Wed 3:00 PM - 4:30 PM",
        "location": "Business School, Room 108",
        "syllabus": (
            "Week 1-3: Supply, demand, and market equilibrium\n"
            "Week 4-6: Consumer and producer theory\n"
            "Week 7-9: Market structures (perfect competition, monopoly)\n"
            "Week 10-12: Game theory and strategic behavior\n"
            "Week 13-15: Market failures and government policy"
        ),
        "assignments": [
            {"name": "Problem Set 1 - Supply & Demand", "due_date": "2026-04-11"},
            {"name": "Problem Set 2 - Consumer Theory", "due_date": "2026-04-25"},
            {"name": "Midterm Exam", "due_date": "2026-05-09"},
            {"name": "Case Study Analysis", "due_date": "2026-05-23"},
            {"name": "Final Exam", "due_date": "2026-06-07"},
        ],
    },
    {
        "course_id": "PSY100",
        "course_name": "Introduction to Psychology",
        "professor": "Dr. Lisa Thompson",
        "professor_email": "lthompson@university.edu",
        "office_hours": "Fri 10:00 AM - 12:00 PM, Room 330",
        "schedule": "Tue/Thu 4:00 PM - 5:30 PM",
        "location": "Social Sciences Building, Room 205",
        "syllabus": (
            "Week 1-3: History and methods of psychology\n"
            "Week 4-6: Biological bases of behavior\n"
            "Week 7-9: Learning, memory, and cognition\n"
            "Week 10-12: Development and personality\n"
            "Week 13-15: Social psychology and abnormal behavior"
        ),
        "assignments": [
            {"name": "Reflection Paper 1", "due_date": "2026-04-12"},
            {"name": "Research Article Review", "due_date": "2026-04-26"},
            {"name": "Midterm Exam", "due_date": "2026-05-10"},
            {"name": "Group Presentation", "due_date": "2026-05-24"},
            {"name": "Final Exam", "due_date": "2026-06-08"},
        ],
    },
]


def seed():
    """Write all sample courses to DynamoDB."""
    for course in COURSES:
        table.put_item(Item=course)
        print(f"Seeded: {course['course_id']} - {course['course_name']}")
    print(f"\nDone! {len(COURSES)} courses seeded into {TABLE_NAME}.")


if __name__ == "__main__":
    seed()
