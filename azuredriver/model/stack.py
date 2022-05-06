'''Module to maintain stack'''


class Stack():
    '''This class is used to maintain stack'''

    def __init__(self, stack_id, name, status):
        self.stack_id = stack_id
        self.name = name
        self.status = status

    def __str__(self):
        return f'id: {self.stack_id} name: {self.name} status: {self.status}'

    @classmethod
    def from_dict(cls, dict_map):
        '''Class method'''
        return Stack(dict_map.get('StackId', None), dict_map.get('StackName', None),
        dict_map.get('StackStatus', None))

    def to_dict(self):
        '''This method is used to set data to dict'''
        return {
            'id': self.stack_id,
            'name': self.name,
            'status': self.status
        }
