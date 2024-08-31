#!/usr/bin/env python3
# -*- mode: python-mode; py-indent-tabs-mode: nil -*-

from queue import Queue
from osmocom.gsup.message import *

from freeradius_osmohlr_gsup.CCM import CCM
from freeradius_osmohlr_gsup.GSUP import GSUP


class GSUPClient(CCM):
    def connectionMade(self):
        super().connectionMade()
        self.dbg('GSUP connectionMade()')
        self.factory.client = self
        self.open_requests = {}

    def send_auth_request(self, imsi):
        authInfoRequest = GsupMessage.from_dict({
            'msg_type': 'SEND_AUTH_INFO_REQUEST',
            'ies': [
                {'imsi': imsi}
            ]
        })
        self.transport.write(GSUP().add_header(authInfoRequest.to_bytes()))

        q = Queue()
        if imsi in self.open_requests:
            self.open_requests[imsi] += q
        else:
            self.open_requests[imsi] = [q]

        return q

    def osmo_GSUP(self, data):
        message = GsupMessage.from_bytes(data)
        message_d = message.to_dict()
        imsi = None

        for ie in message_d["ies"]:
            if "imsi" in ie:
                imsi = ie['imsi']

        if type(self.open_requests[imsi]) is list:
            for q in self.open_requests[imsi]:
                q.put(message_d)

            del self.open_requests[imsi]
