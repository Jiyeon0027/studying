"""
더미 노드를 사용한 연결 리스트를 구현한 파일
"""


class Node:
    """
    더미 노드를 사용한 연결 리스트의 노드 클래스
    """

    def __init__(self, item):
        self.data = item
        self.next = None


class LinkedList:
    """
    더미 노드를 사용한 연결 리스트
    """

    def __init__(self):
        self.node_count = 0
        self.head = Node(None)
        self.tail = None
        self.head.next = self.tail

    def __repr__(self):
        if self.node_count == 0:
            return "LinkedList: empty"

        s = ""
        curr = self.head
        while curr.next:
            curr = curr.next
            s += repr(curr.data)
            if curr.next is not None:
                s += " -> "
        return s

    def get_length(self):
        return self.node_count

    def traverse(self):
        result = []
        curr = self.head
        while curr.next:
            curr = curr.next
            result.append(curr.data)
        return result

    def get_at(self, pos):
        if pos < 0 or pos > self.node_count:
            return None

        i = 0
        curr = self.head
        while i < pos:
            curr = curr.next
            i += 1

        return curr

    def insert_after(self, prev, new_node):
        new_node.next = prev.next
        if prev.next is None:
            self.tail = new_node
        prev.next = new_node
        self.node_count += 1
        return True

    def insert_at(self, pos, new_node):
        if pos < 1 or pos > self.node_count + 1:
            return False

        if pos != 1 and pos == self.node_count + 1:
            prev = self.tail
        else:
            prev = self.get_at(pos - 1)
        return self.insert_after(prev, new_node)

    def pop_after(self, prev):
        curr = prev.next
        prev.next = curr.next
        if curr.next is None:
            self.tail = prev
        self.node_count -= 1
        return curr.data

    def pop_at(self, pos):
        if pos < 1 or pos > self.node_count:
            return None

        prev = self.get_at(pos - 1)
        return self.pop_after(prev)

    def concat(self, next_l):
        self.tail.next = next_l.head.next
        if next_l.tail:
            self.tail = next_l.tail
        self.node_count += next_l.node_count
