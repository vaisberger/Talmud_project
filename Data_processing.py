import urllib.request
import urllib.error
from db import insert
from matching_process import match
from consecutive_analysis import find_consecutive
import os
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
    found_colon  = False
    gemara = False
    index1 = 0
    index2 = 0
    lines = raw_data.split('\n')
    masechet= lines[0].strip()
    
    for line in lines:
        # Extract daf number
        if "Daf" in line:
            daf = line.split(' ')[1]
            citation=""
            found_colon =False
            continue
        
        # Finds gemara mark    
        if "<big><strong>גמ׳</strong></big>" in line:
            mishna_start = False
            gemara = True
            start_mark = line.index("<big><strong>גמ׳</strong></big>") + len("<big><strong>גמ׳</strong></big>")
            if ":" in line[start_mark:]:
                dot_mark = line.index(":", start_mark)
                citation += line[dot_mark+1:].strip() + "\n"
                found_colon  = True
            continue
       
        
        if gemara and not (line.strip().startswith("<big><strong>מתני׳</strong></big>") 
                           or line.strip().startswith("מתני׳ <big><strong>") 
                           or line.strip().startswith("<big><strong>מתני'</strong></big>")): 
            if "<strong>הדרן עלך" in line.strip():
                found_colon =False 
            if not found_colon :
              if ":" in line and "מתני׳" not in line:
                start = line.index(":")
            
              # Start extracting citation
                found_colon  = True
                remaining = line[start+1:].strip()

             # Check if citation also ENDS on same line
                if ":" in remaining:
                   if found_colon :
                    end = remaining.index(":")
                    citation = remaining[:end].strip() + "\n"
                    index1 += 1
                    insert(masechet, 'citations', index1, daf, citation)
                    citations.append({"index": index1, "daf": daf, "citation": citation})
                    citation = ""
                    found_colon  = False
                   endofline=remaining[end+1:]
                   # if there is another ":" in the end 
                   if endofline.count(":")==1:
                     found_colon  = True
                     end= endofline.index(":")
                     citation+= endofline[end+1:]
                else: 
                   citation+=remaining
                   
                   
            else:
              if ":" in line:
                end = line.index(":")
                citation += line[:end].strip() + "\n"
                index1 += 1
                insert(masechet, 'citations', index1, daf, citation)
                citations.append({"index": index1, "daf": daf, "citation": citation})
                citation = ""
                found_colon  = False
            
                # Check if a NEW citation starts on the same line
                remaining = line[end+1:].strip()
                if ":" in remaining and "מתני׳" not in remaining:
                  next_start = remaining.index(":")
                  citation += remaining[next_start+1:].strip() + "\n"
                  found_colon  = True
                
                 # Check if this new citation ALSO ends on same line
                  after_start = remaining[next_start+1:]
                  if ":" in after_start:
                    next_end = after_start.index(":")
                    citation = after_start[:next_end].strip() + "\n"
                    index1 += 1
                    insert(masechet, 'citations', index1, daf, citation)
                    citations.append({"index": index1, "daf": daf, "citation": citation})
                    citation = ""
                    found_colon  = False
                    if ":" in after_start[next_end+1:] and ":)" not in after_start[next_end+1:]:
                       found_colon =True
              else:
                   # Continue building the citation
                 citation += line.strip() + '\n'
        

        # Extract mishna
        if "<big><strong>מתני׳</strong></big>" in line or "מתני׳ <big><strong>" in line or "<big><strong>מתני'</strong></big>" in line :
            gemara = False
            found_colon  = False
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
                insert(masechet,'mishnayot', index2, daf, mishna)
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
                insert(masechet,'mishnayot', index2, daf, mishna)
                mishnayot.append({"index": index2, "daf": daf, "mishna": mishna})
                mishna = ""
            else:
                mishna += line.strip() + '\n'

    print(f"{masechet}")
    return mishnayot, citations

if __name__ == "__main__":
    url = input("Please enter the url\n")
    mishnayot, citations = process_talmud_page(url)
    match()
    find_consecutive()

   
 
         
  

                    