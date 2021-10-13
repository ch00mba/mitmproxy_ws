#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  4 23:41:42 2021

@author: alexei
"""

#import substrateinterface 
from substrateinterface import SubstrateInterface
from substrateinterface.exceptions import SubstrateRequestException
import json
#import time
#from datetime import datetime


    
# import logging
# logging.basicConfig(level=logging.DEBUG)

try:
    substrate = SubstrateInterface(
        #url="wss://endpointtest.uniquenetwork.io",
        url="wss://testnet2.uniquenetwork.io",
        ss58_format=42,
        type_registry_preset='substrate-node-template',
        type_registry=d
    )
    #events = substrate.query("System", "Events")
    head_chain = substrate.get_chain_head()
    print(head_chain)
    substrate.close()


    
#    while True:
#        head_chain = substrate.get_chain_head()
#        print(head_chain)
#        print(datetime.now())



except ConnectionRefusedError:
    print("error in block retrival")
    exit()
    




