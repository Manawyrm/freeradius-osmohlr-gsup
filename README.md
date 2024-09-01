# FreeRADIUS EAP-SIM OsmoHLR/GSUP client

This package can be used to authenticate a wired (802.1x) or wireless (WPA-Enterprise) network against a SIM card using EAP-SIM.  
The required authentication data will be provided by [OsmoHLR](https://osmocom.org/projects/osmo-hlr/wiki/OsmoHLR) via the [Generic Subscriber Update Protocol (GSUP)](https://osmocom.org/projects/cellular-infrastructure/wiki/GSUP).

## Project status
Works™, tested against OsmoHLR with MILENAGE

![Wireshark screenshot, showing RADIUS and GSUP traffic](https://screenshot.tbspace.de/wxktilfhmeg.png)

## Configuration
Install module first.

In `sites-enabled/default` add `gsup` like:
```
	gsup

	eap {
		ok = return
	}
```

Create `mods-enabled/gsup` with:
```
python3 gsup {
	module = freeradius_osmohlr_gsup.freeradius_gsup

	mod_instantiate = ${.module}
	func_instantiate = instantiate

	mod_authorize = ${.module}
	func_authorize = authorize

	config {
		gsup_hostname = "localhost"
		gsup_port = 4222
		gsup_timeout = 5
	}
}
```
(configure GSUP parameters accordingly)

## Notes / Known issues
- EAP-AKA/AKA'? Provisions for AKA are present, not tested yet.
- Credential caching loops over all cached credentials (60s timeout), possible memory/performance bottleneck

## Thanks to
- LaF0rge for implementing the GSUP de/encoder in the osmocom python package
- Darell Tan / [geekman/simtriplets](https://github.com/geekman/simtriplets) for inspiration about FreeRADIUS python module handling
- bonzi for nerd-sniping me into this adventure