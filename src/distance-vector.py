import sys
sys.path.append('..')

from src.sim import Sim
from src import node
from src import link
from src import packet

from networks.network import Network

class RoutingTable(object):
    def __init__(self):
        # format for data: {destination_address: [cost, link_address]}
        self.routing_table = dict()

        # format: {neighbor_hostname: {destination_address: cost}}
        self.neighbor_routing_tables = {}

    def get_routing_table(self):
        # format: {destination_address: cost}
        output_table = dict()
        for destination_address, entry in self.routing_table.iteritems():
            output_table[destination_address] = entry[0]

        return output_table

    def check_link_to_self(self, this_node, destination_hostname):
        this_address = this_node.get_address(destination_hostname)
        updated = False

        if self.routing_table.get(this_address) is None:
            self.routing_table[this_address] = [0, None]
            updated = True

        return this_address, updated

    # handle neighbor routing tables

    def upsert_neighbor_routing_table(self, hostname, neighbor_routing_table):
        self.neighbor_routing_tables[hostname] = neighbor_routing_table

    def refresh_routing_table(self, this_node):
        updated_routing_table = False

        for hostname, destinations in self.neighbor_routing_tables.iteritems():
            for destination_address, cost in destinations.iteritems():
                if self.routing_table.get(destination_address) is None \
                            or (cost + 1) < self.routing_table[destination_address][0]:
                    self.routing_table[destination_address] = [cost + 1, this_node.get_link(hostname)]
                    updated_routing_table = True

        return updated_routing_table

class DistanceVectorApp(object):
    def __init__(self, node):
        # the format used for the routing table is {address: cost}
        self.routing_table = RoutingTable()
        self.node = node
        self.source_address = None
        self.broadcast_count = 0

    def receive_packet(self,received_packet):
        # print Sim.scheduler.current_time(), self.node.hostname, received_packet.ident, received_packet.body
        hostname = received_packet.body['hostname']
        neighbor_routing_table = received_packet.body['routing_table']

        self.source_address, updated_self_link = self.routing_table.check_link_to_self(self.node, hostname)
        self.routing_table.upsert_neighbor_routing_table(hostname, neighbor_routing_table)
        updated_routing_table = self.routing_table.refresh_routing_table(self.node)

        if updated_routing_table or updated_self_link:
            print ("%d, %s, Updated Routing Table Values:" + str(self.routing_table.get_routing_table())) % (Sim.scheduler.current_time(), self.node.hostname)
            # print "%s neighbor routing tables: %s" % (self.node.hostname, self.routing_table.neighbor_routing_tables)

    def broadcast_routing_table(self, event):
        routing_table = self.routing_table.get_routing_table()
        hostname = self.node.hostname

        data_dictionary = dict()
        data_dictionary['hostname'] = hostname
        data_dictionary['routing_table'] = routing_table

        routing_table_packet = packet.Packet(destination_address=0, ident=0, ttl=1, protocol='dvrouting', body=data_dictionary)
        Sim.scheduler.add(delay=0, event=routing_table_packet, handler=self.node.send_packet)

        if self.broadcast_count < 100:
            Sim.scheduler.add(delay=30, event="", handler=self.broadcast_routing_table)
            self.broadcast_count += 1
        else:
            print "--------> ENDING <--------"

if __name__ == '__main__':
    # parameters
    Sim.scheduler.reset()
    Sim.set_debug(True)

    # setup network
    net = Network('../networks/five-nodes.txt')

    # get nodes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    n3 = net.get_node('n3')
    n4 = net.get_node('n4')
    n5 = net.get_node('n5')
    # n6 = net.get_node('n6')
    # n7 = net.get_node('n7')
    # n8 = net.get_node('n8')
    # n9 = net.get_node('n9')
    # n10 = net.get_node('n10')
    # n11 = net.get_node('n11')
    # n12 = net.get_node('n12')
    # n13 = net.get_node('n13')
    # n14 = net.get_node('n14')
    # n15 = net.get_node('n15')

    # setup broadcast application
    d1 = DistanceVectorApp(n1)
    n1.add_protocol(protocol="dvrouting",handler=d1)
    d2 = DistanceVectorApp(n2)
    n2.add_protocol(protocol="dvrouting",handler=d2)
    d3 = DistanceVectorApp(n3)
    n3.add_protocol(protocol="dvrouting",handler=d3)
    d4 = DistanceVectorApp(n4)
    n4.add_protocol(protocol="dvrouting",handler=d4)
    d5 = DistanceVectorApp(n5)
    n5.add_protocol(protocol="dvrouting",handler=d5)
    # d6 = DistanceVectorApp(n6)
    # n6.add_protocol(protocol="dvrouting", handler=d6)
    # d7 = DistanceVectorApp(n7)
    # n7.add_protocol(protocol="dvrouting", handler=d7)
    # d8 = DistanceVectorApp(n8)
    # n8.add_protocol(protocol="dvrouting", handler=d8)
    # d9 = DistanceVectorApp(n9)
    # n9.add_protocol(protocol="dvrouting", handler=d9)
    # d10 = DistanceVectorApp(n10)
    # n10.add_protocol(protocol="dvrouting", handler=d10)
    # d11 = DistanceVectorApp(n11)
    # n11.add_protocol(protocol="dvrouting", handler=d11)
    # d12 = DistanceVectorApp(n12)
    # n12.add_protocol(protocol="dvrouting", handler=d12)
    # d13 = DistanceVectorApp(n13)
    # n13.add_protocol(protocol="dvrouting", handler=d13)
    # d14 = DistanceVectorApp(n14)
    # n14.add_protocol(protocol="dvrouting", handler=d14)
    # d15 = DistanceVectorApp(n15)
    # n15.add_protocol(protocol="dvrouting", handler=d15)

    d1.broadcast_routing_table("")
    d2.broadcast_routing_table("")
    d3.broadcast_routing_table("")
    d4.broadcast_routing_table("")
    d5.broadcast_routing_table("")
    # d6.broadcast_routing_table("")
    # d7.broadcast_routing_table("")
    # d8.broadcast_routing_table("")
    # d9.broadcast_routing_table("")
    # d10.broadcast_routing_table("")
    # d11.broadcast_routing_table("")
    # d12.broadcast_routing_table("")
    # d13.broadcast_routing_table("")
    # d14.broadcast_routing_table("")
    # d15.broadcast_routing_table("")

    # run the simulation
    Sim.scheduler.run()
