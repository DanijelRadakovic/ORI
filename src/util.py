import heapq
import random


class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.
    """
    def __init__(self):
        self.__heap = []

    def __len__(self):
        return len(self.__heap)

    def push(self, item, priority):
        """
        Add item to priority queue
        :param item: item that needs to be added
        :param priority: item's priority
        """
        entry = (priority, item)
        heapq.heappush(self.__heap, entry)

    def pop(self):
        """
        Remove item from priority queue with lowest priority
        :return: item with lowest priority
        """
        (_, item) = heapq.heappop(self.__heap)
        return item

    def is_empty(self):
        """
        Checks if priority queue is empty
        :return: true if priority is empty, otherwise false
        """
        return len(self.__heap) == 0

    def update(self, item, priority):
        """
        If item already in priority queue with higher priority, update its priority
        and rebuild the __heap.
        If item already in priority queue with equal or lower priority, do nothing.
        If item not in priority queue, do the same thing as self.push.
        :param item: item that needs to be updated
        :param priority: item's priority
        """
        for index, (p, c, i) in enumerate(self.__heap):
            if i == item:
                if p <= priority:
                    break
                del self.__heap[index]
                self.__heap.append((priority, c, item))
                heapq.heapify(self.__heap)
                break
        else:
            self.push(item, priority)

    def clear(self):
        self.__heap = []


class PriorityQueueWithFunction(PriorityQueue):
    """
    Implements a priority queue with the same push/pop signature of the
    Queue and the Stack classes. This is designed for drop-in replacement for
    those two classes. The caller has to provide a priority function, which
    extracts each item's priority.
    """
    def __init__(self, priority_function):
        """
        priority_function (item) -> priority
        :param priority_function: priority_function
        """
        self.priorityFunction = priority_function      # store the priority function
        PriorityQueue.__init__(self)        # super-class initializer

    def push(self, item, priority=None):
        """
        Adds an item to the queue with priority from the priority function
        :param item: item that needs to be added to priority queue
        :param priority: it should be always None
        """
        PriorityQueue.push(self, item, self.priorityFunction(item))


def flip_coin(p):
    """
    Probability indicator
    :param p: probability
    :return: is p greater than random number
    """
    r = random.random()
    return r < p
