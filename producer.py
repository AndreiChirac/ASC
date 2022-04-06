"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
import time


class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available
s
        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.id = None
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        self.id = self.marketplace.register_producer()

    def run(self):
        while 1:
            for product_process in self.products:
                """
                product_process este format din product numarul de produse pe care urmam sa le producem si timpul
                de asteptare intre doua produse
                """
                product = product_process[0]
                product_nr = product_process[1]
                product_cnt = 0
                product_wait_time = product_process[2]

                while True:
                    """
                    in cazul in care s-a produs deja cantitatea dorita fom dori trecerea la urmatorul produs
                    """
                    if product_cnt >= product_nr:
                        break
                    """
                    in cazul in care publish intoarce true inseamna ca publicarea s-a realizat cu succes asa ca putem
                    incrementa numaurl de produse create si trebuie sa asteptam intervalul de timp in caz contrat se
                    va astepta pana cand marketplace-ul devine disponibil
                    """
                    if self.marketplace.publish(str(self.id), product):
                        product_cnt += 1
                        time.sleep(product_wait_time)
                    else:
                        time.sleep(self.republish_wait_time)




