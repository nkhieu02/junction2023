from dataclasses import dataclass
from queue import PriorityQueue
from typing import List, Callable
from langchain.schema import Document

DOCUMENTS: List[Document] = []



@dataclass
class Node:
    id: int
    messages: List[dict] 
    value: float = None
    parent: int = None

@dataclass
class Tot:

    '''
    n: Number of nodes
    Required:
    - generate: function, takes previous thoughts, prompt, and number of child
    - score: function
    - goal_check: function
    - prompt: str

    Non-Required but important:
    - cut-off: cut off for the node value
    - max-tries: limit number of decomposing a node
    '''
    retrieve: Callable
    generate: Callable
    score: Callable
    goal_check: Callable
    messages: List[dict]
    n: int = 0 # total node
    nof_child: int = 3
    # important hyper-parameter
    cut_off: float = 3
    max_tries: int = 20
    total_tries = 1 # Count the first thought as well
    priority_queue: PriorityQueue = PriorityQueue(maxsize=100)
    nodes = set()
    goal_reached: bool = False

    def __post_init__(self):
        ids = list(range(self.nof_child))
        self.n += self.nof_child
        last_question = self.messages[-1]['content']
        if len(last_question) > 10:
            self.retrieve(self.messages)
        nodes = [Node(id=id, messages=self.messages) for id in ids]
        # Generate next thought for all child nodes
        thoughts = self.generate(self.messages, self.nof_child)
        for i,thought in enumerate(thoughts):
            nodes[i].messages.append({'role': 'user', 'content': 'Give me your next thought.'})
            nodes[i].messages.append({'role': 'assistant', 'content': thought})
        # Compute the value for each node then push to the queue
        for node in nodes:
            # No cut off for first initialize
            node.value = self.score(node.messages)
            self.priority_queue.put((-node.value, node))

    def _create_childs(self, parent_node: Node):
        ids = list(range(self.n + 1, self.n + self.nof_child + 1))
        self.n += self.nof_child
        nodes = [Node(id=id, messages=parent_node.messages) for id in ids]
        # Generate next thought for all child nodes
        thoughts = self.generate(parent_node.messages, self.nof_child)
        for i,thought in enumerate(thoughts):
            nodes[i].messages.append({'role': 'user', 'content': 'Give me your next thought.'})
            nodes[i].messages.append({'role': 'assistant', 'content': thought})
        # Compute the value for each node then push to the queue
        for node in nodes:
            # No cut off for first initialize
            node.value = self.score(node.messages)
            self.priority_queue.put((-node.value, node))
        for node in nodes:
            if node.value < self.cut_off:
                continue
            self.priority_queue.put((-node.value, node))
    
    def search_answer(self):

        while (not self.goal_reached) and (self.total_tries < self.max_tries):
            
            _, node = self.priority_queue.get()
            self.goal_reached = self.goal_check(node.messages)
            if self.goal_reached:
                return node.messages
            
            # Create more child
            self._create_childs(node)
            self.total_tries += 1

        

        
    

        
    
    
