import sqlite3
from db import insert_match

"""Function that does the comparation using the algorithem longest_common_substring"""
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
"""Function that calculates how similar two texts are based on shared words"""
def token_overlap_score(citation, mishna): 
  citation_tokens = set(citation.split()) 
  mishna_tokens = set(mishna.split()) 
  overlap = citation_tokens & mishna_tokens 
  return len(overlap) / len(citation_tokens)

def match():
  conn = sqlite3.connect('mishnayot.db')
  cursor = conn.cursor()

  def get_all_mishnayot():
    cursor.execute("SELECT id, masechet, daf, mishna FROM mishnayot")
    return cursor.fetchall()

  def get_all_citations():
    cursor.execute("SELECT id, masechet, daf, citation FROM citations")
    return cursor.fetchall()

  mishnayot=get_all_mishnayot()
  citations=get_all_citations()
  index=0
  matched_count = 0
  
  # For each citation matches it's mishna
  for citation_id, masechet_c, citation_daf, citation_text in citations: 
       citation=' '.join(citation_text.split())
       for mishna_id, masechet_m, mishna_daf, mishna_text in mishnayot:
         mishna=' '.join(mishna_text.split())
         if masechet_m==masechet_c:
          sub_s=longest_common_substring(mishna,citation,2)
          token_score=token_overlap_score(citation,mishna)
          if sub_s >= 2 and token_score > 0.5: 
            index+=1
            matched_count+=1
            insert_match(index,masechet_c,mishna_daf,citation_id,citation_daf)
            break
            
  print(f"\nTotal matches: {matched_count} out of {len(citations)} citations")
  conn.close()

          