#!/usr/bin/env python
# -*- coding: utf-8 -*-

import spade
import time
from time import sleep
import threading

# #####################################
# #####################################
# organizator
# #####################################
# #####################################

class OrganizatorAgent(spade.Agent.Agent):
    class Ponasanje(spade.Behaviour.Behaviour):
        def onStart(self):
            self.counter = 0
            self.vrijeme = 0

        def _process(self):
            time.sleep(5)

            # print "\n Agent "+ self.getName() + " is online"

            # self.end()

        def unesiVrijeme(self):
            self.vrijeme = input("Vrijeme:")

    class SendMessage(spade.Behaviour.OneShotBehaviour):
        def _process(self):


            vrijeme = self.odrediVrijemeSastanka()
            self.posaljiPorukuAgentima(vrijeme)

            threading.Semaphore().release();

        def odrediVrijemeSastanka(self):
            vrijeme = raw_input("Unesi vrijeme sastanka:")
            return vrijeme


        # saljemo povratnu poruku svakom agentu o vremenu koje zelimo za sastanak
        def posaljiPorukuAgentima(self,vrijeme):
            print "Slanje vremena agentima klijentima ..."

            i = 1
            while (i < 5):
                i += 1
                klijent = "agent_klijent%i@127.0.0.1" % (i)
                adresa = "xmpp://" + klijent

                primatelj = spade.AID.aid(name=klijent,
                                          addresses=[adresa])

                # Second, build the message
                self.msg = spade.ACLMessage.ACLMessage()  # Instantiate the message
                self.msg.setPerformative("inform")  # Set the "inform" FIPA performative
                self.msg.setOntology("termin_sastanka")  # Set the ontology of the message content
                self.msg.setLanguage("Hrvatski")  # Set the language of the message content
                self.msg.addReceiver(primatelj)  # Add the message receiver
                self.msg.setContent(vrijeme)  # Set the message content
                self.myAgent.send(self.msg)

                print "\nposlao sam poruku agentu klijentu " + klijent + " !"

                time.sleep(2)
            if vrijeme=="stop":
                self.MyAgent._kill
                print "Agent organizator se gasi..."


    # ##Primanje poruke
    class PovratnePoruke(spade.Behaviour.Behaviour):
        def _process(self):
            self.msg = None
            self.msg = self._receive(True,10)
            if self.msg:
                print "\nJa sam Agent Organizator " + self.name + "Primio sam poruku povratnu poruku %s!" % self.msg.content

                if self.msg.content == "ok":
                    print "postignuli smo dogovor"
                else:
                    print "nema dogovora"


            else:
                print "Čekao sam ali nema poruke"


    def _setup(self):
        # definiramo moguća ponašanja agenta organizatora

        time.sleep(5)
        p = self.Ponasanje()
        posalji_poruku = self.SendMessage()
        print "\n Agent\t" + self.getName() + " is online"



        #šaljemo poruke o terminu agentima
        self.addBehaviour(posalji_poruku, None);
        self.addBehaviour(p, None)


        ##test--> radi
        #povratne = self.PovratnePoruke()
        #self.setDefaultBehaviour( povratne )



        #time.sleep(20)
        ###Prihvaćanje poruke sa predloškom - ontologija
        feedback_template = spade.Behaviour.ACLTemplate()
        feedback_template.setOntology("povratna_informacija")
        mt = spade.Behaviour.MessageTemplate(feedback_template)
        povratne = self.PovratnePoruke()
        self.addBehaviour(povratne, mt)
        #threading.Semaphore(5)


# #####################################
# #####################################
# Agent klijent
# #####################################
# #####################################
class KlijentAgent(spade.Agent.Agent):
    '''class Ponasanje(spade.Behaviour.Behaviour):
        def onStart(self):
            self.counter = 0

        def _process(self):

            # print "Brojač " + self.name + ":", self.counter
            self.counter = self.counter + 1

            #if (self.counter > 1):
            #    self.end();
            #self.end()'''

    # ##Primanje poruke

    class PrimiTerminSastanka(spade.Behaviour.Behaviour):
        def _process(self):
            self.msg = None
            self.msg = self._receive(True)
            if self.msg:
                print "Ja sam agent klijent " + self.name + "Primio sam poruku %s!" % self.msg.content


                #terminating agents after done job
                if self.msg.content=="stop":
                    print "Agent "+ self.getName() + " se gasi."
                    self.MyAgent._kill()

                else:
                    rezultat = self.evaluirajPrijedlog()
                    self.posaljiOdgovor(rezultat)


            else:
                print "Čekao sam ali nema poruke"

        def evaluirajPrijedlog(self):
            print "evaluiram..."
            return "ok"

        def posaljiOdgovor(self,rezultat):

            # First, form the receiver AID
            primatelj = spade.AID.aid(name="agent_organizator@127.0.0.1",
                                      addresses=["xmpp://agent_organizator@127.0.0.1"])

            # Second, build the message -> this šljaka
            self.msg = spade.ACLMessage.ACLMessage()  # Instantiate the message
            self.msg.setPerformative("inform")  # Set the "inform" FIPA performative
            self.msg.setOntology("povratna_informacija")  # Set the ontology of the message content
            self.msg.setLanguage("Hrvatski")  # Set the language of the message content
            self.msg.addReceiver(primatelj)  # Add the message receiver
            self.msg.setContent(rezultat)  # Set the message content

            #print self.msg
            self.myAgent.send(self.msg)

            print "\nposlao sam poruku agentu organizatoru!"


    ### Definiranje mogućih ponašanja agenta
    def _setup(self):


        print "\n Agent\t" + self.getName() + " is online"


        #p = self.Ponasanje()
        #self.addBehaviour(p, None)
        time.sleep(15)
        ###Prihvaćanje poruke sa predloškom - ontologija

        feedback_template = spade.Behaviour.ACLTemplate()
        feedback_template.setOntology("termin_sastanka")
        mt = spade.Behaviour.MessageTemplate(feedback_template)
        termin = self.PrimiTerminSastanka()
        self.addBehaviour(termin, mt)


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

# ########################################
if __name__ == '__main__':
    print "Program počinje..."

    emafor = threading.Semaphore(value=5)

    for i in range(1, 6):
        # inicijalizacija dretve agenta organizatora
        if (i == 1):
            try:
                thread1 = threading.Thread(target=inicijalizirajAgentaOrganizatora(i), args=(i)).start()
            except:
                print "\nGreška prilikom inicijalizacije agenta organizatora !"

        # inicijalizacija agenata klijenata
        else:
            try:
                thread2 = threading.Thread(target=inicijalizirajAgentaKlijenta(i), args=(i)).start()
            except:
                print "\nGreška prilikom inicijalizacije agenta klijenta %i!" % (i)



