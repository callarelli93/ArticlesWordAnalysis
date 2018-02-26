#RUN CODE WITH PYTHON 2 INTERPRETER!!

from bs4 import BeautifulSoup
import string
import inflect
from collections import Counter
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import operator

class Articles:

    def __init__(self, markup_file):

        """
        :param markup_file: path to file containing markup language
        :param articles: before processed() is called == list of articles in markup language
                         after processed() is called == concatenated lists of words in each article
        :param is_processed: bool to assert if articles have been processed
        :param Word_Freq_PA: dictionary where key=word, value=list of list-pairs [article no, word_frequency]
        :param Word_Freq_TOT: dictionary where key=word, value=word frequency across all articles
        """

        self.articles =[element for element in BeautifulSoup(open(markup_file, 'r').read(), 'html.parser').find_all('doc')]
        self.is_processed = False
        self.Word_Freq_PA = {}
        self.Word_Freq_TOT = {}


    #Method to process articles in markup language and
    def process(self):

        #Exclude markup text
        self.articles = [str(article.get_text()) for article in self.articles]

        #Low-cap
        self.articles = [article.lower() for article in self.articles]

        #Strip punctuation
        self.articles = [article.translate(None, string.punctuation) for article in self.articles]

        #Strip numbers
        self.articles = [article.translate(None, '1234567890') for article in self.articles]

        #Split into words-list
        self.articles = [article.split() for article in self.articles]

        #Handle-plurals
        p = inflect.engine()
        articles_words = []
        for article in self.articles:
            words = []
            for word in article:
                if p.singular_noun(word) is not False:
                    words.append(p.singular_noun(word))
                else:
                    words.append(word)
            articles_words.append(words)

        self.articles = articles_words
        print 'Articles processed'
        self.is_processed = True



    #Method to initialize Word_Freq_PA
    def create_word_freq_PA(self):
        if self.is_processed is False:
            print 'Articles have not been processed, please process articles first!'
            exit()
        else:
            word_count = [Counter(article) for article in self.articles]
            freq_table_PA = {}


            for i in range(len(word_count)):
                if i == 0:
                    for key in word_count[0]:
                        a = {}
                        a.setdefault(key, []).append([1, word_count[0][key]])
                        freq_table_PA.update(a)
                else:
                    for key in word_count[i]:
                        #If key already in dictionary, append another list
                        if key in freq_table_PA:
                            freq_table_PA[key].append([i+1, word_count[i][key]])
                        #If key not in the dictionary, update the dictionary
                        else:
                            freq_table_PA.update({key : [[i+1, word_count[i][key]]]})

            self.Word_Freq_PA = freq_table_PA



    #Method to initialize Word_Freq_TOT
    def create_word_freq_TOT(self):
        if self.is_processed is False:
            print 'Articles have not been processed, please process articles first!'
            exit()
        else:
            word_count = [Counter(article) for article in self.articles]
            freq_table_tot = {}

            for i in range(len(word_count)):
                if i == 0:
                    freq_table_tot.update(word_count[0])
                else:
                    for key in word_count[i]:
                        if key in freq_table_tot:
                            freq_table_tot[key] = freq_table_tot[key] + word_count[i][key]
                        else:
                            freq_table_tot.update({key: word_count[i][key]})



            self.Word_Freq_TOT = freq_table_tot



def powlaw(x, a, b):
    return a * pow(x, b)

#Plot data on log-log scale and a histogram with a power-law fitted to the data
def plot_word_freq(word_freq_table):

    sorted_table = sorted(word_freq_table.values())
    count_table = Counter(sorted_table)
    width = 1.0

    #Data on a log-log scale
    plt.figure(1)
    plt.plot(count_table.keys(), count_table.values(), 'bs')
    plt.title('Data on log/log scale')
    plt.xlabel('Count')
    plt.ylabel('Count Frequency')
    plt.xscale('log')
    plt.yscale('log')
    #Fit a power law
    xvals = np.linspace(1, 50, 100)
    popt, pcov = curve_fit(powlaw, count_table.keys(), count_table.values())
    yvals = powlaw(xvals, popt[0], popt[1])
    plt.plot(xvals, yvals, 'k--', label='Linear relationship on a \nlog/log scale suggests \na power law')
    plt.ylim([1, 1000])
    plt.legend()

    #Data displayed on a histogram with a power-law fitted
    plt.figure(2)
    ax = plt.axes()
    ax.set_xticks(count_table.keys())
    ax.set_xticklabels(count_table.keys())
    adjusted_bins = [item - width/2 for item in count_table.keys()]
    plt.bar(adjusted_bins, count_table.values(), width=width, color='g')
    plt.xlim([0,20])
    plt.xlabel('Count')
    plt.ylabel('Count Frequency')
    # Fit a power law
    xvals = np.linspace(1, 50, 100)
    popt, pcov = curve_fit(powlaw, count_table.keys(), count_table.values())
    yvals = powlaw(xvals, popt[0], popt[1])
    plt.plot(xvals, yvals, 'k--', label='fit: $y = a x ^{b}$ \n $a = %5.3f$ \n $b = %5.3f$' % tuple(popt))
    plt.legend()
    plt.title('Histogram with data fitted to a power law')
    plt.show()



if __name__ == '__main__':

    PATH_TO_FILE = '/insert/path/to/html/file/filename.txt'

    LA_articles = Articles('text.rtf')
    LA_articles.process()
    LA_articles.create_word_freq_PA()
    LA_articles.create_word_freq_TOT()

    word_frequency_per_article = LA_articles.Word_Freq_PA
    total_word_frequency = LA_articles.Word_Freq_TOT


    # Print output in format: "word" -> [article number, number of appearences] -> etc...
    sorted_total_word_frequency = sorted(total_word_frequency.items(), key=operator.itemgetter(1), reverse=True)
    sorted_word_frequency_per_article = [(item[0], word_frequency_per_article[item[0]]) for item in sorted_total_word_frequency]
    for i in range(len(sorted_word_frequency_per_article)):
        string = ''
        for j in sorted_word_frequency_per_article[i][1]:
            string += '->' + str(j)
        print sorted_word_frequency_per_article[i][0], string


    #Figure(1): Data on log-log scale
    #Figure(2): A histogram with a power-law fitted to the data
    plot_word_freq(total_word_frequency)



