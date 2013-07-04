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
import QtContacts 5.0

ContactDetailItem {
    id: root

    detail: root.contact ? root.contact.name : null

    view: ContactDetailViewText {
        function isNotEmptyString(string) {
            return (string && string.length !== 0);
        }

        function formatNameToDisplay() {
            if (!root.contact) {
                return ""
            }

            if (root.contact.displayLabel && root.contact.displayLabel.label && root.contact.displayLabel.label !== "") {
                return root.contact.displayLabel.label
            } else if (detail) {
               return [detail.prefix, detail.firstName, detail.middleName, detail.lastName, detail.suffix].filter(isNotEmptyString).join(" ")
            } else {
                return ""
            }
        }

        height: units.gu(10)
        label {
            fontSize: "large"
            elide: Text.ElideRight
            color: Qt.rgba(0.4, 0.4, 0.4, 1.0)
            style: Text.Raised
            styleColor: "white"
            text: formatNameToDisplay()
        }
    }

    editor: ContactDetailEditorText {
        fields: [   Name.FirstName,
                    Name.MiddleName,
                    Name.LastName
                ]
        height: implicitHeight
    }
}
