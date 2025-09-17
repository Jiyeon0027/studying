"""
연결 리스트를 구현한 파일
"""


class Node:
    """
    연결 리스트의 노드 클래스
    """

    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    """
    연결 리스트 클래스
    """

    def __init__(self):
        self.head = None
        self.tail = None
        self.node_count = 0

    def __repr__(self):  # 문자열 표현
        if self.head is None:
            return "LinkedList: empty"
        s = ""
        curr = self.head
        while curr is not None:
            s += repr(curr.data)
            if curr.next is not None:
                s += " -> "
            curr = curr.next
        return s

    def get_at(self, pos):  # pos 번째 노드 반환
        if pos < 1 or pos > self.node_count:
            return None
        curr = self.head  # 첫 노드부터 시작
        i = 1
        while i < pos:
            curr = curr.next
            i += 1
        return curr

    def insert_at(self, pos, new_node):  # pos 앞에 노드 삽입
        if pos < 1 or pos > self.node_count + 1:
            return False  # 범위 초과

        if pos == 1:
            new_node.next = self.head
            self.head = new_node
        else:
            if pos == self.node_count + 1:
                prev = self.tail
            else:
                prev = self.get_at(pos - 1)
            new_node.next = prev.next
            prev.next = new_node

        if pos == self.node_count + 1:
            self.tail = new_node

        # print(self.head.data, self.tail.data)
        self.node_count += 1
        return True

    def pop_at(self, pos):  # pos 번째 노드 삭제
        if pos < 1 or pos > self.node_count:
            raise IndexError

        if pos == 1:
            curr = self.head
            self.head = self.head.next

            if pos == self.node_count:
                self.tail = None

        else:
            prev = self.get_at(pos - 1)
            curr = prev.next
            prev.next = curr.next

            if pos == self.node_count:
                self.tail = prev

        self.node_count -= 1
        return curr.data

    def concat(self, next_l):
        self.tail.next = next_l.head
        # 여기서 왜 next_l.tail이 None일 가능성이 있다면 next_l.head가 None일 가능성이 있는 것 아닌가?
        if next_l.tail:
            self.tail = next_l.tail
            self.node_count += next_l.node_count
        return True
