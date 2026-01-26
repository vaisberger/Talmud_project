import re

def strip_mishna_marker(line: str) -> str:
    for marker in (
        "<big><strong>מתני׳</strong></big>",
        "מתני׳ <big><strong>",
        "<big><strong>מתני'</strong></big>",
    ):
        if line.startswith(marker):
            return line[len(marker):].strip()
    return line.strip()


def extract_mishnayot_and_citations(text: str):
    mishnayot = []
    citations = []
    daf="1a"
    masechet=""
    lines = text.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("Daf"):
           daf=line[len("Daf"):]
        if i==0:
           masechet=line.strip()

        # -------------------
        # MISHNA EXTRACTION
        # -------------------
        if (
            line.startswith("<big><strong>מתני׳</strong></big>") or
            line.startswith("מתני׳ <big><strong>") or
            line.startswith("<big><strong>מתני'</strong></big>")
        ):
               # REMOVE the marker from the first line
            first_line = strip_mishna_marker(line)
            mishna_lines = [first_line] if first_line else []
            
            colon_found = ":" in line
            j = i + 1

            while not colon_found and j < len(lines):
                mishna_lines.append(lines[j])
                if ":" in lines[j]:
                    colon_found = True
                j += 1

            full_text = " ".join(mishna_lines)
            first_colon_index = full_text.find(":")
            if first_colon_index != -1:
                mishnayot.append({"text":full_text[:first_colon_index].strip(),"daf":daf})

            i = j
            continue

        # -------------------
        # GEMARA + CITATIONS
        # -------------------
        if line.startswith("<big><strong>גמ׳</strong></big>"):
            gemara_lines = []
            j = i + 1

            while j < len(lines):
                next_line = lines[j].strip()
                if (
                    next_line.startswith("<big><strong>מתני׳</strong></big>") or
                    next_line.startswith("מתני׳ <big><strong>") or
                    next_line.startswith("<big><strong>מתני'</strong></big>")
                ):
                    break
                gemara_lines.append(lines[j])
                j += 1

            gemara_text = "\n".join(gemara_lines)

            # -------- FIXED CITATION PARSER (STATE MACHINE) --------
            inside_citation = False
            current = []
            paren_level = 0
            skip_next_colon = False
            k = 0
            length = len(gemara_text)

            while k < length:
                char = gemara_text[k]
                if gemara_text.startswith("Daf", k) and (k == 0 or gemara_text[k-1] == "\n"):
                   # extract full daf line
                   end = gemara_text.find("\n", k)
                   if end == -1:
                     end = length
                   daf = gemara_text[k+3:end].strip()  # skip "Daf"
                   k = end + 1
                   inside_citation = False
                   current = []
                   continue
                # Track parentheses
                if char == "(":
                    paren_level += 1
                elif char == ")":
                    if paren_level > 0:
                        paren_level -= 1

                # Handle chapter-end markers
                if gemara_text.startswith("<strong>הדרן עלך", k):
                    skip_next_colon = True
                    k += len("<strong>הדרן עלך")
                    continue

                # Handle Daf boundaries (abandon ongoing citations)
                if gemara_text.startswith("Daf", k) and (k == 0 or gemara_text[k-1] == "\n"):
                    inside_citation = False
                    current = []
                    next_newline = gemara_text.find("\n", k)
                    if next_newline == -1:
                        break
                    k = next_newline + 1
                    continue

                # Handle colons
                if char == ":":
                    if skip_next_colon:
                        skip_next_colon = False
                        k += 1
                        continue

                    # Start citation only if not inside parentheses
                    if not inside_citation and paren_level == 0:
                        inside_citation = True
                        current = []
                    # End citation anywhere
                    elif inside_citation:
                        citation = "".join(current).strip()
                        if citation:
                            citation = "\n".join(line.strip() for line in citation.splitlines())
                            citations.append({"text":citation,"daf": daf})
                        inside_citation = False
                        current = []

                    k += 1
                    continue

                # Add characters to current citation
                if inside_citation:
                    current.append(char)

                k += 1

            # Close citation if Gemara ends while inside one
            if inside_citation:
                citation = "".join(current).strip()
                if citation:
                    citation = "\n".join(line.strip() for line in citation.splitlines())
                    citations.append({"text":citation,"daf": daf})

            i = j
            continue

        i += 1

    return mishnayot, citations, masechet

