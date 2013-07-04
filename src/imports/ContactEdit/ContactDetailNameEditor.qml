/*
 * Copyright (C) 2012-2013 Canonical, Ltd.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; version 3.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

import QtQuick 2.0
import Ubuntu.Components 0.1
import QtContacts 5.0 as QtContacts

import "../Common"

ContactDetailItem {
    id: root

    detail: root.contact ? root.contact.name : null
    fields: [ QtContacts.Name.FirstName, QtContacts.Name.MiddleName, QtContacts.Name.LastName ]

    fieldDelegate: TextInputDetail {
        detail: root.detail
        width: root.width
        height: units.gu(4)
    }
}
