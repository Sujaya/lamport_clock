# lamport_clock
Implementing Lamport clock for distributed processes.


Message format:
client to DC

CLIREQ: \<dcID>, \<noOfTickets>
CLIREQ: 1, 4


Between DCs:
REQ: \<selfID>, \<noOfTickets>
REP: \<selfID>, \<noOfTickets>
REL: \<selfID>, \<remTickets>
