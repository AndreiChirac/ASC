"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import os
import threading
import time
import logging
from logging.handlers import RotatingFileHandler
from .product import Tea, Coffee

filename = "marketplace.log"
logging.basicConfig(filename=filename,
                    format='%(asctime)s %(message)s',
                    filemode='w')

logging.Formatter.converter = time.gmtime
logger = logging.getLogger('marketplace_loger')

should_roll_over = os.path.isfile(filename)
handler = logging.handlers.RotatingFileHandler(filename, 
mode = 'w', backupCount = 10)
if should_roll_over:  # log already exists, roll over!
    handler.doRollover()

# Now we are going to Set the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    """
    metoda care verifica daca un produs este disponibil in magazin si returneaza produsul dorit
    """

    def check_item_market(self, product):
        logger.info("In check_item " + str(product))
        for product_complex in self.marketplace_products:
            if product == product_complex[0]:
                logger.info("Out check_item")
                return product_complex
        logger.info("Out check_item")
        return None

    """
    metoda care verifica daca un produs se afla in cosul cu cart_id si returneaza produsul dorit
    """

    def check_item_cart(self, product, cart_id):
        logger.info("In check_item_cart " + str(product) + " " + str(cart_id))
        for product_complex in self.cart[cart_id]:
            if product == product_complex[0]:
                logger.info("Out check_item_cart")
                return product_complex
        logger.info("Out check_item_cart")
        return None

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """

        """
        capacitatea maxima de produse pe care le poate avea un producator simultan 
        """
        self.queue_size_per_producer = queue_size_per_producer

        # lista cu toate produsele disponibilie (prod id, produs)
        self.marketplace_products = []

        # lista cu fiecare produs furnizat de un producator cu id ul x
        self.producers_list = {}
        self.mr_of_producers = 0

        # dictionar cu toate cosurile din magazin
        self.cart = {}
        self.nr_of_carts = 0

        self.lock = threading.Lock()

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        logger.info("In register_producer")
        """
        deoarece folosim o variabila care trebuie incrementata vom avea nevoie de un lock pentru ca un thread
        sa nu citeasca o valoare veche
        """
        with self.lock:
            self.producers_list[self.mr_of_producers] = []
            self.mr_of_producers = self.mr_of_producers + 1
            logger.info("Out register_producer")
            return self.mr_of_producers - 1

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        logger.info("In publish " + producer_id + " " + str(product))
        if len(self.producers_list[int(producer_id)]) >= self.queue_size_per_producer:
            logger.info("Out publish")
            return False

        self.producers_list[int(producer_id)].append(product)
        self.marketplace_products.append((product, int(producer_id)))
        logger.info("Out publish")
        return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        """
        deoarece folosim o variabila care trebuie incrementata vom avea nevoie de un lock pentru ca un thread
        sa nu citeasca o valoare veche
        """
        logger.info("In new_cart")
        with self.lock:
            self.cart[self.nr_of_carts] = []
            self.nr_of_carts = self.nr_of_carts + 1
            logger.info("Out new_cart")
            return self.nr_of_carts - 1

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        logger.info("In add_to_cart " + str(cart_id) + " " + str(product))
        """
        lock-ul este folostit deoare in momentul in care un cumparator vrea sa adauge in cos acel produs sa fie blocat
        astfel astfel incat sa nu poata exista un alt thread care sa fure produsul
        """
        with self.lock:
            item = self.check_item_market(product)
            if item is not None:
                self.cart[cart_id].append(item)
                self.marketplace_products.remove(item)
                logger.info("Out add_to_cart")
                return True
            else:
                logger.info("Out add_to_cart")
                return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        logger.info("In remove_from_cart " + str(cart_id) + " " + str(product))
        item = self.check_item_cart(product, cart_id)
        """
        nu avem nevoie de lock pe intreaga operatie deoarece fiecare thread are cart_id-ul lui iar metoda de append este
        thread safe (https://stackoverflow.com/questions/6319207/are-lists-thread-safe)
        """
        if item is not None:
            self.cart[cart_id].remove(item)
            self.marketplace_products.append(item)
            logger.info("Out remove_from_cart")

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        logger.info("In place_order " + str(cart_id))
        """
        nu avem nevoie de lock pe intreaga operatie deoarece fiecare thread are cart_id-ul lui
        """
        product_list = []
        for product_extended in self.cart[cart_id]:
            product = product_extended[0]
            producer_id = product_extended[1]
            self.producers_list[producer_id].remove(product)
            product_list.append(product)
        logger.info("Out place_order")
        return product_list

