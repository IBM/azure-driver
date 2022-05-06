'''Python script for Associated Topology'''
from ignition.model.associated_topology import AssociatedTopology

STACK_RESOURCE_TYPE = 'Azure'
STACK_NAME = 'InfrastructureStack'


class AZUREAssociatedTopology(AssociatedTopology):
    '''This class is used manage associated topolgy'''

    def add_stack_id(self, resource_name, stack_id):
        '''This method is used to add stack id'''
        self.add_entry(resource_name, stack_id, STACK_RESOURCE_TYPE)

    def get_stack_id(self, resource_name):
        '''This method is used to get the stack id'''
        entry = self.get(resource_name)
        if entry is not None:
            return entry.to_dict()['id']
        else:
            return None
