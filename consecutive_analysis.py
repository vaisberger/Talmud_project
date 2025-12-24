import sqlite3
from matching_process import longest_common_substring
import Levenshtein
"""comparing 2 consecutive citations with few tests"""
def check_similar_citations(text1, text2):
        t1 = text1.strip()
        t2 = text2.strip()
        # their equal
        if t1 == t2:
          return True
         
        # Removes וכו' 
        if t1.endswith("וכו'"):
          t1 = t1[:-4].strip()  

        if t2.endswith("וכו'"):
          t2 = t2[:-4].strip()
        
        # one contains the other
        if t1 in t2 or t2 in t1:
           longer = max(len(t1), len(t2))
           shorter = min(len(t1), len(t2))

        # if length difference is small (within 40%)
           if shorter / longer >= 0.6:
              return True

        return False

"""comparing 2 consecutive citations using levenshtein distance"""
def levenshtein_dis(text_1,text_2):
 t1 = text_1.strip()
 t2 = text_2.strip()
 distance = Levenshtein.distance(t1, t2)
 if distance <= 1:
    print(f"Match found! Distance: {distance}")
    return True
 if t1 in t2 or t2 in t1:
       return True
 return False


def find_consecutive():

    conn = sqlite3.connect('mishnayot.db')
    cursor = conn.cursor()
    
    # Get all matched citations for mishnayot that have 2+ citations
    cursor.execute("""
      SELECT m.masechet, m.mishna_daf, m.citation_id, m.citation_daf, c.citation
      FROM matched m
      JOIN citations c ON m.citation_id = c.id AND m.masechet = c.masechet
      WHERE (m.masechet, m.mishna_daf) IN (
        SELECT masechet, mishna_daf 
        FROM matched 
        GROUP BY masechet, mishna_daf 
        HAVING COUNT(*) > 1
     )
     ORDER BY m.masechet, m.citation_id
    """)
    rows = cursor.fetchall()

    found_consecutive = []
    curr=[]
    
    #For each consecutive citations finds the ones that are the same 
    for i, (masechet,mishna, cit_id, cit_daf, citation_text) in enumerate(rows):
        if i==0:
            curr.append((mishna,citation_text,cit_daf))
        else:
          if masechet==rows[i-1][0]:
            prev_masechet,prev_mishna,prev_id,prev_cit_daf,prev_text= rows[i-1]  
            if prev_masechet==masechet and prev_id+1==cit_id and check_similar_citations(prev_text,citation_text): #and check_similar_citations(prev_text,citation_text):
                curr.append((masechet,mishna,citation_text,cit_daf))
            else:
                if len(curr)>=2:
                    found_consecutive.append(curr)
                curr=[(masechet,mishna, citation_text, cit_daf)]
    if len(curr)>=2:
        found_consecutive.append(curr)

    for i in found_consecutive:
        print(i)
    print(f"found {len(found_consecutive)} instances where a Mishna is cited consecutively in the shas")