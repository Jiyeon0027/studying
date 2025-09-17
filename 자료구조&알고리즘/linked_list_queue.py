"""연결 리스트 큐를 구현한 파일

Raises:
    IndexError: 인덱스 초과 예외

Returns:
    _type_: 연결 리스트 큐
"""


class Node:
    """
    연결 리스트 큐의 노드 클래스
    """

    def __init__(self, item):
        self.data = item
        self.prev = None
        self.next = None


class DoublyLinkedList:
    """
    연결 리스트 큐의 이중 연결 리스트 클래스
    """

    def __init__(self):
        self.node_count = 0
        self.head = Node(None)
        self.tail = Node(None)
        self.head.prev = None
        self.head.next = self.tail
        self.tail.prev = self.head
        self.tail.next = None

    def __repr__(self):
        if self.node_count == 0:
            return "LinkedList: empty"

        s = ""
        curr = self.head
        while curr.next.next:
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

    def reverse(self):
        result = []
        curr = self.tail
        while curr.prev.prev:
            curr = curr.prev
            result.append(curr.data)
        return result

    def get_at(self, pos):
        if pos < 0 or pos > self.node_count:
            return None

        if pos > self.node_count // 2:
            i = 0
            curr = self.tail
            while i < self.node_count - pos + 1:
                curr = curr.prev
                i += 1
        else:
            i = 0
            curr = self.head
            while i < pos:
                curr = curr.next
                i += 1

        return curr

    def insert_after(self, prev, new_node):
        next_node = prev.next
        new_node.prev = prev
        new_node.next = next_node
        prev.next = new_node
        next_node.prev = new_node
        self.node_count += 1
        return True

    def insert_at(self, pos, new_node):
        if pos < 1 or pos > self.node_count + 1:
            return False

        prev = self.get_at(pos - 1)
        return self.insert_after(prev, new_node)

    def pop_after(self, prev):
        curr = prev.next
        next_node = curr.next
        prev.next = next_node
        next_node.prev = prev
        self.node_count -= 1
        return curr.data

    def pop_at(self, pos):
        if pos < 1 or pos > self.node_count:
            raise IndexError("Index out of range")

        prev = self.get_at(pos - 1)
        return self.pop_after(prev)

    def concat(self, next_l):
        self.tail.prev.next = next_l.head.next
        next_l.head.next.prev = self.tail.prev
        self.tail = next_l.tail

        self.node_count += next_l.node_count


class LinkedListQueue:
    """
    연결 리스트 큐 클래스
    """

    def __init__(self):
        self.data = DoublyLinkedList()

    def size(self):
        return self.data.get_length()

    def is_empty(self):
        return True if self.data.get_length() == 0 else False

    def enqueue(self, item):
        node = Node(item)
        self.data.insert_at(self.data.get_length() + 1, node)

    def dequeue(self):
        return self.data.pop_at(1)

    def peek(self):
        return self.data.get_at(1).data
