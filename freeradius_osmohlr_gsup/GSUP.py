from osmopy.osmo_ipa import IPA


class GSUP(IPA):
    def add_header(self, data):
        """
        Add GSUP header
        """
        return super(GSUP, self).add_header(data, IPA.PROTO['OSMO'], IPA.EXT['GSUP'])

    def rem_header(self, data):
        """
        Remove GSUP header, check for appropriate protocol and extension
        """
        (_, proto, ext, d) = super(GSUP, self).del_header(data)
        if self.PROTO['OSMO'] != proto or self.EXT['GSUP'] != ext:
            return None
        return d
