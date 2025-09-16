class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.nodeCount = 0
    
    def __repr__(self): #문자열 표현
        if self.head is None:
            return 'LinkedList: empty'
        s = ''
        curr = self.head
        while curr is not None:
            s += repr(curr.data)
            if curr.next is not None:
                s += ' -> '
            curr = curr.next
        return s
    
    def getAt(self, pos):# pos 번째 노드 반환
        if pos < 1 or pos > self.nodeCount:
            return None
        curr = self.head # 첫 노드부터 시작
        i=1
        while i<pos :
            curr = curr.next
            i+=1
        return curr
    
    def insertAt(self, pos, newNode):# pos 앞에 노드 삽입
        if pos < 1 or pos > self.nodeCount + 1:
            return False # 범위 초과
        
        if pos == 1:
            newNode.next = self.head
            self.head = newNode
        else:
            if pos == self.nodeCount + 1:
                prev = self.tail
            else:
                prev = self.getAt(pos-1)
            newNode.next = prev.next
            prev.next = newNode
        
        if pos == self.nodeCount + 1:
            self.tail = newNode
            
        # print(self.head.data, self.tail.data)
        self.nodeCount += 1
        return True
    
    def popAt(self, pos):# pos 번째 노드 삭제
        if pos < 1 or pos > self.nodeCount:
            raise IndexError
        
        if pos == 1:
            curr = self.head
            self.head = self.head.next
            
            if pos == self.nodeCount:
                self.tail = None
        
        else:
            prev = self.getAt(pos-1)
            curr = prev.next
            prev.next = curr.next
            
            if pos == self.nodeCount:
                self.tail = prev
            
        self.nodeCount -= 1
        return curr.data
    
    def concat(self, L):
        self.tail.next = L.head # 여기서 왜 L.tail이 None일 가능성이 있다면 L.head가 None일 가능성이 있는 것 아닌가???? 흠ㅇ므
        if L.tail:
            self.tail = L.tail
        self.nodeCount += L.nodeCount
        return True
