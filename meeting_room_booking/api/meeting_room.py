import frappe
from frappe import _
from typing import Optional

@frappe.whitelist()
def get_available_rooms(booking_date: str, start_time: str, end_time: str):

    # Validate booking time
    if start_time >= end_time:
        frappe.throw(_("End Time must be greater than Start Time"))

    # Get all available meeting rooms
    rooms = frappe.get_all(
        "Meeting Room",
        filters={"status": "Available"},
        fields=["name", "capacity", "location", "facilities", "status"]
    )

    available_rooms = []

    for room in rooms:
        # Check for overlapping bookings
        conflict = frappe.db.sql(
            """
            SELECT name
            FROM `tabRoom Booking`
            WHERE room = %s
            AND booking_date = %s
            AND status IN ('Pending Approval', 'Approved', 'Completed')
            AND start_time < %s
            AND end_time > %s
            LIMIT 1
            """,
            (room.name, booking_date, end_time, start_time),
            as_dict=True
        )

        if not conflict:
            available_rooms.append(room)

    return {
        "success": True,
        "rooms": available_rooms
    }


@frappe.whitelist()
def create_room_booking(
    meeting_title: str,
    room: str,
    requested_by: str,
    booking_date: str,
    start_time: str,
    end_time: str,
    purpose: Optional[str] = None
):

    # Validate booking time
    if start_time >= end_time:
        frappe.throw(_("Start Time must be before End Time"))

    if not frappe.db.exists("Meeting Room", room):
        frappe.throw(_("Meeting Room does not exist"))

    room_doc = frappe.get_doc("Meeting Room", room)

    if room_doc.status != "Available":
        frappe.throw(_("Room is not available"))

    # Prevent double booking
    conflict = frappe.db.sql(
        """
        SELECT name
        FROM `tabRoom Booking`
        WHERE room = %s
        AND booking_date = %s
        AND status IN ('Pending Approval', 'Approved', 'Completed')
        AND start_time < %s
        AND end_time > %s
        LIMIT 1
        """,
        (room, booking_date, end_time, start_time),
        as_dict=True
    )

    if conflict:
        frappe.throw(_("Room is already booked during this time"))

    # Create the booking
    booking = frappe.get_doc({
        "doctype": "Room Booking",
        "meeting_title": meeting_title,
        "room": room,
        "requested_by": requested_by or frappe.session.user,
        "booking_date": booking_date,
        "start_time": start_time,
        "end_time": end_time,
        "purpose": purpose
    })

    booking.insert(ignore_permissions=True)

    return {
        "success": True,
        "message": _("Booking created successfully"),
        "booking_id": booking.name
    }

@frappe.whitelist()
def get_booking_details(booking_id: str):

    # Check if the booking exists
    if not frappe.db.exists("Room Booking", booking_id):
        frappe.throw(_("Booking not found"))

    booking = frappe.get_doc("Room Booking", booking_id)

    return {
        "success": True,
        "booking": {
            "meeting_title": booking.meeting_title,
            "room": booking.room,
            "requested_by": booking.requested_by,
            "booking_date": booking.booking_date,
            "start_time": booking.start_time,
            "end_time": booking.end_time,
            "purpose": booking.purpose,
            "status": booking.status
        }
    }


@frappe.whitelist()
def get_my_bookings(
    employee: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    status: Optional[str] = None
):

    # Build filters based on the request
    filters = {"requested_by": employee}

    if status:
        filters["status"] = status

    if from_date and to_date:
        filters["booking_date"] = ["between", [from_date, to_date]]
    elif from_date:
        filters["booking_date"] = [">=", from_date]
    elif to_date:
        filters["booking_date"] = ["<=", to_date]

    bookings = frappe.get_all(
        "Room Booking",
        filters=filters,
        fields=[
            "name",
            "meeting_title",
            "room",
            "booking_date",
            "start_time",
            "end_time",
            "status"
        ],
        order_by="booking_date desc"
    )

    return {
        "success": True,
        "bookings": bookings
    }


@frappe.whitelist()
def cancel_booking(booking_id: str, cancellation_reason: Optional[str] = None):

    # Check if the booking exists
    if not frappe.db.exists("Room Booking", booking_id):
        frappe.throw(_("Booking not found"))

    booking = frappe.get_doc("Room Booking", booking_id)

    # Get current user's Employee ID
    employee = frappe.db.get_value(
        "Employee",
        {"user_id": frappe.session.user},
        "name"
    )

    # Allow Admin OR Administrator OR the employee who created booking
    if (
        frappe.session.user not in ["Administrator", "Admin"]
        and booking.requested_by != employee
    ):
        frappe.throw(_("Not allowed to cancel this booking"))

    if booking.status == "Completed":
        frappe.throw(_("Completed bookings cannot be cancelled"))

    if booking.status == "Cancelled":
        frappe.throw(_("Booking is already cancelled"))

    booking.status = "Cancelled"
    
    booking.save(ignore_permissions=True)

    return {
        "success": True,
        "message": _("Booking cancelled successfully")
    }