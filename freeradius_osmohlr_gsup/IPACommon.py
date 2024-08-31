from twisted.protocols import basic
from osmopy.osmo_ipa import IPA

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


class IPACommon(basic.Int16StringReceiver):
    """
    Generic IPA protocol handler: include some routines for simpler subprotocols.
    It's not intended as full implementation of all subprotocols, rather common ground and example code.
    """

    def dbg(self, line):
        """
        Debug print helper
        """
        self.factory.log.debug(line)

    def osmo_CTRL(self, data):
        """
        OSMO CTRL protocol
        Placeholder, see corresponding derived class
        """
        pass

    def osmo_GSUP(self, data):
        """
        OSMO GSUP extension
        Placeholder, see corresponding derived class
        """
        pass

    def osmo_UNKNOWN(self, data):
        """
        OSMO defaul extension handler
        """
        self.dbg('OSMO unknown extension received %s' % data)

    def handle_CCM(self, data, proto, msgt):
        """
        CCM (IPA Connection Management)
        Placeholder, see corresponding derived class
        """
        pass

    def handle_OSMO(self, data, proto, extension):
        """
        Dispatcher point for OSMO subprotocols based on extension name, lambda default should never happen
        """
        method = getattr(self, 'osmo_' + IPA().ext(extension), lambda: "extension dispatch failure")
        method(data)

    def handle_UNKNOWN(self, data, proto, extension):
        """
        Default protocol handler
        """
        self.dbg('IPA received message for %s (%s) protocol with attribute %s' % (IPA().proto(proto), proto, extension))

    def process_chunk(self, data):
        """
        Generic message dispatcher for IPA (sub)protocols based on protocol name, lambda default should never happen
        """
        (_, proto, extension, content) = IPA().del_header(data)
        if content is not None:
            method = getattr(self, 'handle_' + IPA().proto(proto), lambda: "protocol dispatch failure")
            method(content, proto, extension)

    def dataReceived(self, data):
        """
        Override for dataReceived from Int16StringReceiver because of inherently incompatible interpretation of length
        If default handler is used than we would always get off-by-1 error (Int16StringReceiver use equivalent of l + 2)
        """
        if len(data):
            (head, tail) = IPA().split_combined(data)
            self.process_chunk(head)
            self.dataReceived(tail)

    def connectionMade(self):
        """
        We have to resetDelay() here to drop internal state to default values to make reconnection logic work
        Make sure to call this via super() if overriding to keep reconnection logic intact
        """
        addr = self.transport.getPeer()
        self.dbg('IPA connected to %s:%d peer' % (addr.host, addr.port))
        self.factory.resetDelay()
