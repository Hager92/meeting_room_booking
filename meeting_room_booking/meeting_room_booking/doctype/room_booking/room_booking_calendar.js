frappe.views.calendar["Room Booking"] = {
    field_map: {
        start: "booking_date",
        end: "booking_date",
        id: "name",
        title: "meeting_title",
        allDay: 1
    },

    filters: [
        {
            fieldtype: "Select",
            fieldname: "status",
            label: "Status",
            options: "\nApproved",
            default: "Approved"
        }
    ]
};