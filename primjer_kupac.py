#!/usr/bin/env python
# -*- coding: utf-8 -*-

import spade
from spade.Agent import Agent
from spade.DF import ServiceDescription
from spade.Behaviour import OneShotBehaviour, EventBehaviour, ACLTemplate, MessageTemplate
from spade.ACLMessage import ACLMessage

import sys
from time import sleep

class Kupac( Agent ):
  class InicijalnaPonuda( OneShotBehaviour ):
    def _process( self ):
      msg = ACLMessage()
      primatelj = spade.AID.aid(name="prodavac@127.0.0.1", addresses=["xmpp://prodavac@127.0.0.1"])
      msg.addReceiver( primatelj )
      msg.setOntology( 'pregovaranje' )
      msg.setContent( '
'.join( [ ':'.join( par ) for par in self.myAgent.moja_ponuda.items() ] ) )
      self.myAgent.send( msg )
        
  class Pregovaranje( EventBehaviour ):
    def _process( self ):
      self.msg = None
      self.msg = self._receive( True )
      if self.msg:
    if self.msg.content == 'odbij' or self.msg.content == 'prihvati':
      self.myAgent._kill()
    redovi = self.msg.content.split( '
' )
    ponuda = dict( [ red.split( ':' ) for red in redovi ] )
    interpretacija = self.myAgent.interpretiraj( ponuda )
    
    msg = ACLMessage()
    msg.addReceiver( self.msg.sender )
    msg.setOntology( 'pregovaranje' )
    
    if interpretacija == 'odbij' or interpretacija == 'prihvati':
      msg.setContent( interpretacija )
      self.myAgent.send( msg )
      self.myAgent._kill()
    else:
      msg.setContent( '
'.join( [ ':'.join( par ) for par in interpretacija.items() ] ) )
      sleep( 1 )
      self.myAgent.send( msg )
    

  def interpretiraj( self, ponuda ):
    self.vrijeme -= 1
    if self.vrijeme == 0:
      print 'Kupac: Odbijam ponudu zbog isteka vremena:', ponuda
      return 'odbij'
    else:
      self.moja_ponuda = self.generiraj_ponudu( ponuda )
      if self.evaluiraj( self.moja_ponuda ) + 1 >= self.evaluiraj( ponuda ):
    print 'Kupac: Prihvaćam ponudu:', ponuda
    return 'prihvati'
      else:
    print 'Kupac: Dajem protuponudu:', self.moja_ponuda
    return self.moja_ponuda
  
  def evaluiraj( self, ponuda ):
    return sum( [ float( i ) for i in ponuda.values() ] )
  
  def generiraj_ponudu( self, ponuda ):
    p = {}
    for proizvod in self.moja_ponuda.keys():
      p[ proizvod ] = str( float( self.moja_ponuda[ proizvod ] ) + ( float( ponuda[ proizvod ] ) - float( self.moja_ponuda[ proizvod ] ) ) / 50.0 )
    return p

  def _setup( self ):
    p = ACLTemplate()
    p.setOntology( 'pregovaranje' )
    m = MessageTemplate( p )
    self.addBehaviour( self.Pregovaranje(), m )
    
    self.moja_ponuda = { 'a':'0', 'b':'0'  }
    self.vrijeme = 20
    
    self.addBehaviour( self.InicijalnaPonuda() )
    
if __name__ == '__main__':
  p = Kupac( 'kupac@127.0.0.1', 'tajna' )
  p.start()
