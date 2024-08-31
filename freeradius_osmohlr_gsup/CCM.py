from twisted.internet import reactor
from osmopy.osmo_ipa import IPA
from freeradius_osmohlr_gsup.IPACommon import IPACommon


class CCM(IPACommon):
    """
    Implementation of CCM protocol for IPA multiplex
    """

    def ack(self):
        self.transport.write(IPA().id_ack())

    def ping(self):
        self.transport.write(IPA().ping())

    def pong(self):
        self.transport.write(IPA().pong())

    def handle_CCM(self, data, proto, msgt):
        """
        CCM (IPA Connection Management)
        Only basic logic necessary for tests is implemented (ping-pong, id ack etc)
        """
        if msgt == IPA.MSGT['ID_GET']:
            self.transport.getHandle().sendall(IPA().id_resp(self.factory.ccm_id))
            # if we call
            # self.transport.write(IPA().id_resp(self.factory.test_id))
            # instead, then we would have to also call
            # reactor.callLater(1, self.ack)
            # instead of self.ack()
            # otherwise the writes will be glued together - hence the necessity for ugly hack with 1s timeout
            # Note: this still might work depending on the IPA implementation details on the other side
            self.ack()
            # schedule PING in 4s
            reactor.callLater(4, self.ping)
        if msgt == IPA.MSGT['PING']:
            self.pong()
