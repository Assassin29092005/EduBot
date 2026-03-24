import json
import os
import logging
import boto3

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# X-Ray tracing (graceful fallback if not available)
try:
    from aws_xray_sdk.core import patch_all
    patch_all()
except ImportError:
    logger.info("aws_xray_sdk not available, skipping X-Ray tracing")

# DynamoDB resource
TABLE_NAME = os.environ.get("TABLE_NAME", "EduBot-Courses")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    """Main Lambda handler invoked by Amazon Lex v2."""
    logger.info("Received event: %s", json.dumps(event))

    intent_name = event["sessionState"]["intent"]["name"]
    slots = event["sessionState"]["intent"].get("slots", {})

    if intent_name == "GetCourseSyllabus":
        return handle_get_course_syllabus(event, slots)
    elif intent_name == "GetProfessorInfo":
        return handle_get_professor_info(event, slots)
    elif intent_name == "GetClassSchedule":
        return handle_get_class_schedule(event, slots)
    elif intent_name == "GetAssignmentDeadline":
        return handle_get_assignment_deadline(event, slots)
    elif intent_name == "FallbackIntent":
        return handle_fallback(event)
    else:
        return handle_fallback(event)


def get_slot_value(slots, slot_name):
    """Safely extract a resolved slot value."""
    slot = slots.get(slot_name)
    if slot and slot.get("value"):
        return slot["value"].get("interpretedValue")
    return None


def get_course(course_id):
    """Fetch a course from DynamoDB by course_id."""
    try:
        response = table.get_item(Key={"course_id": course_id.upper()})
        return response.get("Item")
    except Exception as e:
        logger.error("Error fetching course %s: %s", course_id, str(e))
        return None


def elicit_slot(event, slot_to_elicit, message):
    """Return an ElicitSlot dialog action."""
    return {
        "sessionState": {
            "dialogAction": {
                "type": "ElicitSlot",
                "slotToElicit": slot_to_elicit,
            },
            "intent": event["sessionState"]["intent"],
        },
        "messages": [{"contentType": "PlainText", "content": message}],
    }


def close(event, message):
    """Return a Close dialog action (fulfillment)."""
    return {
        "sessionState": {
            "dialogAction": {"type": "Close"},
            "intent": {
                "name": event["sessionState"]["intent"]["name"],
                "state": "Fulfilled",
            },
        },
        "messages": [{"contentType": "PlainText", "content": message}],
    }


def handle_get_course_syllabus(event, slots):
    """Handle the GetCourseSyllabus intent."""
    course_id = get_slot_value(slots, "CourseId")
    if not course_id:
        return elicit_slot(
            event, "CourseId", "Which course would you like the syllabus for? Please provide the course ID (e.g., CS101)."
        )

    course = get_course(course_id)
    if not course:
        return close(event, f"Sorry, I couldn't find a course with ID {course_id.upper()}. Please check the course ID and try again.")

    syllabus = course.get("syllabus", "No syllabus information available.")
    course_name = course.get("course_name", course_id.upper())
    return close(event, f"Here's the syllabus for {course_name} ({course_id.upper()}):\n\n{syllabus}")


def handle_get_professor_info(event, slots):
    """Handle the GetProfessorInfo intent."""
    course_id = get_slot_value(slots, "CourseId")
    if not course_id:
        return elicit_slot(
            event, "CourseId", "Which course's professor would you like to know about? Please provide the course ID (e.g., CS101)."
        )

    course = get_course(course_id)
    if not course:
        return close(event, f"Sorry, I couldn't find a course with ID {course_id.upper()}. Please check the course ID and try again.")

    professor = course.get("professor", "Unknown")
    office_hours = course.get("office_hours", "Not specified")
    email = course.get("professor_email", "Not available")
    course_name = course.get("course_name", course_id.upper())
    return close(
        event,
        f"Professor info for {course_name} ({course_id.upper()}):\n"
        f"- Professor: {professor}\n"
        f"- Office Hours: {office_hours}\n"
        f"- Email: {email}",
    )


def handle_get_class_schedule(event, slots):
    """Handle the GetClassSchedule intent."""
    course_id = get_slot_value(slots, "CourseId")
    if not course_id:
        return elicit_slot(
            event, "CourseId", "Which course schedule would you like to see? Please provide the course ID (e.g., CS101)."
        )

    course = get_course(course_id)
    if not course:
        return close(event, f"Sorry, I couldn't find a course with ID {course_id.upper()}. Please check the course ID and try again.")

    schedule = course.get("schedule", "No schedule available.")
    location = course.get("location", "TBD")
    course_name = course.get("course_name", course_id.upper())
    return close(
        event,
        f"Schedule for {course_name} ({course_id.upper()}):\n"
        f"- Time: {schedule}\n"
        f"- Location: {location}",
    )


def handle_get_assignment_deadline(event, slots):
    """Handle the GetAssignmentDeadline intent."""
    course_id = get_slot_value(slots, "CourseId")
    if not course_id:
        return elicit_slot(
            event, "CourseId", "Which course's assignment deadlines would you like? Please provide the course ID (e.g., CS101)."
        )

    course = get_course(course_id)
    if not course:
        return close(event, f"Sorry, I couldn't find a course with ID {course_id.upper()}. Please check the course ID and try again.")

    deadlines = course.get("assignments", [])
    course_name = course.get("course_name", course_id.upper())
    if not deadlines:
        return close(event, f"No assignment deadlines found for {course_name} ({course_id.upper()}).")

    deadline_text = "\n".join(
        f"- {a['name']}: Due {a['due_date']}" for a in deadlines
    )
    return close(
        event,
        f"Upcoming assignments for {course_name} ({course_id.upper()}):\n{deadline_text}",
    )


def handle_fallback(event):
    """Handle the FallbackIntent."""
    return close(
        event,
        "I'm sorry, I didn't understand that. I can help you with:\n"
        "- Course syllabus information\n"
        "- Professor details and office hours\n"
        "- Class schedules\n"
        "- Assignment deadlines\n\n"
        "Try asking something like 'What is the syllabus for CS101?' or 'When is the next assignment for MATH201 due?'",
    )
