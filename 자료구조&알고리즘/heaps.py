"""
배열을 이용한 이진트리의 구현
"""


class MaxHeap:
    """
    배열을 이용한 이진트리의 구현
    """

    def __init__(self):
        # 0번째 인덱스는 사용하지 않음
        self.data = [None]

    def insert(self, item):
        self.data.append(item)  # 맨 마지막에 추가
        self.heapify_up(len(self.data) - 1)

    def heapify_up(self, index):
        parent = index // 2
        if parent > 0 and self.data[index] > self.data[parent]:
            self.data[index], self.data[parent] = (
                self.data[parent],
                self.data[index],
            )
            self.heapify_up(parent)

    def remove(self):
        if len(self.data) == 1:
            data = None
        else:
            self.data[1], self.data[-1] = self.data[-1], self.data[1]
            data = self.data.pop(-1)  # 맨 마지막 원소를 제거
            self.max_heapify(1)
        return data

    def max_heapify(self, index):
        left = index * 2
        right = index * 2 + 1
        smallest = index
        if left < len(self.data) and self.data[left] > self.data[smallest]:
            smallest = left
        if right < len(self.data) and self.data[right] > self.data[smallest]:
            smallest = right
        if smallest != index:
            self.data[index], self.data[smallest] = (
                self.data[smallest],
                self.data[index],
            )
            self.max_heapify(smallest)
