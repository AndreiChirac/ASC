"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

import time
from threading import Thread


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time

    """
    metoda care realizeaza cererile de adaugare a unui produs in cos
    """
    def add_request(self, requests, new_cart_id):
        requests_made = 1
        while True:

            if requests_made > requests["quantity"]:
                break

            error_code = self.marketplace.add_to_cart(
                new_cart_id, requests["product"])

            if error_code or error_code is None:
                requests_made += 1
            else:
                time.sleep(self.retry_wait_time)
    """
    metoda care realizeaza cererile de scoatere a unui produs din cos
    """
    def rm_request(self, requests, new_cart_id):
        requests_made = 1
        while True:

            if requests_made > requests["quantity"]:
                break

            error_code = self.marketplace.remove_from_cart(
                new_cart_id, requests["product"])

            if error_code or error_code is None:
                requests_made += 1
            else:
                time.sleep(self.retry_wait_time)

    def run(self):
        """
        luam fiecare lista din cadrul lui carts deoarece pentru fiecare lista vom avea un id nou pentru cos
        """
        for new_cart in self.carts:

            new_cart_id = self.marketplace.new_cart()
            """
            parcurgem fiecare operatie de add sau remove si o tratam specific 
            """
            for requests in new_cart:
                if requests["type"] == "add":
                    self.add_request(requests, new_cart_id)
                else:
                    self.rm_request(requests, new_cart_id)
            """
            dupa ce am terminat toate opertaiile din cadrul listei trebuie sa finalizam comanda
            si sa printam pentru a genera output-ul
            """
            for product in self.marketplace.place_order(new_cart_id):
                print(self.name + " bought " + str(product))

