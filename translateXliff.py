import sys
import re
from mkTranslation.translate_google import mkGoogleTranslator
import xml.etree.ElementTree as ET
ET.register_namespace("", "urn:oasis:names:tc:xliff:document:1.2")

def parseHTML(element):
    for e in element:
        # Save tail because we clear the element at below lines
        savedTail = e.tail
        # Check if element has text and isn't line break
        if e.text != None and e.text != "\n":
            # Get the whole text: It deletes tags inside the element. For instance: <strong></strong>
            text = "".join(e.itertext())
            print("text attrib: %s \n innertext attrib: %s \n tail attrib: %s\n\n"%(e.text, "".join(e.itertext()), e.tail))
            # Find some problematic words like &amp; or &quot in whole text;
            amp_html = re.finditer("&\w+;", text)
            # We use clear in order to remove e.text and e.itertext() data
            e.clear()
            e.text = ''
            # Init counters to the loop
            i = 0

            for ah in amp_html:
                # Get the occurrence position
                j = ah.span()[0]
                e.text += mkGoogleTranslator().translate_text(text=text[i:j], dest=destinationLanguage).text + ah.group()
                i = ah.span()[1]
            if i !=0:
                # We need to include the last chars of the text after the last occurrence
                e.text += mkGoogleTranslator().translate_text(text=text[i:len(text)], dest=destinationLanguage).text
            else:
                # If no &amp; on text, translate the whole text
                e.text = mkGoogleTranslator().translate_text(text=text, dest=destinationLanguage).text
            
            # Some time we have a tail not included in "itertext", so we have to parse like previous
            if savedTail != None and savedTail != "\n":
                print("HAVE--- TAIL")
                amp_html = re.finditer("&\w+;", savedTail)
                i = 0
                text = savedTail
                for ah in amp_html:
                    print("HAVE--- AMP2")
                    j = ah.span()[0]
                    savedTail += mkGoogleTranslator().translate_text(text=text[i:j], dest=destinationLanguage).text + ah.group()
                    i = ah.span()[1]
                if i != 0:
                    e.text += mkGoogleTranslator().translate_text(text=text[i:len(text)], dest=destinationLanguage).text
                else:
                    e.text += mkGoogleTranslator().translate_text(text=text, dest=destinationLanguage).text
        else:
            parseHTML(e)


destinationLanguage = None
tree = ET.parse(sys.argv[1])
root = tree.getroot()

destinationLanguage = root[0].attrib['target-language']
print('The target language is "%s"' % destinationLanguage)

bodyElement = root[0][0]
for group in bodyElement:
    for trans_unit in group:
        text = trans_unit[1].text
        if text != None:
            # If no HTML provided, it's only plain text
            trans_unit[1].text = mkGoogleTranslator().translate_text(text=text, dest=destinationLanguage).text
        elif len(list(trans_unit[1])):
            # Check if element has child
            parseHTML(trans_unit[1][0])

tree.write(sys.argv[1]+'_traduit.xlf', encoding="UTF-8")


