/*
 * Copyright (C) 2012-2015 Canonical, Ltd.
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

import QtQuick 2.4
import Ubuntu.Components 1.3
import Ubuntu.Components.Popups 1.3 as Popups

MainView {
    id: mainWindow
    objectName: "addressBookAppMainWindow"

    property string modelErrorMessage: ""
    readonly property bool appActive: Qt.application.active

    signal applicationReady()

    function contact(contactId)
    {
        mainStack.resetStack()
        if (mainStack.contactListPage) {
            mainStack.contactListPage.showContactWithId(contactId)
        } else {
            console.error("Contact preview requested but ContactListPage not loaded")
        }
    }

    function create(phoneNumber)
    {
        mainStack.resetStack()
        if (mainStack.contactListPage) {
            mainStack.contactListPage.createContactWithPhoneNumber(phoneNumber)
        } else {
            console.error("Contact creation requested but ContactListPage not loaded")
        }
    }

    function pick(single)
    {
        console.debug("Pick mode:" + single)
        pickWithTransfer(single === "true", null)
    }

    function pickWithTransfer(single, activeTransfer)
    {
        mainStack.resetStack()
        if (mainStack.contactListPage) {
            mainStack.contactListPage.startPickMode(single, activeTransfer)
        } else {
            console.error("Pick mode requested but ContactListPage not loaded")
        }
    }

    function importvcard(_url)
    {
        importvcards([_url])
    }

    function importvcards(_urls)
    {
        mainStack.resetStack()
        if (mainStack.contactListPage) {
            mainStack.contactListPage.importContact(_urls)
        } else {
            console.error("Import vcard requested but ContactListPage not loaded")
        }
    }

    width: units.gu(90)
    height: units.gu(71)
    anchorToKeyboard: false

    AdaptivePageLayout {
        id: mainStack

        property var contactListPage: null
        property var bottomEdge: null

        function resetStack()
        {
            mainStack.removePages(primaryPage);
        }

        function _nextItemInFocusChain(item, foward)
        {
            var next = item.nextItemInFocusChain(foward)
            var first = next
            //WORKAROUND: SDK does not allow us to disable focus for items due bug: #1514822
            //because of that we need this
            while (!next || !next.hasOwnProperty("_allowFocus")) {
                next = next.nextItemInFocusChain(foward)

                // avoid loop
                if (next === first) {
                    next = null
                    break
                }
            }
            if (next) {
                next.forceActiveFocus()
            }
            return next
        }

        primaryPage: contactPage
        onContactListPageChanged: {
            if (contentHubLoader.status === Loader.Ready) {
                contentHubLoader.item.pageStack = mainStack
            } else {
                contentHubLoader.setSource(Qt.resolvedUrl("ContentHubProxy.qml"), {"pageStack": mainStack})
            }
        }

        anchors.fill: parent
        layouts: [
            PageColumnsLayout {
                when: mainStack.width >= units.gu(80)
                PageColumn {
                    maximumWidth: units.gu(50)
                    minimumWidth: units.gu(40)
                    preferredWidth: units.gu(40)
                }
                PageColumn {
                    fillWidth: true
                }
            },
            PageColumnsLayout {
                when: true
                PageColumn {
                    fillWidth: true
                }
            }
        ]

        onColumnsChanged: {
            if (mainStack.columns > 1)
                mainStack.addPageToNextColumn(primaryPage, Qt.resolvedUrl("./ABMultiColumnEmptyState.qml"))
        }

        Component.onCompleted: {
            if (mainStack.columns > 1)
                mainStack.addPageToNextColumn(primaryPage, Qt.resolvedUrl("./ABMultiColumnEmptyState.qml"))
        }
    }

    ABContactListPage {
        id: contactPage
        pageStack: mainStack
    }

    Component.onCompleted: {
        application.elapsed()
        i18n.domain = "address-book-app"
        i18n.bindtextdomain("address-book-app", i18nDirectory)
        mainWindow.applicationReady()
    }

    // WORKAROUND: Due the missing feature on SDK, they can not detect if
    // there is a mouse attached to device or not. And this will cause the
    // bootom edge component to not work correct on desktop.
    // We will consider that  a mouse is always attached until it get implement on SDK.
    Binding {
        target:  QuickUtils
        property: "mouseAttached"
        value: application.usingMouse
    }

    Component {
        id: errorDialog

        Popups.Dialog {
            id: dialogue

            title: i18n.tr("Error")
            text: mainWindow.modelErrorMessage

            Button {
                text: i18n.tr("Cancel")
                gradient: UbuntuColors.greyGradient
                onClicked: PopupUtils.close(dialogue)
            }
        }
    }

    Connections {
        target: UriHandler
        onOpened: {
            for (var i = 0; i < uris.length; ++i) {
                application.parseUrl(uris[i])
            }
        }
    }

    Loader {
        id: contentHubLoader

        //We can not use async load, the export requested signal can be received before the component get ready
        //asynchronous: true
        source: Qt.resolvedUrl("ContentHubProxy.qml")
        onStatusChanged: {
            if (status === Loader.Ready) {
                item.pageStack = mainStack
            }
        }
    }

    // If application was called from uri handler and lost the focus reset the app to normal state
    onAppActiveChanged: {
        if (appActive) {
            mainStack.forceActiveFocus()
        }

        if (!appActive && mainStack.contactListPage) {
            mainStack.contactListPage.returnToNormalState()
        }
    }
}
