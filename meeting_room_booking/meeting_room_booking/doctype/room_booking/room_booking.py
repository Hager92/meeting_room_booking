import frappe
from frappe.model.document import Document


class RoomBooking(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        booking_date: DF.Date
        end_time: DF.Time
        meeting_title: DF.Data
        purpose: DF.SmallText | None
        requested_by: DF.Link
        room: DF.Link
        start_time: DF.Time
        status: DF.Literal["Draft", "Pending Approval", "Approved", "Rejected", "Completed", "Cancelled"]
    # end: auto-generated types

    def validate(self):

        if self.start_time >= self.end_time:
            frappe.throw("End Time must be greater than Start Time")

        self.validate_booking_conflict()

    def validate_booking_conflict(self):

        conflict = frappe.db.sql("""
            SELECT name
            FROM `tabRoom Booking`
            WHERE room=%s
            AND booking_date=%s
            AND status IN ('Approved','Pending Approval','Completed')
            AND name != %s
            AND (
                start_time < %s
                AND end_time > %s
            )
        """,
        (
            self.room,
            self.booking_date,
            self.name,
            self.end_time,
            self.start_time
        ))

        if conflict:
            frappe.throw(
                "This room is already booked during the selected time."
            )