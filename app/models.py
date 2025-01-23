from typing import List
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

service_mechanics = db.Table(
    'service_mechanics',
    Base.metadata,
    db.Column('service_ticket_id', db.ForeignKey('service_tickets.id')),
    db.Column('mechanic_id', db.ForeignKey('mechanics.id'))
)

class ServiceTicketPart(Base):
    __tablename__ = 'service_ticket_parts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    service_ticket_id: Mapped[int] = mapped_column(db.ForeignKey('service_tickets.id'), nullable=False)
    part_id: Mapped[int] = mapped_column(db.ForeignKey('parts.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(db.Integer, nullable=False)
    
    service_ticket: Mapped['ServiceTicket'] = db.relationship(back_populates='service_ticket_parts')
    part: Mapped['Part'] = db.relationship(back_populates='service_ticket_parts')

class Customer(Base):
    __tablename__ = 'customers'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(100), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(db.String(20), unique=True)
    password: Mapped[str] = mapped_column(db.String(100), nullable=False)
    
    service_tickets: Mapped[List['ServiceTicket']] = db.relationship(back_populates='customer', cascade="all, delete")
    
class ServiceTicket(Base):
    __tablename__ = 'service_tickets'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    VIN: Mapped[str] = mapped_column(db.String(17), nullable=False)
    service_date: Mapped[str] = mapped_column(db.String(10), nullable=False)
    service_desc: Mapped[str] = mapped_column(db.String(255))
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id'), nullable=False)
    
    customer: Mapped['Customer'] = db.relationship(back_populates='service_tickets')
    mechanics: Mapped[List['Mechanic']] = db.relationship(secondary=service_mechanics, back_populates='service_tickets')
    service_ticket_parts: Mapped[List['ServiceTicketPart']] = db.relationship(back_populates='service_ticket', cascade="all, delete")
    parts: Mapped[List['Part']] = db.relationship(secondary='service_ticket_parts', back_populates='service_tickets', overlaps="part, service_ticket, service_ticket_parts")
   
class Mechanic(Base):
    __tablename__ = 'mechanics'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(100), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(db.String(20), unique=True)
    salary: Mapped[float] = mapped_column(db.Float(10), nullable=False)
    password: Mapped[str] = mapped_column(db.String(100), nullable=False)
    
    service_tickets: Mapped[List['ServiceTicket']] = db.relationship(secondary=service_mechanics, back_populates='mechanics', cascade="all, delete")
    
class Part(Base):
    __tablename__ = 'parts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    price: Mapped[float] = mapped_column(db.Float(10), nullable=False)
    quantity: Mapped[int] = mapped_column(db.Integer, nullable=False)
    
    service_ticket_parts: Mapped[List['ServiceTicketPart']] = db.relationship(back_populates='part', cascade="all, delete", overlaps="parts")
    service_tickets: Mapped[List['ServiceTicket']] = db.relationship(secondary='service_ticket_parts', back_populates='parts', cascade="all, delete", overlaps="part, service_ticket, service_ticket_parts")
