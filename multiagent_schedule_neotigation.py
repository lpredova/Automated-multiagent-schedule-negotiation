#!/usr/bin/env python
# -*- coding: utf-8 -*-

import spade
import time
from time import sleep
import threading


# organizator
class OrganizatorAgent(spade.Agent.Agent):
    class Ponasanje(spade.Behaviour.Behaviour):
        def onStart(self):
            self.counter = 0
            self.vrijeme = 0

        def _process(self):
            time.sleep(5)

            # print "\n Agent "+ self.getName() + " is online"

            #self.end()

        def unesiVrijeme(self):
            self.vrijeme = input("Vrijeme:")

    class SendMessage(spade.Behaviour.OneShotBehaviour):
        def _process(self):
            # First, form the receiver AID
            primatelj = spade.AID.aid(name="agent_klijent2@127.0.0.1",
                                     addresses=["xmpp://agent_klijent2@127.0.0.1"])

            # Second, build the message
            self.msg = spade.ACLMessage.ACLMessage()  # Instantiate the message
            self.msg.setPerformative("inform")  # Set the "inform" FIPA performative
            self.msg.setOntology("test")  # Set the ontology of the message content
            self.msg.setLanguage("Hrvatski")  # Set the language of the message content
            self.msg.addReceiver(primatelj)  # Add the message receiver
            self.msg.setContent("Hello World")  # Set the message content
            self.myAgent.send(self.msg)

            print "poslao sam poruku !"


    def _setup(self):
        p = self.Ponasanje()
        m = self.SendMessage()
        print "\n Agent\t" + self.getName() + " is online"

        self.addBehaviour(p, None)

        time.sleep(7)
        self.addBehaviour(m, None);


# Agent klijent
class KlijentAgent(spade.Agent.Agent):
    class Ponasanje(spade.Behaviour.Behaviour):
        def onStart(self):
            self.counter = 0

        def _process(self):
            time.sleep(10)
            # print "Brojač " + self.name + ":", self.counter
            #self.counter = self.counter + 1

            #if (self.counter > 1):
            #    self.end();
            #self.end()

    ###Primanje poruke

    class SvePoruke( spade.Behaviour.Behaviour ):
            def _process( self ):
                self.msg = None
                self.msg = self._receive( True, 10 )
                if self.msg:
                    print "Ja sam " + self.name + "Primio sam poruku %s!"%self.msg.content
                else:
                    print "Čekao sam ali nema poruke"




    def _setup(self):
        p = self.Ponasanje()
        prihvati_poruku = self.SvePoruke()

        print "\n Agent\t" + self.getName() + " is online"
        self.addBehaviour(p, None)

        time.sleep(15)
        self.setDefaultBehaviour(prihvati_poruku)


# ########################################

# metode za inicijalizaciju agenata
def inicijalizirajAgentaOrganizatora(i):
    ip = "agent_organizator@127.0.0.%i" % (i)
    korisnik = "organizator"

    o = OrganizatorAgent(ip, korisnik)
    o.start()


def inicijalizirajAgentaKlijenta(i):
    ip = "agent_klijent%i@127.0.0.1" % (i)
    korisnik = "klijent_0%i" % (i)
    k = KlijentAgent(ip, korisnik)
    k.start()


if __name__ == '__main__':
    print "Program počinje..."

    for i in range(1, 6):
        # inicijalizacija dretve agenta organizatora
        if (i == 1):
            try:
                threading.Thread(target=inicijalizirajAgentaOrganizatora(i), args=(i)).start()
            except:
                print "\nGreška prilikom inicijalizacije agenta organizatora !"

        # inicijalizacija agenata klijenata
        else:
            try:
                threading.Thread(target=inicijalizirajAgentaKlijenta(i), args=(i)).start()
            except:
                print "\nGreška prilikom inicijalizacije agenta klijenta %i!" % (i)



