import logging
from typing import Dict, Optional
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

def extract_urv_contents(soup: BeautifulSoup, subject_title: str = None) -> Optional[Dict[str, str]]:
    logger.debug("🔍 Searching for contents table with Topic/Sub-topic headers")
    result = {"contents": None, "objectives": None, "competences": None}

    contents_table = None
    for table in soup.find_all('table'):
        headers = table.find_all('td', class_='VerdanaBlanca mainfons')
        if headers:
            header_texts = [header.get_text(strip=True).lower() for header in headers]
            if ('topic' in header_texts or 'tema' in header_texts) and ('sub-topic' in header_texts or 'subtema' in header_texts):
                contents_table = table
                logger.info("✅ Contents table found with Topic/Sub-topic headers")
                break

    if not contents_table:
        logger.debug("🔍 No table with Topic/Sub-topic headers, trying fallback")
        for table in soup.find_all('table'):
            rows = table.find_all('tr')
            if len(rows) > 2:
                cells = rows[0].find_all('td')
                if len(cells) >= 2 and any('Verdana' in cell.get('class', []) for cell in table.find_all('td')):
                    content_valid = False
                    for row in rows:
                        row_cells = row.find_all('td', class_='Verdana')
                        if len(row_cells) >= 2:
                            topic = row_cells[0].get_text(strip=True)
                            if len(topic) > 5 and not re.match(r'^[A-Z\s,]+$', topic):
                                content_valid = True
                                break
                    if content_valid:
                        contents_table = table
                        logger.info("✅ Fallback table found with Verdana class cells")
                        break

    if contents_table:
        contents = []
        for row in contents_table.find_all('tr'):
            cells = row.find_all('td', class_='Verdana')
            if len(cells) >= 2:
                topic = cells[0].get_text(strip=True)
                subtopics = cells[1].get_text(separator="\n", strip=True).split('\n')
                if topic and subtopics and any(subtopic.strip() for subtopic in subtopics):
                    subtopics_clean = [subtopic.strip() for subtopic in subtopics if subtopic.strip()]
                    contents.append(f"TOPIC: {topic}\nSUBTOPICS: {', '.join(subtopics_clean)}")
                    logger.debug(f"Extracted topic: {topic} with subtopics: {subtopics_clean}")
        if contents:
            result["contents"] = "\n\n".join(contents)

    for table in soup.find_all('table'):
        rows = table.find_all('tr')
        for i, row in enumerate(rows):
            cells = row.find_all('td')
            if len(cells) >= 3 and 'Learning outcomes' in row.get_text():
                objectives = []
                for next_row in rows[i+1:]:
                    if 'Type' in next_row.get_text():
                        break
                    code_cell = next_row.find('a', class_='Ntooltip2')
                    if code_cell:
                        objectives.extend([
                            obj.strip() 
                            for obj in next_row.get_text(separator='<br>').split('<br>') 
                            if obj.strip()
                        ])
                if objectives:
                    result["objectives"] = "\n".join(objectives)

            if len(cells) >= 3 and 'Competences' in row.get_text():
                competences = []
                for next_row in rows[i+1:]:
                    if 'Type' in next_row.get_text():
                        break
                    code_cell = next_row.find('td', string=re.compile(r'[A-Z]+\d+'))
                    if code_cell:
                        competences.append(next_row.get_text(separator=' ', strip=True))
                if competences:
                    result["competences"] = "\n".join(competences)

    if any(result.values()):
        return result
    logger.info("❌ No valid contents extracted from table")
    return None