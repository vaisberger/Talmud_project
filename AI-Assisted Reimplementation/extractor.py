import re

def extract_mishnayot_and_citations(text: str):
    mishnayot = []
    citations = []

    lines = text.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # -------------------
        # MISHNA EXTRACTION
        # -------------------
        if (
            line.startswith("<big><strong>מתני׳</strong></big>") or
            line.startswith("מתני׳ <big><strong>") or
            line.startswith("<big><strong>מתני'</strong></big>")
        ):
            mishna_lines = [line]
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
                mishnayot.append(full_text[:first_colon_index].strip())

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
            skip_next_colon = False

            k = 0
            length = len(gemara_text)

            while k < length:

                # Detect chapter-end marker
                if gemara_text.startswith("<strong>הדרן עלך", k):
                    skip_next_colon = True
                    k += len("<strong>הדרן עלך")
                    continue

                # Detect Daf boundary (line with only 'Daf')
                if gemara_text.startswith("Daf", k) and (k == 0 or gemara_text[k-1] == "\n"):
                 # If a citation was in progress, abandon it (citations cannot span daf)
                    inside_citation = False
                    current = []

                # Skip to next line
                    next_newline = gemara_text.find("\n", k)
                    if next_newline == -1:
                       break
                    k = next_newline + 1
                    continue
                    

                char = gemara_text[k]

                if char == ":":
                    # Ignore exactly ONE colon after chapter-end
                    if skip_next_colon:
                        skip_next_colon = False
                        k += 1
                        continue
                        

                    if not inside_citation:
                        inside_citation = True
                        current = []
                    else:
                        citation = "".join(current).strip()
                        if citation:
                            citation = "\n".join(
                                line.strip() for line in citation.splitlines()
                            )
                            citations.append(citation)

                        inside_citation = False
                        current = []

                    k += 1
                    continue

                if inside_citation:
                    current.append(char)

                k += 1
            # ------------------------------------------------------
# CLOSE citation if gemara ends while inside one
            if inside_citation:
             citation = "".join(current).strip()
             if citation:
                citation = "\n".join(
                  line.strip() for line in citation.splitlines()
                   )
                citations.append(citation)

            i = j
            continue

        i += 1

    return mishnayot, citations
