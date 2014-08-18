#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import spade
import time
import json
from time import sleep
import threading
from GoogleCalendarApi import GoogleCalendar

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

        def unesiVrijeme(self):
            self.vrijeme = input("Vrijeme:")

    class SendMessage(spade.Behaviour.OneShotBehaviour):

        #Metoda kojom primamo formatirano vrijeme koje je korisnik unio te ga šaljemo agentima
        #Sadrzi mali izbornik u kojem mozemo odabrati zelimo li unijeti vrijeme sastanka ili prekinuti pregovore
        def _process(self):
            odaberi = "3"
            while(odaberi != "1" and odaberi !="2"):
                odaberi = raw_input("########\nAgent organizator\n1)Predlozi sastanak\n2)Odustani od pregovaranja\n\nOdaberi:")

                if(odaberi == "1"):
                    vrijeme = self.odrediVrijemeSastanka()
                    self.posaljiPorukuAgentima(vrijeme)

                if(odaberi == "2"):
                    print "Agent organizator se gasi..."
                    self.posaljiPorukuAgentima("stop")
                    self.MyAgent._kill

            threading.Semaphore().release();



        #Određujemo početno vrijeme i formatiramo ga prema Googleovom API-i
        #primjer google-ovog formata
        #2008-03-07T17:06:02.000Z so that's YYYY-MM-DDTHH:MM:SS.MMMZ
        def odrediVrijemeSastanka(self):

            #Pocetno vrijeme
            print "\nUnesi pocetno vrijeme dogadjaja...\n"
            godina_pocetak = raw_input("pocetna godina (yyyy)   : ")
            mjesec_pocetak = raw_input("pocetni mjesec (mm)     :")
            dan_pocetak = raw_input("pocetni dan (dd)  :")
            sat_pocetak = raw_input("pocetni sat (hh)   : ")
            minute_pocetak = raw_input("pocetne minute (mm)     : ")

            pocetno_vrijeme = godina_pocetak + "-" + mjesec_pocetak + "-" + dan_pocetak + "T"+sat_pocetak +":"+ minute_pocetak + ":00.000Z"

            #Zavrsno vrijeme
            print "\nUnesi zavrsno vrijeme dogadjaja...\n"
            godina_kraj = raw_input("zavrsna godina (yyyy)      : ")
            mjesec_kraj = raw_input("zavrsni mjesec (mm)        :")
            dan_kraj = raw_input("zavrsni dan (dd)      : ")
            sat_kraj = raw_input("zavrsni sat (hh)      : ")
            minute_kraj = raw_input("zavrsne minute (mm)        : ")

            zavrsno_vrijeme = godina_kraj + "-" + mjesec_kraj + "-" + dan_kraj + "T"+sat_kraj +":"+ minute_kraj + ":00.000Z"

            vremena_sastanka =[pocetno_vrijeme,zavrsno_vrijeme]

            return vremena_sastanka


        # saljemo povratnu poruku svakom agentu o vremenima za koje
        # zelimo organizirati sastanak
        def posaljiPorukuAgentima(self,vrijeme):
            print "Slanje vremena agentima klijentima ..."

            i = 1
            while (i < 5):
                i += 1
                klijent = "agent_klijent%i@127.0.0.1" % (i)
                adresa = "xmpp://" + klijent

                primatelj = spade.AID.aid(name=klijent,
                                          addresses=[adresa])

                self.msg = spade.ACLMessage.ACLMessage()  # Instantiate the message
                self.msg.setPerformative("inform")  # Set the "inform" FIPA performative
                self.msg.setOntology("termin_sastanka")  # Set the ontology of the message content
                self.msg.setLanguage("Hrvatski")  # Set the language of the message content
                self.msg.addReceiver(primatelj)  # Add the message receiver
                self.msg.setContent(vrijeme)  # Set the message content
                self.myAgent.send(self.msg)

                print "\nposlao sam poruku agentu klijentu " + klijent + " !"

                time.sleep(2)


    # Primanje poruke uspješnosti pregovaranja od agenata klijenata
    class PovratnePoruke(spade.Behaviour.Behaviour):

        brojac_odgovora = 0
        odgovori=[]

        def _process(self):
            self.msg = None
            self.msg = self._receive(True,10)
            if self.msg:
                        self.brojac_odgovora +=1
                        print self.brojac_odgovora

                        self.odgovori.append(self.msg.content)

                        print self.odgovori

                        if(self.brojac_odgovora%4==0):
                            print "primio sam sve"
                            for x in self.odgovori:

                                self.brojac_odgovora-=1

                                if x!= "ok":
                                    print "\nNema dogovora"

                                    #ToDo -> nova runda, poziv metode izbornika rjesiti
                                    #resetiramo lokalne varijable klase agenta organizatora
                                    self.brojac_odgovora = 0
                                    del self.odgovori[:]

                                    print "pobrisao sam varijable"


                                    #OrganizatorAgent.SendMessage._process()
                                if self.brojac_odgovora==0:
                                    print "imamo deal"
                                    #ToDo -> Srediti upisivanje u kalendar
                                    #resetiramo lokalne varijable klase agenta organizatora

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

        ###Prihvaćanje poruke sa predloškom - ontologija
        feedback_template = spade.Behaviour.ACLTemplate()
        feedback_template.setOntology("povratna_informacija")
        mt = spade.Behaviour.MessageTemplate(feedback_template)
        povratne = self.PovratnePoruke()
        self.addBehaviour(povratne, mt)
        #threading.Semaphore(5)


# #####################################
# Agent klijent
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

    # Metoda za primanje poruke od agenta organizatora te instanciramo klasu za
    # kontaktiranje google calendar usluge te vraćamo agentu organizatoru odgovor
    class PrimiTerminSastanka(spade.Behaviour.Behaviour):
        def _process(self):
            self.msg = None
            self.msg = self._receive(True)
            if self.msg:
                print "Ja sam agent klijent " + self.name + "Primio sam poruku %s!" % self.msg.content

                # Gasimo agenta
                if self.msg.content=="stop":
                    print "Agent "+ self.getName() + " se gasi."
                    self.MyAgent._kill()

                # Šaljemo početna i završna vremena google-u
                else:
                    print "Kontaktiram Google Calendar ! "
                    vremena =  self.msg.content.split("'")

                    pocetno_vrijeme = vremena[1]
                    zavrsno_vrijeme = vremena[3]

                    rezultat = self.evaluirajPrijedlog(pocetno_vrijeme,zavrsno_vrijeme)
                    self.posaljiOdgovor(rezultat)
            else:
                print "Čekao sam ali nema poruke"


        # Metoda koja poziva klasu GoogleCalendar u kojoj kontaktiramo Google-Calendar-API
        def evaluirajPrijedlog(self,pocetno_vrijeme,zavrsno_vrijeme):
            print "Evaluiram prijedlog..."
            calendar = GoogleCalendar("466301455600-rull43ikdhd7d691dtcitufhnlab9nfu.apps.googleusercontent.com","g7S6psNxN9tw7PmpILxIsxzw",'agent0.zavrsni@gmail.com')

            if(calendar.main(pocetno_vrijeme,zavrsno_vrijeme)): return "ok"

            else:
                print "raspored zauzet"
                return "fail"


        def posaljiOdgovor(self,rezultat):

            primatelj = spade.AID.aid(name="agent_organizator@127.0.0.1",
                                      addresses=["xmpp://agent_organizator@127.0.0.1"])

            # Second, build the message -> this šljaka
            self.msg = spade.ACLMessage.ACLMessage()  # Instantiate the message
            self.msg.setPerformative("inform")  # Set the "inform" FIPA performative
            self.msg.setOntology("povratna_informacija")  # Set the ontology of the message content
            self.msg.setLanguage("Hrvatski")  # Set the language of the message content
            self.msg.addReceiver(primatelj)  # Add the message receiver
            self.msg.setContent(rezultat)  # Set the message content
            self.myAgent.send(self.msg)

            print "\nposlao sam poruku agentu organizatoru %s!"%(rezultat)


    ### Definiranje mogućih ponašanja agenta
    def _setup(self):


        print "\n Agent\t" + self.getName() + " is online"


        #p = self.Ponasanje()
        #self.addBehaviour(p, None)
        time.sleep(15)

        #Prihvaćanje poruke sa predloškom - ontologija
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
    #Podaci za autentifikaciju agenta na google cloudu
    #agent 0
    #client_id ="466301455600-rull43ikdhd7d691dtcitufhnlab9nfu.apps.googleusercontent.com"
    #client_secret = "g7S6psNxN9tw7PmpILxIsxzw"

    #agent 1
    #client_id ="969348362348-nfs15alf9velcc7dr5312cebijs66cp4.apps.googleusercontent.com"
    #client_secret = "8Zt_4PsA_JpGGnmFO1PDETj3"

    #agent 2
    #client_id ="111267856009-qj1ravtgqptrlpb9nl83at347vhkgkpd.apps.googleusercontent.com"
    #client_secret = "iehwQARcxZh0YUuzzxrJQxji"

    #agent 3
    #client_id ="485027726364-fgf7ng6oa671uti4lhv0ugsccilgln97.apps.googleusercontent.com"
    #client_secret = "d4UqsL3DF0sPZy2fxspKuvr_"

    

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