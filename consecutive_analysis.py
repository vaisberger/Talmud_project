import sqlite3
from matching_process import longest_common_substring

"""comparing 2 consecutive citations with few tests"""
def check_similar_citations(text1, text2):
        t1 = text1.strip()
        t2 = text2.strip()
        # their equal
        if t1 == t2:
          return True
         
        # Removes וכו' 
        if t1.endswith('וכו'):
          t1 = t1[:-3].strip()  

        if t2.endswith('וכו'):
          t2 = t2[:-3].strip() 
        
        # one contains the other
        if t1 in t2 or t2 in t1:
           longer = max(len(t1), len(t2))
           shorter = min(len(t1), len(t2))

        # if length difference is small (within 20%)
           if shorter / longer >= 0.8:
              return True

        return False

def find_consecutive():

    conn = sqlite3.connect('mishnayot.db')
    cursor = conn.cursor()
    
    # Get all matched citations for mishnayot that have 2+ citations
    cursor.execute("""
    SELECT m.mishna_daf, m.citation_id, m.citation_daf, c.citation
    FROM matched m
    JOIN citations c ON m.citation_id = c.id
    WHERE m.mishna_daf IN (
        SELECT mishna_daf 
        FROM matched 
        GROUP BY mishna_daf 
        HAVING COUNT(*) > 1
    )
    ORDER BY m.citation_id
    """)
    rows = cursor.fetchall()

    found_consecutive = []
    curr=[]

    for i, (mishna, cit_id, cit_daf, citation_text) in enumerate(rows):
        if i==0:
            curr.append((mishna,citation_text,cit_daf))
        else:
            prev_mishna,prev_id,prev_cit_daf,prev_text= rows[i-1]
            if prev_mishna==mishna and prev_id+1==cit_id and check_similar_citations(prev_text,citation_text):
                curr.append((mishna,citation_text,cit_daf))
            else:
                if len(curr)>=2:
                    found_consecutive.append(curr)
                curr=[(mishna, citation_text, cit_daf)]
    if len(curr)>=2:
        found_consecutive.append(curr)

    for i in found_consecutive:
        print(i)
    print(f"found {len(found_consecutive)} instances where a Mishna is cited consecutively in Bava Batra")