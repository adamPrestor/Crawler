import sqlite3

DB_NAME = 'inverted_index.db'

def insert_index(document, word_list, frequencies, indexes):
    """ Inserts inverted index entries for a single document. """

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Insert new words into word list
    words_vals = [(w,) for w in word_list]
    insert_word_q = "INSERT OR IGNORE INTO IndexWord VALUES (?)"
    cur.executemany(insert_word_q, words_vals)

    # Add inverted index entries
    entries = []
    for word in word_list:
        freqs = frequencies[word]
        inds = ','.join(str(i) for i in indexes[word])

        entries.append((word, document, freqs, inds))
    insert_index_q = "INSERT INTO Posting VALUES (?,?,?,?)"
    cur.executemany(insert_index_q, entries)

    conn.commit()
    conn.close()

