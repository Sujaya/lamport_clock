# lamport_clock
Implementing Lamport clock for distributed processes.


Message format:\
client to DC

CLIREQ: \<dcID>, \<noOfTickets>
CLIREQ: 1, 4


Between DCs:\
REQ: \<selfID>, \<noOfTickets>
REP: \<selfID>, \<noOfTickets>
REL: \<selfID>, \<remTickets>


serverConfig:\

{
	"datacenters": {
		"d1": ["127.0.0.1", 5001],
		"d2": ["127.0.0.1", 5002],
		"d3": ["127.0.0.1", 5003]
	},

	"tickets": 20
}
