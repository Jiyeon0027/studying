class Node:

    def __init__(self, key, data):
        self.key = key
        self.data = data
        self.left = None
        self.right = None

    def insert(self, key, data):
        if self.key < key:
            if self.right:
                self.right.insert(key, data)
            else:
                self.right = Node(key, data)
        elif self.key > key:
            if self.left:
                self.left.insert(key, data)
            else:
                self.left = Node(key, data)
        else:  # key == self.key
            raise KeyError("Key already exists")

    def inorderTraversal(self, node):
        traversal = []
        if node:
            traversal = self.inorderTraversal(node.left)
            traversal.append(node.key)
            traversal = self.inorderTraversal(node.right)
        return traversal

    def min(self):
        if self.left:
            return self.left.min()
        else:
            return self

    def max(self):
        if self.right:
            return self.right.max()
        else:
            return self

    def lookup(self, key, parent=None):
        if key < self.key:
            if self.left:
                return self.left.lookup(key, self)
            else:
                return None, None

        elif key > self.key:
            if self.right:
                return self.right.lookup(key, self)
            else:
                return None, None

        else:  # key == self.key
            return self, parent


class BinarySearchTree:

    def __init__(self):
        self.root = None

    def inorderTraversal(self):
        if self.root:
            return self.root.inorderTraversal(self.root)
        else:
            return []

    def insert(self, key, data):
        if self.root:
            self.root.insert(key, data)
        else:
            self.root = Node(key, data)

    def min(self):
        if self.root:
            return self.root.min()
        else:
            return self

    def max(self):
        if self.root:
            return self.root.max()
        else:
            return None

    def lookeup(self, key):
        if self.root:
            return self.root.lookup(key)
        else:
            return None, None
