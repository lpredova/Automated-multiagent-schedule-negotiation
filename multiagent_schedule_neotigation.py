# coding=utf-8
__author__ = 'lovro'

#!/usr/bin/env python

import spade
import time
import threading
from GoogleCalendarApi import GoogleCalendar
from spade.Agent import Agent
from spade.Behaviour import Behaviour, ACLTemplate, MessageTemplate
from spade.ACLMessage import ACLMessage


class OrganizatorAgent(Agent):
    class Pregovaranje(Behaviour):

        brojac_krugova_pregovora = 0
        lokacija = ""
        naziv = ""

        pocetno_vrijeme = ""
        zavrsno_vrijeme = ""
        trajanje_dogadjaja = ""

        izbornik_odabir = "0"
        brojac_odgovora = 0
        odgovori = []

        def _process(self):
            self.msg = None
            self.msg = self._receive(True)

            if self.msg:

                print "\nAgent organizator : " + str(self.brojac_odgovora+1) + " /4 poruka primljeno"
                self.brojac_odgovora += 1
                self.odgovori.append(self.msg.content)

                if self.brojac_odgovora % 4 == 0:

                    for x in range(0, 4):
                        print self.odgovori[x]

                    termin = self.nadjiNajboljiTermin()

                    if termin == "":
                        self.brojac_odgovora = 0
                        del self.odgovori[:]
                        print "\nNe može se odrediti najbolji termin sastanka s tim vremenom." \
                              "\nMolimo predložite novi termin !"
                        self.izbornik()

                    else:
                        print "\nNajbolji termin je : " + termin
                        self.upisiTerminUKalendar(termin)

            else:
                print self.msg
                print "\nAgent organizator : Čekao sam ali nema poruke"
                self.prikaziIzbornik()

        def prikaziIzbornik(self):

            if self.brojac_krugova_pregovora == 10:
                print "\nDogovor nije postignut u 10 krugova pregovora"
                self.zaustaviAgenta()
            self.izbornik()

        def izbornik(self):
                print "\n\n%i. krug pregovora" % (self.brojac_krugova_pregovora + 1)
                self.izbornik_odabir = raw_input(
                    "\n1)Predlozi sastanak\n2)Odustani od pregovaranja\n\nOdabir:")

                if self.izbornik_odabir == "1":
                    self.brojac_odgovora = 0
                    self.brojac_krugova_pregovora += 1
                    self.odgovori = []
                    vrijeme = self.odrediVrijemeSastanka()
                    self.posaljiPorukuAgentima(vrijeme)

                if self.izbornik_odabir == "2":
                    self.zaustaviAgenta()

        def zaustaviAgenta(self):
            print "Agent organizator se gasi..."
            self.posaljiPorukuAgentima("stop")
            self.MyAgent._kill

        def odrediVrijemeSastanka(self):

            self.lokacija = raw_input("\nUnesite lokaciju sastanka:")
            self.naziv = raw_input("Naziv sastanka sastanka:")

            print "Unesi pocetno vrijeme intervala..."
            godina_pocetak = raw_input("pocetna godina (yyyy)   : ")
            mjesec_pocetak = raw_input("pocetni mjesec (mm)     :")
            dan_pocetak = raw_input("pocetni dan (dd)  :")
            sat_pocetak = raw_input("pocetni sat (hh)   : ")
            minute_pocetak = raw_input("pocetne minute (mm)     : ")

            print "\nUnesi zavrsno vrijeme intervala...\n"
            godina_kraj = raw_input("zavrsna godina (yyyy)      : ")
            mjesec_kraj = raw_input("zavrsni mjesec (mm)        :")
            dan_kraj = raw_input("zavrsni dan (dd)      : ")
            sat_kraj = raw_input("zavrsni sat (hh)      : ")
            minute_kraj = raw_input("zavrsne minute (mm)        : ")

            self.trajanje_dogadjaja = raw_input("\ntrajanje događaja (min)        : ")
            self.pocetno_vrijeme = godina_pocetak + "-" + mjesec_pocetak + "-" + dan_pocetak + "T" + sat_pocetak + ":" + minute_pocetak + ":00.000Z"
            self.zavrsno_vrijeme = godina_kraj + "-" + mjesec_kraj + "-" + dan_kraj + "T" + sat_kraj + ":" + minute_kraj + ":00.000Z"
            vremena_sastanka = [self.pocetno_vrijeme, self.zavrsno_vrijeme, self.trajanje_dogadjaja]

            return vremena_sastanka

        def posaljiPorukuAgentima(self, poruka):
            i = 1
            while i < 5:
                time.sleep(0.3)
                i += 1
                klijent = "agent_klijent%i@127.0.0.1" %i
                adresa = "xmpp://" + klijent
                primatelj = spade.AID.aid(name=klijent, addresses=[adresa])
                self.msg = ACLMessage()
                self.msg.setPerformative("inform")
                self.msg.setOntology("termin_sastanka")
                self.msg.setLanguage("Hrvatski")
                self.msg.addReceiver(primatelj)
                self.msg.setContent(poruka)
                self.myAgent.send(self.msg)
                print "\nposlao sam poruku agentu klijentu " + klijent + " !"

        def nadjiNajboljiTermin(self):

            rjesenje = False

            for x in range(0, 4):

                element = self.odgovori[x]
                if element == "[]":
                    return ""

                redak = element.translate(None, '[]').split(",")
                for l in range(0, len(redak)):

                    #print "uzeli smo sada : " + redak[l]

                    if "Termin je blokiran" in redak[l]:
                        continue
                    pojava = 0

                    for y in range(0, 4):
                        #print "usporedjujem " + redak[l] + " sa %i"%y + ". tim retkom"
                        el = self.odgovori[y]
                        red = el.translate(None, '[]').split(",")
                        for k in range(0, len(red)):
                            #print "usporedjujem " + redak[l] + " sa " + red[k]

                            if redak[l] == red[k]:
                                pojava += 1
                                #print pojava

                            if pojava == 4:
                                return redak[l]

            if not rjesenje:
                return ""

        def upisiTerminUKalendar(self, termin):

            izbor = 0
            while izbor != 1 or izbor != 2:
                izbor = input("\nŽelite sastanak s terminom %s upisati u kalendar ?"
                              "\n1)Dodaj u kalendar"
                              "\n2)Odustani"
                              "\nodabir:" % termin)
                if izbor == 1:

                    pocetno_vrijeme = termin.split("'")[1]
                    zavrsno_vrijeme = self.izracunajZavrsnoVrijeme(termin);

                    calendar = GoogleCalendar()
                    try:
                        if calendar.upisiTerminUKalendar(pocetno_vrijeme, zavrsno_vrijeme, self.naziv, self.lokacija):
                            print "Događaj je uspješno upisan u kalendar..."
                            self.zaustaviAgenta()
                            self.izbornik()

                    except:
                        print "Dodavanje događaja nije uspjelo !"
                        self.izbornik()

                if izbor == 2:
                    print "Dodavanje događaja otkazano !"
                    self.izbornik_odabir = 0
                    self.izbornik()
                    return

        def izracunajZavrsnoVrijeme(self, pocetno_vrijeme):

            godina = pocetno_vrijeme.split("-")[0].split("'")[1]
            mjesec = pocetno_vrijeme.split("-")[1]
            dan = pocetno_vrijeme.split("-")[2].split("T")[0]
            pocetni_sat = int(pocetno_vrijeme.split("T")[1].split(":")[0])
            pocetne_min = int(pocetno_vrijeme.split("T")[1].split(":")[1]) + int(self.trajanje_dogadjaja)

            if pocetne_min > 60:
                razlika = pocetne_min % 60
                pocetni_sat += pocetne_min / 60
                pocetne_min = razlika

            zavrsno_vrijeme = godina + "-" + mjesec + "-" + dan + "T" + str(pocetni_sat) + ":" + str(pocetne_min) \
                              + ":00.000Z"

            return zavrsno_vrijeme

    def _setup(self):

        time.sleep(5)

        print "\n Agent\t" + self.getName() + " je aktivan"

        povratna_informacija = ACLTemplate()
        povratna_informacija.setOntology("povratna_informacija")
        predlozak = spade.Behaviour.MessageTemplate(povratna_informacija)
        pregovaranje = self.Pregovaranje()

        self.addBehaviour(pregovaranje, predlozak)
        pregovaranje.prikaziIzbornik()


class KlijentAgent(Agent):
    google_client_id = ""
    google_client_secret = ""
    google_client_username = ""

    ne_preferirani_termini = ""

    class PrimiTerminSastanka(Behaviour):

        calendar = ""
        ime_agenta = ""
        pocetno_vrijeme = ""
        zavrsno_vrijeme = ""
        trajanje_dogadjaja = ""

        google_client_id = ""
        google_client_secret = ""
        google_client_username = ""

        ne_preferirani_termini = ""

        def setGoogleAccountPodatke(self, id, secret, user, ime, termini):
            self.google_client_id = id
            self.google_client_secret = secret
            self.google_client_username = user
            self.ime_agenta = ime
            self.ne_preferirani_termini = termini

            self.calendar = GoogleCalendar(self.google_client_id, self.google_client_secret,
                                           self.google_client_username)

        def _process(self):
            self.msg = None
            self.msg = self._receive(True)
            if self.msg:
                print "\nAgent " + self.ime_agenta + " : primio sam poruku :  %s " % self.msg.content

                if self.msg.content == "stop":
                    print "Agent " + self.ime_agenta + ": gasim se"
                    self.MyAgent._kill()

                if self.msg.content == "potvrda":
                    print "Agent " + self.ime_agenta + ": Sastanak potvrđen -\tgasim se"
                    self.MyAgent._kill()

                else:
                    vremena = self.msg.content.split("'")

                    self.pocetno_vrijeme = vremena[1]
                    self.zavrsno_vrijeme = vremena[3]
                    self.trajanje_dogadjaja = vremena[5]

                    rezultat = self.evaluirajPrijedlog(self.pocetno_vrijeme, self.zavrsno_vrijeme,
                                                       self.trajanje_dogadjaja)
                    self.posaljiOdgovor(rezultat)
            else:
                print "\nAgent " + self.ime_agenta + " : čekao sam ali nema poruke"
                self.posaljiOdgovor("Nisam primio poruku")

        def evaluirajPrijedlog(self, pocetno_vrijeme, zavrsno_vrijeme, trajanje):
            print "\nAgent " + self.ime_agenta.split(" ")[0] + " : Evaluiram prijedlog za sastankom"

            try:
                pocetak_godina = pocetno_vrijeme.split("-")[0]
                pocetak_mjesec = pocetno_vrijeme.split("-")[1]
                pocetak_dan = pocetno_vrijeme.split("-")[2].split("T")[0]
                zavrsetak_godina = zavrsno_vrijeme.split("-")[0]
                zavrsetak_mjesec = zavrsno_vrijeme.split("-")[1]
                zavrsetak_dan = zavrsno_vrijeme.split("-")[2].split("T")[0]

                slobodni_termini = []
                trajanje_intervala = int(trajanje)

                fiksni_zavrsni_sat = int(zavrsno_vrijeme.split("T")[1].split(":")[0])
                fiksne_zavrsne_min = int(zavrsno_vrijeme.split("T")[1].split(":")[1])

                pocetak_intervala_sati = int(pocetno_vrijeme.split("T")[1].split(":")[0])
                pocetak_intervala_minute = int(pocetno_vrijeme.split("T")[1].split(":")[1])

                pivot_intervala_sati_prednji = pocetak_intervala_sati
                pivot_intervala_minute_prednji = pocetak_intervala_minute

                ne_preferirani_pocetak_sati = int(self.ne_preferirani_termini[0].split(":")[0])
                ne_preferirani_pocetak_minute = int(self.ne_preferirani_termini[0].split(":")[1])
                ne_preferirani_zavrsetak_sati = int(self.ne_preferirani_termini[1].split(":")[0])
                ne_preferirani_zavrsetak_minute = int(self.ne_preferirani_termini[1].split(":")[1])

                while fiksni_zavrsni_sat - 1 >= pivot_intervala_sati_prednji \
                        and fiksne_zavrsne_min <= pivot_intervala_minute_prednji:

                    pivot_intervala_sati_zadnji = pivot_intervala_sati_prednji
                    pivot_intervala_minute_zadnji = pivot_intervala_minute_prednji

                    if ne_preferirani_pocetak_sati == pivot_intervala_sati_prednji \
                            and ne_preferirani_pocetak_minute <= pivot_intervala_minute_prednji:

                        slobodni_termini.append("Termin je blokiran !")
                        pivot_intervala_minute_prednji += trajanje_intervala

                        if pivot_intervala_minute_prednji >= 60:
                            pivot_intervala_sati_prednji += 1
                            pivot_intervala_minute_prednji = 0

                        continue

                    if ne_preferirani_zavrsetak_sati == pivot_intervala_sati_prednji \
                            and ne_preferirani_zavrsetak_minute >= pivot_intervala_minute_prednji:

                        slobodni_termini.append("Termin je blokiran !")
                        pivot_intervala_minute_prednji += trajanje_intervala

                        if pivot_intervala_minute_prednji >= 60:
                            pivot_intervala_sati_prednji += 1
                            pivot_intervala_minute_prednji = 0

                        continue

                    if ne_preferirani_pocetak_sati < pivot_intervala_sati_zadnji \
                            and ne_preferirani_zavrsetak_sati > pivot_intervala_sati_prednji:
                        slobodni_termini.append("Termin je blokiran !")
                        pivot_intervala_minute_prednji += trajanje_intervala

                        if pivot_intervala_minute_prednji >= 60:
                            pivot_intervala_sati_prednji += 1
                            pivot_intervala_minute_prednji = 0

                        continue

                    else:
                        pivot_intervala_minute_prednji += trajanje_intervala
                        if pivot_intervala_minute_prednji >= 60:
                            pivot_intervala_sati_prednji += 1
                            pivot_intervala_minute_prednji = 0

                        if pivot_intervala_sati_zadnji < 10:
                            pocetak_sat = "0%i" % (pivot_intervala_sati_zadnji)
                        else:
                            pocetak_sat = "%i" % (pivot_intervala_sati_zadnji)

                        if pivot_intervala_minute_zadnji < 10:
                            pocetak_minute = "0%i" % (pivot_intervala_minute_zadnji)
                        else:
                            pocetak_minute = "%i" % (pivot_intervala_minute_zadnji)

                        if pivot_intervala_sati_prednji < 10:
                            zavrsetak_sat = "0%i" % (pivot_intervala_sati_prednji )
                        else:
                            zavrsetak_sat = "%i" % (pivot_intervala_sati_prednji )

                        if pivot_intervala_minute_prednji < 10:
                            zavrsetak_minute = "0%i" % pivot_intervala_minute_prednji
                        else:
                            zavrsetak_minute = "%i" % (pivot_intervala_minute_prednji )

                        pocetno_vrijeme = pocetak_godina + "-" + pocetak_mjesec + "-" + pocetak_dan + "T" + \
                                          pocetak_sat + ":" + pocetak_minute + ":00.000Z"
                        zavrsno_vrijeme = zavrsetak_godina + "-" + zavrsetak_mjesec + "-" + str(zavrsetak_dan) + "T" \
                                          + zavrsetak_sat + ":" + zavrsetak_minute + ":00.000Z"

                        # TODO za ux je dobro da ispisuje al bespotrebno
                        print self.name + ": računam slobodno vrijeme..."

                        try:
                            if self.calendar.main(pocetno_vrijeme, zavrsno_vrijeme):
                                slobodni_termini.append(pocetno_vrijeme)
                        except:
                            continue

                return slobodni_termini

            except:
                return "Greska u evaluaciji"

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

            print  "\nAgent " + self.ime_agenta + " : poslao sam poruku agentu organizatoru %s\n!" % (odgovor)


    def _setup(self):

        print "\n Agent\t" + self.getAID().getName() + " je aktivan"

        feedback_template = ACLTemplate()
        feedback_template.setOntology("termin_sastanka")
        mt = MessageTemplate(feedback_template)
        termin = self.PrimiTerminSastanka()
        self.addBehaviour(termin, mt)
        termin.setGoogleAccountPodatke(self.google_client_id, self.google_client_secret, self.google_client_username,
                                       self.getAID().getName(), self.ne_preferirani_termini)


    def setGoogleAccountPodatke(self, id, secret, user, termini):
        self.google_client_id = id
        self.google_client_secret = secret
        self.google_client_username = user
        self.ne_preferirani_termini = termini


def inicijalizirajAgentaOrganizatora(i):
    ip = "agent_organizator@127.0.0.%i" % (i)
    korisnik = "organizator"

    o = OrganizatorAgent(ip, korisnik)
    o.start()


def inicijalizirajAgentaKlijenta(i):
    google_korisnici = {
        "2": ["466301455600-rull43ikdhd7d691dtcitufhnlab9nfu.apps.googleusercontent.com", "g7S6psNxN9tw7PmpILxIsxzw",
              "agent0.zavrsni@gmail.com", ["00:00", "08:00"]],
        "3": ["969348362348-nfs15alf9velcc7dr5312cebijs66cp4.apps.googleusercontent.com", "8Zt_4PsA_JpGGnmFO1PDETj3",
              "agent01.zavrsni@gmail.com", ["00:00", "06:00"]],
        "4": ["111267856009-qj1ravtgqptrlpb9nl83at347vhkgkpd.apps.googleusercontent.com", "8Zt_4PsA_JpGGnmFO1PDETj3",
              "agent02.zavrsni@gmail.com", ["22:00", "05:50"]],
        "5": ["485027726364-fgf7ng6oa671uti4lhv0ugsccilgln97.apps.googleusercontent.com", "d4UqsL3DF0sPZy2fxspKuvr_",
              "agent03.zavrsni@gmail.com", ["19:00", "23:00"]]}

    id = google_korisnici["%i" % (i)][0]
    secret = google_korisnici["%i" % (i)][1]
    user = google_korisnici["%i" % (i)][2]
    termini = google_korisnici["%i" % (i)][3]

    ip = "agent_klijent%i@127.0.0.1" % (i)
    korisnik = "klijent_0%i" % (i)
    k = KlijentAgent(ip, korisnik)
    k.start()
    k.setGoogleAccountPodatke(id, secret, user, termini)


if __name__ == '__main__':

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