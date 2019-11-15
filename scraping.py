from selenium import webdriver
from selenium.common import exceptions as sel_exceptions
import logging
import pandas as pd
import threading
import queue


logging.basicConfig(filename="scraping2.log", level=logging.INFO,
                    format="%(asctime)s:%(levelname)s:%(message)s")
data = []

def article_reader(driver, page_counter):
    global data
    # Per article
    norms = driver.find_element_by_xpath(f'//*[@id="p_div_aba1_resultado"]/table[2]/tbody/tr[{page_counter}]/td[3]/table')
    labels = [x.text for x in norms.find_elements_by_class_name("td_ficha_esq.direita")]
    classes = [x.text for x in norms.find_elements_by_class_name("td_ficha_dir.esquerda")]
    info = {label: class_data for label, class_data in zip(labels, classes)}
    if len(labels) != len(classes):
        logging.warning(f"Sizes are different! For label: {len(labels)}. For classes: {len(classes)}")
    data.append(info)


def page_reader(counter, x, driver, pages):
    # Per Page
    page_counter = 2
    while True:
        try:
            article_reader(driver, page_counter)
            page_counter += 1
        except sel_exceptions.NoSuchElementException:
            logging.info(f"Number: {counter}. Pages: {x+1}/{pages} ({((x+1)/pages * 100):.2f}%). Articles: {page_counter-2}")
            break


def number_reader(counter, driver):
    global data
    # Per Number
    driver.find_element_by_xpath('//*[@id="div_leg"]/table/tbody/tr[2]/td[2]/input[2]').click()
    driver.find_element_by_name("leg_numero").send_keys(counter)
    driver.find_elements_by_name("bt_comb")[1].click()
    logging.info(f"NUMBER {counter}")

    try:
        while driver.find_elements_by_class_name("td_facetas")[0].text.count("Carregando..."):
            pass
    except sel_exceptions.StaleElementReferenceException:
        pass
    except IndexError:
        pass

    try:
        pages = driver.find_element_by_xpath('//*[@id="p_div_aba1_resultado"]/table[1]/tbody/tr/td/b[2]').text
        pages = int(pages)
    except sel_exceptions.NoSuchElementException as err:
        logging.info(f"END at number: {counter}. Dataset size: {len(data)}")
        raise err

    for x in range(pages):
        page_reader(counter, x, driver, pages)
        if x < pages - 1:
            if pages > 5:
                driver.find_element_by_xpath('//*[@id="p_div_aba1_resultado"]/table[1]/tbody/tr/td/span[3]').click()
            else:
                driver.find_element_by_xpath(f'//*[@id="p_div_aba1_resultado"]/table[1]/tbody/tr/td/a[{x+2}]').click()

    logging.info(f"FINISHED {counter}. Pages: {pages}. Dataset size: {len(data)}")


class SeleniumThread(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.driver = None
        self.init_reader()
        self.q = q

    def init_reader(self):
        self.driver = webdriver.Chrome()
        self.driver.get("http://biblioteca.aneel.gov.br/index.html")
        self.driver.switch_to.frame("mainFrame")
        self.driver.find_element_by_name("lk_legis").click()

    def run(self):
        global data
        counter = ""
        while True:
            try:
                if self.q.empty():
                    self.kill()
                    break
                counter = self.q.get()
                number_reader(counter=counter, driver=self.driver)
            except sel_exceptions.NoSuchElementException:
                self.kill()
                break
            except Exception as err:
                logging.critical("SCRAPING HAS FAILED")
                logging.critical(err)
                try:
                    df = pd.DataFrame(data)
                    df.to_csv("scraping_completed" + str(counter) + ".csv", encoding="utf-8")
                except:
                    with open("wrong" + str(counter), 'w') as wf:
                        wf.write("[")
                        for x in data:
                            wf.write("{")
                            for i, j in x.items():
                                wf.write(f'"""{i}""":"""{j}""",')
                            wf.write("}")
                        wf.write("]")
                self.kill()
                self.init_reader()
                self.run()
                break

    def kill(self):
        self.driver.quit()


if __name__ == "__main__":
    work = queue.Queue(5000)
    for i in range(1, 5001):
        work.put(i)
    thread_list = []
    for _ in range(5):
        thread = SeleniumThread(work)
        thread_list.append(thread)
        thread.start()
    for x in thread_list:
        x.join()

    df = pd.DataFrame(data)
    df.to_csv("scraping_final_v4.csv", encoding="utf-8")
    logging.info("CONCLUDED")
