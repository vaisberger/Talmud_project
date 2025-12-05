import urllib.request
import urllib.error

mishnayot = []  
citations = []
mishna=""
citation=""
raw_data=""
daf=""
url=input("Please enter the url\n")
try:
    raw_data=urllib.request.urlopen(url).read().decode('utf-8')
except urllib.error.URLError as e:
    print("Error accessing URL")

mishna_start=False
found_dot=False
daf_s=False
gemara=False
index1=0
index2=0
lineS=0
lineE=0
for line in raw_data.split('\n'):
   if "Daf" in line:
       daf_s=True
       daf=line.split(' ')[1]
       continue
#extract citation    
   if "<big><strong>גמ׳</strong></big>" in line:
      mishna_start=False
      gemara=True
      start_mark=line.index("<big><strong>גמ׳</strong></big>")+len("<big><strong>גמ׳</strong></big>")
      if ":" in line[start_mark:]:
         dot_mark=line.index(":", start_mark)
         citation += line[dot_mark+1:].strip() + "\n"
         found_dot=True
      continue
   if gemara: 
     if found_dot:
        if ":" in line:
          end=line.index(":")
          citation += line[:end].strip() + "\n" 
          index1 += 1
          citations.append({"index": index1, "daf": daf, "citation": citation})
          citation = ""
          found_dot = False

          remaining = line[end+1:].strip()
          if ":" in remaining and "מתני׳" not in remaining:
                next_colon = remaining.index(":")
                citation += remaining[next_colon+1:].strip() + "\n"
                found_dot = True
        else:
         citation+=line.strip()+'\n'
     else:
        if ":" in line and "מתני׳" not in line:
           found_dot=True
           start=line.index(":")
           citation += line[start+1:].strip() + "\n" 
      
#extract mishna
   
   if "<big><strong>מתני׳</strong></big>"in line or "מתני׳ <big><strong>" in line:
       gemara=False
       if "<big><strong>מתני׳</strong></big>" in line:
         start=line.index("<big><strong>מתני׳</strong></big>")+len("<big><strong>מתני׳</strong></big>")
       else:
         start=line.index("</strong></big>")+len("</strong></big>")
       remaining_text= line[start:].strip()
       if ":" in remaining_text:
          end = remaining_text.index(":")
          mishna += remaining_text[:end] + "\n"
          index2 += 1
          mishnayot.append({"index": index2, "daf": daf, "mishna": mishna})
          mishna = ""
       else:
          mishna_start = True
          mishna += remaining_text + "\n"
       continue
   
   if mishna_start:
       if ":" in line:
         mishna_start=False
         end=line.index(":")
         mishna+=line[:end]+"\n"
         index2+=1
         mishnayot.append({"index":{index2},"daf":{daf},"mishna":{mishna}})
         mishna=""
       else:
          mishna += line.strip() + '\n'

print("all done")

   
         
  

                    