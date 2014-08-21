# coding=utf-8
# coding=utf-8
__author__ = 'lovro'

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import spade
import time
import threading
from GoogleCalendarApi import GoogleCalendar
from spade.Agent import Agent
from spade.Behaviour import Behaviour,ACLTemplate, MessageTemplate
from spade.ACLMessage import ACLMessage

class OrganizatorAgent(Agent):
    '''
    Dretva agenta organizatora
    '''

    class Pregovaranje(Behaviour):
        '''
        Klasa za primanje poruke od agenata klijenata
        '''
        brojac_krugova_pregovora = 0

        pocetno_vrijeme = ""
        zavrsno_vrijeme = ""

        izbornik_odabir = "0"
        brojac_odgovora = 0
        odgovori = []

        def _process(self):
            self.prikaziIzbornik()

            self.msg = None
            self.msg = self._receive(True,10)
            if self.msg:

                print "primio sam poruku"
                self.brojac_odgovora += 1
                self.odgovori.append(self.msg.content)

                print self.odgovori
                if self.brojac_odgovora % 4 == 0:
                    for x in self.odgovori:
                        self.brojac_odgovora -= 1
                        if self.brojac_odgovora == 0:
                            if self.upisiTerminUKalendar():
                                print "Termin sastanka upisan u kalendar donji"
                                #ToDo ovdje ovo pametnije rijesiti nekako

                                calendar = GoogleCalendar()
                                calendar.upisiTerminUKalendar(self.pocetno_vrijeme,self.zavrsno_vrijeme)

                                #self.izbornik_odabir ="0"
                                #self.prikaziIzbornik()

                            else:
                                print "Nije upisano donji"
                                self.izbornik_odabir ="0"
                                self.prikaziIzbornik()

                        if x != "Termin je u redu":
                            self.brojac_odgovora = 0
                            del self.odgovori[:]

                            print "\nNema dogovora , nova runda pregovora slijedi!!!"
                            self.izbornik_odabir ="0"
                            self.prikaziIzbornik()
            else:
                print self.msg
                print "Agent organizator : Čekao sam ali nema poruke"
                self.prikaziIzbornik()

        def prikaziIzbornik(self):

            if self.brojac_krugova_pregovora == 10:
                print "Dogovor nije postignut u 10 krugova pregovora"
                return 0

            while self.izbornik_odabir=="0":
                print "%i. krug pregovora" %(self.brojac_krugova_pregovora+1)
                self.izbornik_odabir = raw_input(
                    "\n1)Predlozi sastanak\n2)Odustani od pregovaranja\n\nOdabir:")

                if self.izbornik_odabir == "1":
                    self.brojac_odgovora = 0
                    self.brojac_krugova_pregovora +=1
                    self.odgovori = []
                    vrijeme = self.odrediVrijemeSastanka()
                    self.posaljiPorukuAgentima(vrijeme)

                if self.izbornik_odabir == "2":
                    print "Agent organizator se gasi..."
                    self.posaljiPorukuAgentima("stop")
                    self.MyAgent._kill

                self.izbornik_odabir=="0"


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

            self.pocetno_vrijeme = godina_pocetak + "-" + mjesec_pocetak + "-" + dan_pocetak + "T" + sat_pocetak + ":" + minute_pocetak + ":00.000Z"
            self.zavrsno_vrijeme = godina_kraj + "-" + mjesec_kraj + "-" + dan_kraj + "T" + sat_kraj + ":" + minute_kraj + ":00.000Z"
            vremena_sastanka = [self.pocetno_vrijeme, self.zavrsno_vrijeme]

            return vremena_sastanka

        def posaljiPorukuAgentima(self, poruka):
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
                self.msg.setContent(poruka)
                self.myAgent.send(self.msg)

                print "\nposlao sam poruku agentu klijentu " + klijent + " !"

                #ToDo  ovo u produkciji maknit da UX bude bolji
                #time.sleep(2)

        def upisiTerminUKalendar(self):
            '''
            Metoda koja poziva Google kalendar metodu za upis termina u imenik
            :return:
            '''

            print "Sastanak uspješno dogovoren..."

            izbor = 0

            while(izbor!=1 or izbor!=2):
                izbor = input("Želite li dogovoreni sastanak upisati u kalendar ?\n1)Dodaj u kalendar\n2)Odustani")
                if izbor == 1:
                    calendar = GoogleCalendar()
                    lokacija = raw_input("\nUnesite lokaciju sastanka:")
                    naziv = raw_input("Naziv sastanka sastanka:")

                    if calendar.upisiTerminUKalendar(self.pocetno_vrijeme,self.pocetno_vrijeme,lokacija,naziv):

                        return True
                    else:
                        print "nece"
                        return False

                if izbor == 2:
                    print "Dodavanje događaja otkazano !"
                    self.prikaziIzbornik()



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

    ne_preferirani_termini = ""

    class PrimiTerminSastanka(Behaviour):

        calendar  =""
        ime_agenta = ""
        pocetno_vrijeme = ""
        zavrsno_vrijeme = ""

        google_client_id = ""
        google_client_secret = ""
        google_client_username = ""

        ne_preferirani_termini = ""

        def setGoogleAccountPodatke(self, id, secret, user, ime , termini):
            self.google_client_id = id
            self.google_client_secret = secret
            self.google_client_username = user
            self.ime_agenta = ime
            self.ne_preferirani_termini =  termini

            self.calendar = GoogleCalendar(self.google_client_id, self.google_client_secret, self.google_client_username)

        def _process(self):
            self.msg = None
            self.msg = self._receive(True)
            if self.msg:
                print "\nAgent " + self.ime_agenta + " : primio sam poruku :  %s " % self.msg.content
                print self.msg.content.split("'")[1]

                if self.msg.content == "stop":
                    print "Agent " + self.ime_agenta + ": gasim se"
                    self.MyAgent._kill()

                #if self.msg.content.split("'")[1] == "potvrda":
                if self.msg.content == "potvrda":
                    print "Agent " + self.ime_agenta + ": Sastanak potvrđen -\tgasim se"
                    self.MyAgent._kill()

                    #lokacija = self.msg.content.split("'")[3]
                    #naziv = self.msg.content.split("'")[5]
                    #self.calendar.upisiTerminUKalendar(self.pocetno_vrijeme,self.zavrsno_vrijeme,lokacija,naziv)

                else:
                    print "\nAgent " + self.ime_agenta +" : kontaktiram Google Calendar ! "
                    vremena = self.msg.content.split("'")

                    self.pocetno_vrijeme = vremena[1]
                    self.zavrsno_vrijeme = vremena[3]

                    rezultat = self.evaluirajPrijedlog(self.pocetno_vrijeme, self.zavrsno_vrijeme)
                    self.posaljiOdgovor(rezultat)
            else:
                print "\nAgent " + self.ime_agenta +" : čekao sam ali nema poruke"


        def evaluirajPrijedlog(self, pocetno_vrijeme, zavrsno_vrijeme):
            '''
            Metoda koja poziva klasu GoogleCalendar u kojoj kontaktiramo Google-Calendar-API
            Provjerava da li je određeni termin slobodan i ukoliko je vraća "Termin je u redu"
            Također nije dovoljno da je sam termin slobodan već se provjerava i korisnikova preferencija određenog
            termina tako da nije dobovoljno samo da je termin slobodan već i da agent želi uzeti taj termin
            Ako termin nije slobodan tada provjerava kada u tom danu postoji
            slobodan vremenski prostor određenog raspona
            '''

            print "\nAgent " + self.ime_agenta +" : evaluiram prijedlog..."

            if (self.calendar.main(pocetno_vrijeme, zavrsno_vrijeme)):
                print self.ne_preferirani_termini

                ne_preferirani_pocetak  = int(self.ne_preferirani_termini[0].split(":")[0])
                ne_preferirani_zavrsetak  = int(self.ne_preferirani_termini[1].split(":")[0])
                pocetni_sat =  int(pocetno_vrijeme.split("T")[1].split(":")[0])
                zavrsni_sat = int(zavrsno_vrijeme.split("T")[1].split(":")[0])

                #ToDo moguće poboljsanje
                if(pocetni_sat < ne_preferirani_pocetak and ne_preferirani_zavrsetak < zavrsni_sat):
                    return "Mogu ali necu"

                else: return "Termin je u redu"

            else:
                print "\nAgent " + self.ime_agenta +" : tražim slobodan vremenski okvir"

                #racunanje potrebnog trajanja slobodnog vremenskog okvira
                pocetni_sat =  int(pocetno_vrijeme.split("T")[1].split(":")[0])
                zavrsni_sat = int(zavrsno_vrijeme.split("T")[1].split(":")[0])
                trajanje = zavrsni_sat-pocetni_sat
                pocetni_sat +=1

                #if trajanje >= 12:
                #        print "\nAgent " + self.ime_agenta +" : Danas je nemoguće pronaći slobodnog vremena"

                #tražimo slobodan vremenski okvir
                #else:
                while zavrsni_sat <= 23:
                        print "Tražim..."
                        zavrsni_sat = pocetni_sat + trajanje

                        if zavrsni_sat == 24 : return "Ne odgovara mi termin"
                        pocetak_godina =  pocetno_vrijeme.split("-")[0]
                        pocetak_mjesec =  pocetno_vrijeme.split("-")[1]
                        pocetak_dan =  pocetno_vrijeme.split("-")[2].split("T")[0]
                        pocetak_minute =  pocetno_vrijeme.split("T")[1].split(":")[1]

                        zavrsetak_godina =  zavrsno_vrijeme.split("-")[0]
                        zavrsetak_mjesec =  zavrsno_vrijeme.split("-")[1]
                        zavrsetak_dan =  zavrsno_vrijeme.split("-")[2].split("T")[0]
                        zavrsetak_minute =  zavrsno_vrijeme.split("T")[1].split(":")[1]

                        if pocetni_sat < 10 :
                            pocetak_sat = "0%i"%(pocetni_sat)
                        else:
                            pocetak_sat = "%i"%(pocetni_sat)

                        if zavrsni_sat < 10 :
                            zavrsetak_sat = "0%i"%(zavrsni_sat)
                        else:
                            zavrsetak_sat = "%i"%(zavrsni_sat)


                        pocetno_vrijeme = pocetak_godina + "-" + pocetak_mjesec + "-" + pocetak_dan + "T" + pocetak_sat + ":" + pocetak_minute + ":00.000Z"
                        zavrsno_vrijeme = zavrsetak_godina + "-" + zavrsetak_mjesec + "-" + str(zavrsetak_dan) + "T" + zavrsetak_sat + ":" + zavrsetak_minute + ":00.000Z"

                        if self.calendar.main(pocetno_vrijeme, zavrsno_vrijeme):
                                return  pocetno_vrijeme

                        else :
                            pocetni_sat +=1

        def posaljiOdgovor(self, odgovor):

            primatelj = spade.AID.aid(name="agent_organizator@127.0.0.1",
                                      addresses=["xmpp://agent_organizator@127.0.0.1"])

            self.msg = ACLMessage()
            self.msg.setPerformative("inform")
            self.msg.setOntology("povratna_informacija")
            self.msg.setLanguage("Hrvatski")
            self.msg.addReceiver(primatelj)
            self.msg.setContent(odgovor)
            self.myAgent.send(self.msg)

            print  "\nAgent " + self.ime_agenta +" : poslao sam poruku agentu organizatoru %s\n!" % (odgovor)


    def _setup(self):

        print "\n Agent\t" + self.getAID().getName() + " je aktivan"

        # Prihvaćanje poruke sa predloškom - ontologija
        feedback_template = ACLTemplate()
        feedback_template.setOntology("termin_sastanka")
        mt = MessageTemplate(feedback_template)
        termin = self.PrimiTerminSastanka()
        self.addBehaviour(termin, mt)
        termin.setGoogleAccountPodatke(self.google_client_id, self.google_client_secret, self.google_client_username,self.getAID().getName(),self.ne_preferirani_termini)


    def setGoogleAccountPodatke(self, id, secret, user , termini):
        self.google_client_id = id
        self.google_client_secret = secret
        self.google_client_username = user
        self.ne_preferirani_termini = termini


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

    #   podaci o svakom posebnom agentu, njegovi google korisnički podaci,pridružena e-mail adresa i vrijeme koje
    #   korisnik ne preferira odnosno iz nekog razloga ne želi da se sastanak održi baš u to vrijeme,
    #   sastoji se od početnog i završnog vremena perioda za koje ne želimo uznemiravati korisnika

    google_korisnici = {
    "2": ["466301455600-rull43ikdhd7d691dtcitufhnlab9nfu.apps.googleusercontent.com", "g7S6psNxN9tw7PmpILxIsxzw",
          "agent0.zavrsni@gmail.com",["12:00","13:00"]],
    "3": ["969348362348-nfs15alf9velcc7dr5312cebijs66cp4.apps.googleusercontent.com", "8Zt_4PsA_JpGGnmFO1PDETj3",
          "agent01.zavrsni@gmail.com",["08:00","08:45"]],
    "4": ["111267856009-qj1ravtgqptrlpb9nl83at347vhkgkpd.apps.googleusercontent.com", "8Zt_4PsA_JpGGnmFO1PDETj3",
          "agent02.zavrsni@gmail.com",["07:30","08:30"]],
    "5": ["485027726364-fgf7ng6oa671uti4lhv0ugsccilgln97.apps.googleusercontent.com", "d4UqsL3DF0sPZy2fxspKuvr_",
          "agent03.zavrsni@gmail.com",["05:00","10:00"]]}

    id = google_korisnici["%i" % (i)][0]
    secret = google_korisnici["%i" % (i)][1]
    user = google_korisnici["%i" % (i)][2]
    termini = google_korisnici["%i" % (i)][3]

    ip = "agent_klijent%i@127.0.0.1" % (i)
    korisnik = "klijent_0%i" % (i)
    k = KlijentAgent(ip, korisnik)
    k.start()
    k.setGoogleAccountPodatke(id, secret, user,termini)

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