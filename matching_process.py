import sqlite3
from db import insert_match

"""function that does the comparation using the algorithem longest_common_substring"""
def longest_common_substring(mishna, citation,stop):
      mishna_words = mishna.split() 
      citation_words = citation.split() 
      res=0
      for i in range(len(citation_words)):
         for j in range(len(mishna_words)):
            curr = 0
            while (i + curr) < len(citation_words) and (j + curr) < len(mishna_words) and citation_words[i + curr] == mishna_words[j + curr]:
               curr+=1
               if curr >= stop:  
                    return curr
            res = max(res, curr)
      return res


def match():
  conn = sqlite3.connect('mishnayot.db')
  cursor = conn.cursor()

  def get_all_mishnayot():
    cursor.execute("SELECT id, daf, mishna FROM mishnayot")
    return cursor.fetchall()

  def get_all_citations():
    cursor.execute("SELECT id, daf, citation FROM citations")
    return cursor.fetchall()

  mishnayot=get_all_mishnayot()
  citations=get_all_citations()
  index=0
  matched_count = 0
  for citation_id, citation_daf, citation_text in citations:  
       citation=' '.join(citation_text.split())
       for mishna_id, mishna_daf, mishna_text in mishnayot:
         mishna=' '.join(mishna_text.split())
         sub_s=longest_common_substring(mishna,citation,2)
         if sub_s >= 2: 
            index+=1
            matched_count+=1
            insert_match(index,mishna_daf,citation_id,citation_daf)
            break
            
  print(f"\nTotal matches: {matched_count} out of {len(citations)} citations")
  conn.close()

          