# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
#
# Copyright (C) 2013, 2014, 2015 Canonical Ltd.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""address-book-app autopilot tests."""

import os
import time
import subprocess
import re

from autopilot.testcase import AutopilotTestCase
from autopilot.matchers import Eventually
from autopilot.platform import model
from testtools.matchers import Equals

import ubuntuuitoolkit
from ubuntuuitoolkit import emulators as toolkit_emulators


class AddressBookAppTestCase(AutopilotTestCase):
    """A common test case class that provides several useful methods for
    address-book-app tests.
    """
    DEFAULT_DEV_LOCATION = "../../src/app/address-book-app"
    DEB_LOCALTION = "/usr/bin/address-book-app"
    VCARD_PATH_BIN = "/usr/share/address-book-app/vcards/vcard.vcf"
    VCARD_PATH_DEV = os.path.abspath("../data/vcard.vcf")
    ARGS = []
    PRELOAD_VCARD = False
    MEMORY_BACKEND = True

    def setUp(self):
        self.pointing_device = toolkit_emulators.get_pointing_device()
        super(AddressBookAppTestCase, self).setUp()

        # stop vkb
        if model() != "Desktop":
            maliit_info = subprocess.Popen(['/sbin/initctl', 'status', 'maliit-server'], stdout=subprocess.PIPE)
            result = maliit_info.stdout.read()
            if b'start/running,' in result.split():
                subprocess.check_call(['/sbin/initctl', 'stop', 'maliit-server'])

        if 'AUTOPILOT_APP' in os.environ:
            self.app_bin = os.environ['AUTOPILOT_APP']
        else:
            self.app_bin = AddressBookAppTestCase.DEFAULT_DEV_LOCATION

        if AddressBookAppTestCase.MEMORY_BACKEND:
            os.environ['QTCONTACTS_MANAGER_OVERRIDE'] = 'memory'
        else:
            os.environ['QTCONTACTS_MANAGER_OVERRIDE'] = 'galera'
        os.environ['ADDRESS_BOOK_APP_ICON_THEME'] = 'ubuntu-mobile'
        vcard_data = ""
        if self.PRELOAD_VCARD:
            # Use vcard from source tree and fallback on installed vcard (from
            #  address-book-app-autopilot package)
            if os.path.exists(AddressBookAppTestCase.VCARD_PATH_DEV):
                vcard_data = AddressBookAppTestCase.VCARD_PATH_DEV
            else:
                vcard_data = AddressBookAppTestCase.VCARD_PATH_BIN

        os.environ["ADDRESS_BOOK_TEST_DATA"] = vcard_data
        os.environ["LANG"] = "en_US.UTF-8"
        os.environ["LANGUAGE"] = "en_US"
        if vcard_data != "":
            print("Using vcard %s" % vcard_data)
        if os.path.exists(self.app_bin):
            print("Running from: %s" % (self.app_bin))
            self.app = self.launch_test_local()
        elif os.path.exists(self.DEB_LOCALTION):
            print("Running from: %s" % (self.DEB_LOCALTION))
            self.app = self.launch_test_installed()
        else:
            print("Running from click package: address-book-app")
            self.app = self.launch_click_installed()

        AddressBookAppTestCase.ARGS = []
        self.main_window.visible.wait_for(True)

    def tearDown(self):
        super(AddressBookAppTestCase, self).tearDown()

        # start the vkb
        if model() != "Desktop":
            subprocess.check_call(["/sbin/initctl", "start", "maliit-server"])

    def launch_test_local(self):
        return self.launch_test_application(
            self.app_bin,
            *AddressBookAppTestCase.ARGS,
            app_type='qt',
            emulator_base=ubuntuuitoolkit.UbuntuUIToolkitCustomProxyObjectBase)

    def launch_test_installed(self):
        df = "/usr/share/applications/address-book-app.desktop"
        self.ARGS.append("--desktop_file_hint=" + df)
        return self.launch_test_application(
            "address-book-app",
            *AddressBookAppTestCase.ARGS,
            app_type='qt',
            emulator_base=ubuntuuitoolkit.UbuntuUIToolkitCustomProxyObjectBase)

    def launch_click_installed(self):
        return self.launch_click_package(
            'com.ubuntu.address-book',
            emulator_base=ubuntuuitoolkit.UbuntuUIToolkitCustomProxyObjectBase)

    @property
    def main_window(self):
        return self.app.main_window

    def select_a_value(self, field, value_selector, value):
        # Make sure the field has focus
        self.pointing_device.click_object(field)
        self.assertThat(field.activeFocus, Eventually(Equals(True)))

        while(value_selector.currentIndex != value):
            self.keyboard.press_and_release("Shift+Right")
            time.sleep(0.1)

    def type_on_field(self, field, text):
        edit_page = self.main_window.get_contact_edit_page()
        flickable = edit_page.wait_select_single(
            "QQuickFlickable",
            objectName="scrollArea")

        while (not field.activeFocus):
            # wait flicking stops to move to the next field
            self.assertThat(flickable.flicking, Eventually(Equals(False)))

            # use tab to move to the next field
            self.keyboard.press_and_release("Tab")
            time.sleep(0.1)

        self.assertThat(field.activeFocus, Eventually(Equals(True)))

        self.keyboard.type(text)
        self.assertThat(field.text, Eventually(Equals(text)))

    def clear_text_on_field(self, field):
        # Make sure the field has focus
        self.pointing_device.click_object(field)
        self.assertThat(field.activeFocus, Eventually(Equals(True)))

        # click on clear button
        clear_button = field.select_single(objectName='clear_button')
        self.pointing_device.click_object(clear_button)
        self.assertThat(field.text, Eventually(Equals("")))

    # FIXME: Remove this function use ContactEditor.add_field
    def create_new_detail(self, detailGroup):
        detCount = detailGroup.detailsCount
        add_button = detailGroup.select_single("Icon",
                                               objectName="newDetailButton")
        self.pointing_device.click_object(add_button)
        self.assertThat(detailGroup.detailsCount,
                        Eventually(Equals(detCount + 1)))

    def edit_contact(self, index):
        list_page = self.main_window.get_contact_list_page()
        list_page.open_contact(index)

        view_page = self.main_window.get_contact_view_page()
        self.assertThat(view_page.visible, Eventually(Equals(True)))

        # Edit contact
        self.main_window.edit()
        edit_page = self.main_window.get_contact_edit_page()
        self.assertThat(edit_page.visible, Eventually(Equals(True)))

        return edit_page

    def set_phone_number(self, idx, phone_number, phone_type=-1):
        phoneGroup = self.main_window.select_single(
            "ContactDetailGroupWithTypeEditor",
            objectName="phones")

        if idx > 0:
            self.create_new_detail(phoneGroup)

        phone_number_input = self.main_window.select_single(
            "TextInputDetail",
            objectName="phoneNumber_" + str(idx))
        self.type_on_field(phone_number_input, phone_number)

        if phone_type != -1:
            phone_value_selector = self.main_window.select_single(
                "ValueSelector",
                objectName="type_phoneNumber_" + str(idx))
            self.pointing_device.click_object(phone_value_selector)
            self.select_a_value(phone_number_input,
                                phone_value_selector,
                                phone_type)

    def set_email_address(self, idx, email_address, email_type=-1):
        emailGroup = self.main_window.select_single(
            "ContactDetailGroupWithTypeEditor",
            objectName="emails")

        if idx > 0:
            self.create_new_detail(emailGroup)

        email_address_input = self.main_window.select_single(
            "TextInputDetail",
            objectName="emailAddress_" + str(idx))
        self.type_on_field(email_address_input, email_address)

        if email_type != -1:
            email_value_selector = self.main_window.select_single(
                "ValueSelector",
                objectName="type_email_" + str(idx))
            self.pointing_device.click_object(email_value_selector)
            self.select_a_value(email_address_input,
                                email_value_selector,
                                email_type)

    def add_contact(self,
                    first_name,
                    last_name,
                    phone_numbers=None,
                    email_address=None,
                    im_address=None,
                    street_address=None,
                    locality_address=None,
                    region_address=None,
                    postcode_address=None,
                    country_address=None):
        # execute add new contact
        self.main_window.go_to_add_contact()

        first_name_field = self.main_window.select_single(
            "TextInputDetail",
            objectName="firstName")
        last_name_field = self.main_window.select_single(
            "TextInputDetail",
            objectName="lastName")
        self.type_on_field(first_name_field, first_name)
        self.type_on_field(last_name_field, last_name)

        if phone_numbers:
            self.main_window.select_single(
                "ContactDetailGroupWithTypeEditor",
                objectName="phones")
            for idx, number in enumerate(phone_numbers):
                self.set_phone_number(idx, number)

        if email_address:
            self.main_window.select_single(
                "ContactDetailGroupWithTypeEditor",
                objectName="emails")
            for idx, address in enumerate(email_address):
                self.set_email_address(idx, address)

        if im_address:
            imGroup = self.main_window.select_single(
                "ContactDetailGroupWithTypeEditor",
                objectName="ims")
            for idx, address in enumerate(im_address):
                if idx > 0:
                    self.create_new_detail(imGroup)

                im_address_input = self.main_window.select_single(
                    "TextInputDetail",
                    objectName="imUri_" + str(idx))
                self.type_on_field(im_address_input, address)

        if street_address:
            street_0 = self.main_window.selepostcode_addressct_single(
                "TextInputDetail",
                objectName="streetAddress_0")
            self.type_on_field(street_0, street_address)

        if locality_address:
            locality_0 = self.main_window.select_single(
                "TextInputDetail",
                objectName="localityAddress_0")
            self.type_on_field(locality_0, locality_address)

        if region_address:
            region_0 = self.main_window.select_single(
                "TextInputDetail",
                objectName="regionAddress_0")
            self.type_on_field(region_0, region_address)

        if postcode_address:
            postcode_0 = self.main_window.select_single(
                "TextInputDetail",
                objectName="postcodeAddress_0")
            self.type_on_field(postcode_0, postcode_address)

        if country_address:
            country_0 = self.main_window.select_single(
                "TextInputDetail",
                objectName="countryAddress_0")
            self.type_on_field(country_0, country_address)

        self.main_window.save()
