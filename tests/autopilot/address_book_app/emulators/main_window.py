# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# Copyright 2013 Canonical
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.

from ubuntuuitoolkit import emulators as uitk


class MainWindow(uitk.MainView):
    """An emulator class that makes it easy to interact with the app."""

    def get_contact_list_page(self):
        # ContactListPage is the only page that can appears multiple times
        # Ex.: During the pick mode we alway push a new contactListPage, to preserve
        # the current application status
        pages = self.select_many("ContactListPage",
                                 objectName="contactListPage")
        
        # alway return the page without pickMode
        for p in pages:
            if not p.pickMode:
                return p
        return None

    def get_contact_edit_page(self):
        return self.wait_select_single("ContactEditor",
                                       objectName="contactEditorPage")

    def get_contact_view_page(self):
        return self.wait_select_single("ContactView",
                                       objectName="contactViewPage")

    def get_contact_list_pick_page(self):
        pages = self.select_many("ContactListPage",
                                 objectName="contactListPage")
        for p in pages:
            if p.pickMode:
                return p
        return None

    def get_contact_list_view(self):
        """
        Returns a ContactListView iobject for the current window
        """
        return self.wait_select_single( "ContactListView",
                                       objectName="contactListView")

    def get_button(self, name):
        """
        Returns a Button object matching 'name'

        Arguments:
            name: Name of the button
        """
        return self.wait_select_single( "Button", objectName=name)

    def cancel(self):
        """
        Press the 'Cancel' button
        """
        self.pointing_device.click_object(self.get_button("reject"))

    def save(self):
        """
        Press the 'Save' button
        """
        self.pointing_device.click_object(self.get_button("accept"))


