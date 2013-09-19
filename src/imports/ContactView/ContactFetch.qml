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

Item {
    id: root

    property alias model: connections.target
    property bool running: false
    property QtObject contact: null
    property bool contactIsDirty: false

    signal contactFetched(QtObject contact)
    signal contactRemoved()

    function fetchContact(contactId) {
        if (contact && !contactIsDirty) {
            contactFetched(contact)
        } else {
            running = true
            connections.currentQueryId = model.fetchContacts([contactId])
            if (connections.currentQueryId === -1) {
                running = false
            }
        }
    }

    Connections {
        target: root.model

        onContactsChanged: {
            if (root.contact) {
                root.contactIsDirty = true

                for (var i=0; i < root.model.contacts.length; i++) {
                    if (root.model.contacts[i].contactId == root.contact.contactId) {
                        return
                    }
                }
                contactRemoved()
            }
        }
    }

    Connections {
        id: connections

        property int currentQueryId: -1

        onContactsFetched: {
            if (requestId == currentQueryId) {
                root.contactIsDirty = false
                root.running = false
                currentQueryId = -1
                root.contactFetched(fetchedContacts[0])
                root.contact = fetchedContacts[0]
            }
        }
    }
}
