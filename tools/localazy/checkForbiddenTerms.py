#!/usr/bin/env python3

# Copyright 2024 New Vector Ltd.
#
# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-Element-Commercial
# Please see LICENSE files in the repository root for full details.

import sys
from xml.dom import minidom

file = sys.argv[1]

# Dict of forbidden terms, with exceptions for some String name
# Keys are the terms, values are the exceptions.
# If the app is rebranded to Munawar, then "Element" and "Element X" become
# forbidden terms, except where "Element Call" is used or other specific legacy reasons.
forbiddenTerms = {
    "Element": [
        # Exceptions are places where "Element" MUST still appear.
        # "Element Call" related strings:
        "screen_advanced_settings_element_call_base_url",
        "screen_advanced_settings_element_call_base_url_description",
        "screen_incoming_call_subtitle_android",
        "call_invalid_audio_device_bluetooth_devices_disabled",
        # Other strings like "screen_onboarding_welcome_title" or "screen_server_confirmation_message_login_element_dot_io"
        # are expected to be changed via Localazy to use "Munawar". If they still contain "Element",
        # this script should flag them, as "Element" is forbidden and they are no longer exceptions.
    ],
    "Element X": [
        # Exceptions are places where "Element X" MUST still appear.
        # Assumes all UI instances of "Element X" are changed to "Munawar X" (via ApplicationConfig or Localazy).
        # If "screen_room_timeline_legacy_call" is updated by Localazy to "... Munawar X app",
        # it won't be flagged. If it still says "... Element X app", this will flag it.
    ]
}

content = minidom.parse(file)

errors = []

### Strings
for elem in content.getElementsByTagName('string'):
    name = elem.attributes['name'].value
    # Continue if value is empty
    child = elem.firstChild
    if child is None:
        # Should not happen
        continue
    value = child.nodeValue
    # If value contains a forbidden term, add the error to errors
    for (term, exceptions) in forbiddenTerms.items():
        if term in value and name not in exceptions:
            errors.append('Forbidden term "' + term + '" in string: "' + name + '": ' + value)

### Plurals
for elem in content.getElementsByTagName('plurals'):
    name = elem.attributes['name'].value
    for it in elem.childNodes:
        if it.nodeType != it.ELEMENT_NODE:
            continue
        # Continue if value is empty
        child = it.firstChild
        if child is None:
            # Should not happen
            continue
        value = child.nodeValue
        # If value contains a forbidden term, add the error to errors
        for (term, exceptions) in forbiddenTerms.items():
            if term in value and name not in exceptions:
                errors.append('Forbidden term "' + term + '" in plural: "' + name + '": ' + value)

# If errors is not empty print the report
if errors:
    print('Error(s) in file ' + file + ":", file=sys.stderr)
    for error in errors:
        print(" - " + error, file=sys.stderr)
    sys.exit(1)
