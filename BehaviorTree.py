'''
def fallback(methodList):
    for met in methodList:
        if met == 'running':
            return 'running'
        if met == 'done':
            return 'done'
        res=None
        if met != 'failed':
            res=met()
        if res != None and res=='running':
            return 'running'
        if res != None and res == 'done':
            return 'done'
    return 'failed'

def sequence(methodList):
    for met in methodList:
        if met == 'running':
            return 'running'
        if met == 'failed':
            return 'failed'
        res = None
        if met != 'done':
            res = met()
        if res != None and res == 'running':
            return 'running'
        if res != None and res == 'failed':
            return 'failed'
    return 'done'


def t1():
    return 'done'
def t2():
    return 'running'
def t3():
    return 'failed'
'''


class BTNode:
    methodList=None

    def __init__(self, list):
        self.methodList=list

    def run(self):
        return None

class Fallback(BTNode):
    def run(self):
        for met in self.methodList:
            if met == 'running':
                return 'running'
            if met == 'done':
                return 'done'
            res = None
            if met != 'failed':
                res = met()
            if res != None and res == 'running':
                return 'running'
            if res != None and res == 'done':
                return 'done'
        return 'failed'

class Sequence(BTNode):
    def run(self):
        for met in self.methodList:
            if met == 'running':
                return 'running'
            if met == 'failed':
                return 'failed'
            res = None
            if met != 'done':
                res = met()
            if res != None and res == 'running':
                return 'running'
            if res != None and res == 'failed':
                return 'failed'
        return 'done'