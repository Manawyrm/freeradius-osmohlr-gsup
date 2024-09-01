import logging
from twisted.internet.protocol import ReconnectingClientFactory
from freeradius_osmohlr_gsup.IPACommon import IPACommon
from freeradius_osmohlr_gsup.osmo_ipa import IPA

"""
/*
 * Copyright (C) 2016 sysmocom s.f.m.c. GmbH
 *
 * All Rights Reserved
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 */"""


class IPAFactory(ReconnectingClientFactory):
    protocol = IPACommon
    log = None
    ccm_id = IPA().identity(unit=b'1515/0/1', mac=b'00:00:00:00:00:00:00:00', utype=b'FreeRADIUS GSUP', name=b'Unknown',
                            location=b'Milky Way', sw=b"Unknown", serial=b"Unknown")
    client = None

    def __init__(self, proto=None, log=None, ccm_id=None):
        if proto:
            self.protocol = proto
        if ccm_id:
            self.ccm_id = ccm_id
        if log:
            self.log = log
        else:
            self.log = logging.getLogger('IPAFactory')
            self.log.setLevel(logging.CRITICAL)
            self.log.addHandler(logging.NullHandler)

    def clientConnectionFailed(self, connector, reason):
        """
        Only necessary for as debugging aid - if we can somehow set parent's class noisy attribute then we can omit this method
        """
        self.log.warning('IPAFactory connection failed: %s' % reason.getErrorMessage())
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
        client = None

    def clientConnectionLost(self, connector, reason):
        """
        Only necessary for as debugging aid - if we can somehow set parent's class noisy attribute then we can omit this method
        """
        self.log.warning('IPAFactory connection lost: %s' % reason.getErrorMessage())
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
        client = None
