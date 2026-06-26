# Copyright (c) 2026, Hager and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MeetingRoom(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		capacity: DF.Int
		facilities: DF.SmallText | None
		location: DF.Data | None
		room_name: DF.Data
		status: DF.Literal["Available", "Not Available", "Under Maintenance"]
	# end: auto-generated types

	pass
