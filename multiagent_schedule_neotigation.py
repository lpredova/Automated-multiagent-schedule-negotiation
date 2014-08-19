#!/usr/bin/env python
# -*- coding: utf-8 -*-

import spade
import time
import threading
from os import system
from GoogleCalendarApi import GoogleCalendar
from spade.Agent import Agent
from spade.Behaviour import Behaviour,OneShotBehaviour, EventBehaviour, ACLTemplate, MessageTemplate
from spade.ACLMessage import ACLMessage

class OrganizatorAgent(Agent):
    '''
    Dretva agenta organizatora
    '''

    class Pregovaranje(Behaviour):
        '''
        Klasa za primanje poruke od agenata klijenata
        '''

        izbornik_odabir = "0"
        brojac_odgovora = 0
        odgovori = []

        def _process(self):
            self.prikaziIzbornik()

            self.msg = None
            self.msg = self._receive(True)
            if self.msg:
                self.brojac_odgovora += 1
                self.odgovori.append(self.msg.content)

                print self.odgovori
                if (self.brojac_odgovora % 4 == 0):
                    for x in self.odgovori:
                        self.brojac_odgovora -= 1
                        if self.brojac_odgovora == 0:
                            if (self.upisiTerminUKalendar()):
                                print "Termin sastanka upisan u kalendar donji"
                                #ToDo ovdje ovo pametnije rijesiti nekako
                                self.izbornik_odabir ="0"
                                self.prikaziIzbornik()

                            else:
                                print "Nije upisano donji"
                                self.izbornik_odabir ="0"
                                self.prikaziIzbornik()

                        if x != "ok":
                            self.brojac_odgovora = 0
                            del self.odgovori[:]

                            print "\nNema dogovora , nova runda pregovora slijedi!!!"
                            self.izbornik_odabir ="0"
                            self.prikaziIzbornik()

            else:
                print "Čekao sam ali nema poruke"

        def prikaziIzbornik(self):
            while self.izbornik_odabir=="0":
                self.izbornik_odabir = raw_input(
                    "\nAgent organizator odabir " + self.izbornik_odabir + "\n1)Predlozi sastanak\n2)Odustani od pregovaranja\n\nOdaberi:")

                if self.izbornik_odabir == "1":
                    self.brojac_odgovora = 0
                    self.odgovori = []
                    vrijeme = self.odrediVrijemeSastanka()
                    self.posaljiPorukuAgentima(vrijeme)

                if self.izbornik_odabir == "2":
                    print "Agent organizator se gasi..."
                    self.posaljiPorukuAgentima("stop")
                    self.MyAgent._kill

                if(self.izbornik_odabir!="1" or self.izbornik_odabir!="2"):self.izbornik_odabir=="0"


        def odrediVrijemeSastanka(self):
            '''
            Određujemo početno vrijeme i formatiramo ga prema Googleovom API-i
            primjer google-ovog formata
            2008-03-07T17:06:02.000Z so that's YYYY-MM-DDTHH:MM:SS.MMMZ

            :return: vrijeme sastanka - polje s 2 elementa, početnim i završnim vremenom
            '''
            # Pocetno vrijeme
            print "Unesi pocetno vrijeme dogadjaja..."
            godina_pocetak = raw_input("pocetna godina (yyyy)   : ")
            mjesec_pocetak = raw_input("pocetni mjesec (mm)     :")
            dan_pocetak = raw_input("pocetni dan (dd)  :")
            sat_pocetak = raw_input("pocetni sat (hh)   : ")
            minute_pocetak = raw_input("pocetne minute (mm)     : ")

            #Zavrsno vrijeme
            print "\nUnesi zavrsno vrijeme dogadjaja...\n"
            godina_kraj = raw_input("zavrsna godina (yyyy)      : ")
            mjesec_kraj = raw_input("zavrsni mjesec (mm)        :")
            dan_kraj = raw_input("zavrsni dan (dd)      : ")
            sat_kraj = raw_input("zavrsni sat (hh)      : ")
            minute_kraj = raw_input("zavrsne minute (mm)        : ")

            pocetno_vrijeme = godina_pocetak + "-" + mjesec_pocetak + "-" + dan_pocetak + "T" + sat_pocetak + ":" + minute_pocetak + ":00.000Z"
            zavrsno_vrijeme = godina_kraj + "-" + mjesec_kraj + "-" + dan_kraj + "T" + sat_kraj + ":" + minute_kraj + ":00.000Z"
            vremena_sastanka = [pocetno_vrijeme, zavrsno_vrijeme]

            return vremena_sastanka

        def posaljiPorukuAgentima(self, vrijeme):
            '''
            saljemo povratnu poruku svakom agentu o vremenima za koje
            zelimo organizirati sastanak
            :param vrijeme:
            :return:
            '''
            print "Slanje vremena agentima klijentima ..."

            i = 1
            while (i < 5):
                i += 1
                klijent = "agent_klijent%i@127.0.0.1" % (i)
                adresa = "xmpp://" + klijent
                primatelj = spade.AID.aid(name=klijent,
                                          addresses=[adresa])

                self.msg = ACLMessage()
                self.msg.setPerformative("inform")
                self.msg.setOntology("termin_sastanka")
                self.msg.setLanguage("Hrvatski")
                self.msg.addReceiver(primatelj)
                self.msg.setContent(vrijeme)
                self.myAgent.send(self.msg)

                print "\nposlao sam poruku agentu klijentu " + klijent + " !"

                #ToDo  ovo u produkciji maknit da UX bude bolji
                #time.sleep(2)



        def upisiTerminUKalendar(self):
            '''
            Metoda koja poziva Google kalendar metodu za upis termina u imenik
            :return:
            '''

            print "Sastanak uspješno dogovoren...\nUnosim u kalendar..."
            calendar = GoogleCalendar()
            if (calendar.upisiTerminUKalendar()):
                return True
            else:
                return False



    def _setup(self):
        '''
        Definiramo skup mogućih ponašanja agenta
        Zaustavljamo izvođenje dretve na 5 sekundi kako bi se ostali agenti mogi pokrenuti
        :return:
        '''
        time.sleep(5)

        print "\n Agent\t" + self.getName() + " je aktivan"

        povratna_informacija = ACLTemplate()
        povratna_informacija.setOntology("povratna_informacija")
        predlozak = spade.Behaviour.MessageTemplate(povratna_informacija)
        pregovaranje = self.Pregovaranje()

        self.addBehaviour(pregovaranje, predlozak)
        pregovaranje.prikaziIzbornik()


class KlijentAgent(Agent):
    '''
    Agent klijent
    '''

    google_client_id = ""
    google_client_secret = ""
    google_client_username = ""

    class PrimiTerminSastanka(Behaviour):

        google_client_id = ""
        google_client_secret = ""
        google_client_username = ""

        def setGoogleAccountPodatke(self, id, secret, user):
            self.google_client_id = id
            self.google_client_secret = secret
            self.google_client_username = user

        def _process(self):
            self.msg = None
            self.msg = self._receive(True)
            if self.msg:
                print "Ja sam agent klijent " + self.name + "Primio sam poruku %s!" % self.msg.content

                if self.msg.content == "stop":
                    print "Agent " + self.getName() + " se gasi."
                    self.MyAgent._kill()

                else:
                    print "Kontaktiram Google Calendar ! "
                    vremena = self.msg.content.split("'")

                    pocetno_vrijeme = vremena[1]
                    zavrsno_vrijeme = vremena[3]

                    rezultat = self.evaluirajPrijedlog(pocetno_vrijeme, zavrsno_vrijeme)
                    self.posaljiOdgovor(rezultat)
            else:
                print "Čekao sam ali nema poruke"


        # Metoda koja poziva klasu GoogleCalendar u kojoj kontaktiramo Google-Calendar-API
        def evaluirajPrijedlog(self, pocetno_vrijeme, zavrsno_vrijeme):
            print "Evaluiram prijedlog..."
            calendar = GoogleCalendar(self.google_client_id, self.google_client_secret, self.google_client_username)
            if (calendar.main(pocetno_vrijeme, zavrsno_vrijeme)):
                return "ok"

            else:
                print "raspored zauzet"
                return "fail"


        def posaljiOdgovor(self, rezultat):

            primatelj = spade.AID.aid(name="agent_organizator@127.0.0.1",
                                      addresses=["xmpp://agent_organizator@127.0.0.1"])

            self.msg = ACLMessage()
            self.msg.setPerformative("inform")
            self.msg.setOntology("povratna_informacija")
            self.msg.setLanguage("Hrvatski")
            self.msg.addReceiver(primatelj)
            self.msg.setContent(rezultat)
            self.myAgent.send(self.msg)

            print "\nposlao sam poruku agentu organizatoru %s!" % (rezultat)


    def _setup(self):

        print "\n Agent\t" + self.getName() + " je aktivan"


        # Prihvaćanje poruke sa predloškom - ontologija
        feedback_template = ACLTemplate()
        feedback_template.setOntology("termin_sastanka")
        mt = MessageTemplate(feedback_template)
        termin = self.PrimiTerminSastanka()
        self.addBehaviour(termin, mt)
        termin.setGoogleAccountPodatke(self.google_client_id, self.google_client_secret, self.google_client_username)


    def setGoogleAccountPodatke(self, id, secret, user):
        self.google_client_id = id
        self.google_client_secret = secret
        self.google_client_username = user


def inicijalizirajAgentaOrganizatora(i):
    '''
    Metoda za inicijalizaciju agenta organizatora
    :param i:
    :return: Agent organizator
    '''
    ip = "agent_organizator@127.0.0.%i" % (i)
    korisnik = "organizator"

    o = OrganizatorAgent(ip, korisnik)
    o.start()


def inicijalizirajAgentaKlijenta(i):
    '''
    Metoda za inicijalizaciju agenata klijenata
    i korisnicki podaci agenata klijenata za uslugu Google Calendar
    :param i:
    :return: Agenti klijenti
    '''

    google_korisnici = {
    "2": ["466301455600-rull43ikdhd7d691dtcitufhnlab9nfu.apps.googleusercontent.com", "g7S6psNxN9tw7PmpILxIsxzw",
          "agent0.zavrsni@gmail.com"],
    "3": ["969348362348-nfs15alf9velcc7dr5312cebijs66cp4.apps.googleusercontent.com", "8Zt_4PsA_JpGGnmFO1PDETj3",
          "agent01.zavrsni@gmail.com"],
    "4": ["111267856009-qj1ravtgqptrlpb9nl83at347vhkgkpd.apps.googleusercontent.com", "8Zt_4PsA_JpGGnmFO1PDETj3",
          "agent02.zavrsni@gmail.com"],
    "5": ["485027726364-fgf7ng6oa671uti4lhv0ugsccilgln97.apps.googleusercontent.com", "d4UqsL3DF0sPZy2fxspKuvr_",
          "agent03.zavrsni@gmail.com"]}

    id = google_korisnici["%i" % (i)][0]
    secret = google_korisnici["%i" % (i)][1]
    user = google_korisnici["%i" % (i)][2]

    ip = "agent_klijent%i@127.0.0.1" % (i)
    korisnik = "klijent_0%i" % (i)
    k = KlijentAgent(ip, korisnik)
    k.start()
    k.setGoogleAccountPodatke(id, secret, user)

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