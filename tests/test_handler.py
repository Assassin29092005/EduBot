"""Unit tests for EduBot Lambda handler."""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Set environment variables before importing handler
os.environ["TABLE_NAME"] = "EduBot-Courses"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

# Add the lambda directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend", "lambda"))

from handler import lambda_handler


def make_lex_event(intent_name, slots=None):
    """Helper to create a mock Lex v2 event."""
    if slots is None:
        slots = {}
    return {
        "sessionState": {
            "intent": {
                "name": intent_name,
                "slots": slots,
            }
        }
    }


def make_slot(value):
    """Helper to create a slot with an interpreted value."""
    return {"value": {"interpretedValue": value}}


SAMPLE_COURSE = {
    "course_id": "CS101",
    "course_name": "Introduction to Computer Science",
    "professor": "Dr. Alice Chen",
    "professor_email": "achen@university.edu",
    "office_hours": "Mon & Wed 2:00 PM - 4:00 PM, Room 305",
    "schedule": "Mon/Wed/Fri 10:00 AM - 11:00 AM",
    "location": "Science Building, Room 210",
    "syllabus": "Week 1-3: Programming fundamentals\nWeek 4-6: Data structures",
    "assignments": [
        {"name": "Homework 1", "due_date": "2026-04-05"},
        {"name": "Midterm Project", "due_date": "2026-05-03"},
    ],
}


class TestGetCourseSyllabus(unittest.TestCase):
    @patch("handler.table")
    def test_returns_syllabus(self, mock_table):
        mock_table.get_item.return_value = {"Item": SAMPLE_COURSE}
        event = make_lex_event("GetCourseSyllabus", {"CourseId": make_slot("CS101")})

        result = lambda_handler(event, None)

        self.assertEqual(result["sessionState"]["dialogAction"]["type"], "Close")
        self.assertIn("Programming fundamentals", result["messages"][0]["content"])

    @patch("handler.table")
    def test_missing_slot_elicits(self, mock_table):
        event = make_lex_event("GetCourseSyllabus", {"CourseId": None})

        result = lambda_handler(event, None)

        self.assertEqual(result["sessionState"]["dialogAction"]["type"], "ElicitSlot")
        self.assertEqual(result["sessionState"]["dialogAction"]["slotToElicit"], "CourseId")

    @patch("handler.table")
    def test_course_not_found(self, mock_table):
        mock_table.get_item.return_value = {}
        event = make_lex_event("GetCourseSyllabus", {"CourseId": make_slot("FAKE999")})

        result = lambda_handler(event, None)

        self.assertEqual(result["sessionState"]["dialogAction"]["type"], "Close")
        self.assertIn("couldn't find", result["messages"][0]["content"])


class TestGetProfessorInfo(unittest.TestCase):
    @patch("handler.table")
    def test_returns_professor_info(self, mock_table):
        mock_table.get_item.return_value = {"Item": SAMPLE_COURSE}
        event = make_lex_event("GetProfessorInfo", {"CourseId": make_slot("CS101")})

        result = lambda_handler(event, None)

        self.assertEqual(result["sessionState"]["dialogAction"]["type"], "Close")
        content = result["messages"][0]["content"]
        self.assertIn("Dr. Alice Chen", content)
        self.assertIn("achen@university.edu", content)
        self.assertIn("Mon & Wed", content)

    @patch("handler.table")
    def test_missing_slot_elicits(self, mock_table):
        event = make_lex_event("GetProfessorInfo", {})

        result = lambda_handler(event, None)

        self.assertEqual(result["sessionState"]["dialogAction"]["type"], "ElicitSlot")


class TestGetClassSchedule(unittest.TestCase):
    @patch("handler.table")
    def test_returns_schedule(self, mock_table):
        mock_table.get_item.return_value = {"Item": SAMPLE_COURSE}
        event = make_lex_event("GetClassSchedule", {"CourseId": make_slot("CS101")})

        result = lambda_handler(event, None)

        self.assertEqual(result["sessionState"]["dialogAction"]["type"], "Close")
        content = result["messages"][0]["content"]
        self.assertIn("Mon/Wed/Fri", content)
        self.assertIn("Science Building", content)

    @patch("handler.table")
    def test_course_not_found(self, mock_table):
        mock_table.get_item.return_value = {}
        event = make_lex_event("GetClassSchedule", {"CourseId": make_slot("NONE100")})

        result = lambda_handler(event, None)

        self.assertIn("couldn't find", result["messages"][0]["content"])


class TestGetAssignmentDeadline(unittest.TestCase):
    @patch("handler.table")
    def test_returns_deadlines(self, mock_table):
        mock_table.get_item.return_value = {"Item": SAMPLE_COURSE}
        event = make_lex_event("GetAssignmentDeadline", {"CourseId": make_slot("CS101")})

        result = lambda_handler(event, None)

        self.assertEqual(result["sessionState"]["dialogAction"]["type"], "Close")
        content = result["messages"][0]["content"]
        self.assertIn("Homework 1", content)
        self.assertIn("2026-04-05", content)
        self.assertIn("Midterm Project", content)

    @patch("handler.table")
    def test_no_assignments(self, mock_table):
        course_no_assignments = {**SAMPLE_COURSE, "assignments": []}
        mock_table.get_item.return_value = {"Item": course_no_assignments}
        event = make_lex_event("GetAssignmentDeadline", {"CourseId": make_slot("CS101")})

        result = lambda_handler(event, None)

        self.assertIn("No assignment deadlines", result["messages"][0]["content"])

    @patch("handler.table")
    def test_missing_slot_elicits(self, mock_table):
        event = make_lex_event("GetAssignmentDeadline", {"CourseId": None})

        result = lambda_handler(event, None)

        self.assertEqual(result["sessionState"]["dialogAction"]["type"], "ElicitSlot")


class TestFallbackIntent(unittest.TestCase):
    def test_returns_help_message(self):
        event = make_lex_event("FallbackIntent")

        result = lambda_handler(event, None)

        self.assertEqual(result["sessionState"]["dialogAction"]["type"], "Close")
        content = result["messages"][0]["content"]
        self.assertIn("syllabus", content.lower())
        self.assertIn("schedule", content.lower())

    def test_unknown_intent_falls_back(self):
        event = make_lex_event("SomeUnknownIntent")

        result = lambda_handler(event, None)

        self.assertEqual(result["sessionState"]["dialogAction"]["type"], "Close")
        self.assertIn("didn't understand", result["messages"][0]["content"])


if __name__ == "__main__":
    unittest.main()
