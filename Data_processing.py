import sqlite3
import urllib.request
import urllib.error
from db import insert
from matching_process import match
from consecutive_analysis import find_consecutive

"""extracts the mishnayot and the citations"""
def process_talmud_page(url):
    mishnayot = []  
    citations = []
    mishna = ""
    citation = ""
    daf = ""
    
    # Fetch data
    try:
        raw_data = urllib.request.urlopen(url).read().decode('utf-8')
    except urllib.error.URLError as e:
        print(f"Error accessing URL: {e}")
        return
    
    mishna_start = False
    found_dot = False
    gemara = False
    index1 = 0
    index2 = 0
    
    for line in raw_data.split('\n'):
        # Extract daf number
        if "Daf" in line:
            daf = line.split(' ')[1]
            citation=""
            found_dot=False
            continue
        
        # Finds gemara mark    
        if "<big><strong>גמ׳</strong></big>" in line:
            mishna_start = False
            gemara = True
            start_mark = line.index("<big><strong>גמ׳</strong></big>") + len("<big><strong>גמ׳</strong></big>")
            if ":" in line[start_mark:]:
                dot_mark = line.index(":", start_mark)
                citation += line[dot_mark+1:].strip() + "\n"
                found_dot = True
            continue
        
        if gemara and not (line.strip().startswith("<big><strong>מתני׳</strong></big>") or line.strip().startswith("מתני׳ <big><strong>") or line.strip().startswith("<big><strong>מתני'</strong></big>")): 
            if found_dot:
                if ":" in line:
                    end = line.index(":")
                    citation += line[:end].strip() + "\n" 
                    index1 += 1
                    insert('citations', index1, daf, citation)
                    citations.append({"index": index1, "daf": daf, "citation": citation})
                    citation = ""
                    found_dot = False
                    
                    remaining = line[end+1:].strip()
                    if ":" in remaining and "מתני׳" not in remaining:
                        next_colon = remaining.index(":")
                        citation += remaining[next_colon+1:].strip() + "\n"
                        found_dot = True
                else:
                    citation += line.strip() + '\n'
            else:
                if ":" in line and "מתני׳" not in line:
                    found_dot = True
                    start = line.index(":")
                    if line.strip().endswith(":"):
                        continue
                    else:
                       citation += line[start+1:].strip() + "\n" 
        
        # Extract mishna
        if "<big><strong>מתני׳</strong></big>" in line or "מתני׳ <big><strong>" in line or "<big><strong>מתני'</strong></big>" in line :
            gemara = False
            found_dot = False
            citation = ""
            if "<big><strong>מתני׳</strong></big>" in line:
                start = line.index("<big><strong>מתני׳</strong></big>") + len("<big><strong>מתני׳</strong></big>")
            else:
                start = line.index("</strong></big>") + len("</strong></big>")
            
            remaining_text = line[start:].strip()
            if ":" in remaining_text:
                end = remaining_text.index(":")
                mishna += remaining_text[:end] + "\n"
                index2 += 1
                insert('mishnayot', index2, daf, mishna)
                mishnayot.append({"index": index2, "daf": daf, "mishna": mishna})
                mishna = ""
            else:
                mishna_start = True
                mishna += remaining_text + "\n"
            continue
        
        if mishna_start:
            if ":" in line:
                mishna_start = False
                end = line.index(":")
                mishna += line[:end] + "\n"
                index2 += 1
                insert('mishnayot', index2, daf, mishna)
                mishnayot.append({"index": index2, "daf": daf, "mishna": mishna})
                mishna = ""
            else:
                mishna += line.strip() + '\n'
    
    return mishnayot, citations

"""Counts for each mishna how many times we found it in the gemara"""
def count_citations_per_mishna():
    conn = sqlite3.connect('mishnayot.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT mishna_daf, COUNT(*) as citation_count
        FROM matched
        GROUP BY mishna_daf
        ORDER BY mishna_daf
    """)
    results = cursor.fetchall()
    for mishna_daf, count in results:
        print(f"Mishna {mishna_daf}: {count} citations")


if __name__ == "__main__":
    url = input("Please enter the url\n")
    mishnayot, citations = process_talmud_page(url)
    match()
    print(f"Processing complete! Inserted {len(mishnayot)} mishnayot and {len(citations)} citations")
    count_citations_per_mishna()
    find_consecutive()
   
         
  

                    