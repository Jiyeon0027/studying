"""
이중 연결 리스트를 구현한 파일
"""


class Node:
    """
    이중 연결 리스트의 노드 클래스
    """

    def __init__(self, item):
        self.data = item
        self.prev = None
        self.next = None


class DoublyLinkedList:
    """
    이중 연결 리스트 클래스
    """

    def __init__(self):
        self.node_count = 0
        self.head = Node(None)
        self.tail = Node(None)
        self.head.prev = None
        self.head.next = self.tail
        self.tail.prev = self.head
        self.tail.next = None

    def concat(self, next_l):
        self.tail.prev.next = next_l.head.next
        next_l.head.next.prev = self.tail.prev
        next_l.tail.prev.next = self.tail
        self.tail.prev = next_l.tail.prev
        self.node_count += next_l.node_count
        return True

    def traverse(self):
        result = []
        curr = self.head
        while curr.next.next:
            curr = curr.next
            result.append(curr.data)
        return result

    def get_at(self, pos):  # 이중 연결리스트이므로 앞뒤의 갯수 판별 후 확인
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

    def insert_before(self, next_node, new_node):
        before = next_node.prev
        new_node.next = next_node
        new_node.prev = before
        before.next = new_node
        next_node.prev = new_node
        self.node_count += 1
        return True

    def insert_at(self, pos, new_node):
        if pos < 1 or pos > self.node_count + 1:
            return False

        prev = self.get_at(pos - 1)
        return self.insert_after(prev, new_node)

    def pop_after(self, prev):
        cur = prev.next
        cur.next.prev = prev
        prev.next = cur.next
        self.node_count -= 1
        return cur.data

    def pop_before(self, next_node):
        cur = next_node.prev
        next_node.prev = cur.prev
        cur.prev.next = cur.next
        self.node_count -= 1
        return cur.data

    def pop_at(self, pos):
        if pos < 0 or pos > self.node_count:
            raise IndexError
        prev = self.get_at(pos - 1)
        return self.pop_after(prev)
