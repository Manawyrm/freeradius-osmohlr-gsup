#!/usr/bin/env python3
import radiusd

from freeradius_osmohlr_gsup.IPAFactory import IPAFactory
from freeradius_osmohlr_gsup.GSUPClient import GSUPClient

from queue import Queue
from threading import Thread
from twisted.internet import reactor, threads
import argparse, logging, sys
from pprint import pprint as pp

factory = None


def instantiate(p):
    gsup_hostname = radiusd.config["gsup_hostname"]
    gsup_port = int(radiusd.config["gsup_port"])

    log = logging.getLogger('IPAGSUPAdapter')
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler(sys.stdout))

    global factory
    factory = IPAFactory(GSUPClient, log)
    reactor.connectTCP(gsup_hostname, gsup_port, factory)
    queue = Queue()

    # Start Twisted in a background thread, with False to disable signal handler installation
    Thread(target=reactor.run, args=(False,)).start()

    return 0
    # return 0 for success or -1 for failure


def authorize(p):
    global factory

    username = None
    for k, v in p:
        if k == 'User-Name':
            username = v
            if username[0] == '"' and username[-1] == '"':
                username = username[1:-1]

            username = username.split('@')[0]

            # identity: 1=SIM, 0=AKA, 6=AKA_PRIME
            if username[0] == '1':
                username = username[1:]

    if username is None:
        return radiusd.RLM_MODULE_NOTFOUND

    radiusd.radlog(radiusd.L_DBG, 'IMSI %s' % username)

    if factory.client is not None:
        queue = threads.blockingCallFromThread(reactor, factory.client.send_auth_request, username)
        response = queue.get(True, int(radiusd.config["gsup_timeout"]))

        if response["msg_type"] == "SEND_AUTH_INFO_RESULT":
            reply = []
            tuple_count = 1

            # `RAND`::   User authentication challenge.

            # EAP-SIM: 
            # `KC`::     Authentication value from the AuC.
            # `SRES`::   Signing response.

            # EAP-AKA/AKA': 
            # `AUTN`::   Authentication value from the AuC.
            # `CK`::     Ciphering Key.
            # `IK`::     Integrity Key.
            # `XRES`::   Signing response.
            # `SQN`::    (optional)
            # `AK`::     (optional)

            for ie in response["ies"]:
                if "auth_tuple" in ie:
                    for auth_param in ie['auth_tuple']:
                        if "rand" in auth_param:
                            reply.append(tuple(["EAP-Sim-RAND" + str(tuple_count), "0x" + auth_param["rand"].hex()]))

                        # EAP-SIM parameters
                        if "sres" in auth_param:
                            reply.append(tuple(["EAP-Sim-SRES" + str(tuple_count), "0x" + auth_param["sres"].hex()]))

                        if "kc" in auth_param:
                            reply.append(tuple(["EAP-Sim-KC" + str(tuple_count), "0x" + auth_param["kc"].hex()]))

                        # EAP-AKA/AKA' parameters
                        if "autn" in auth_param:
                            reply.append(tuple(["EAP-Sim-AUTN" + str(tuple_count), "0x" + auth_param["autn"].hex()]))

                        if "ck" in auth_param:
                            reply.append(tuple(["EAP-Sim-CK" + str(tuple_count), "0x" + auth_param["ck"].hex()]))

                        if "ik" in auth_param:
                            reply.append(tuple(["EAP-Sim-IK" + str(tuple_count), "0x" + auth_param["ik"].hex()]))

                        if "res" in auth_param:
                            reply.append(tuple(["EAP-Sim-XRES" + str(tuple_count), "0x" + auth_param["res"].hex()]))

                    tuple_count += 1
                    if tuple_count > 3:
                        break

            return (radiusd.RLM_MODULE_UPDATED,
                    tuple(reply),  # reply tuple
                    tuple())  # config tuple

        if response["msg_type"] == "SEND_AUTH_INFO_ERROR":
            radiusd.radlog(radiusd.L_ERR, 'Couldn\'t answer IMSI %s, GSUP error:' % username)
            pp(response)
            return radiusd.RLM_MODULE_NOTFOUND

    else:
        radiusd.radlog(radiusd.L_ERR, 'Couldn\'t answer IMSI %s, GSUP client currently not connected!' % username)
        return radiusd.RLM_MODULE_NOTFOUND

    return radiusd.RLM_MODULE_NOTFOUND
