import re
from itertools import islice


class Converter:

    def __init__(self, content):
        self.markdown = content
        self.hypertext = ''

    
    def getMarkdown(self):
        """
        Returns Markdown version of the content
        """
        return self.markdown


    def convertHTML(self):
        """
        Returns HTML version of the content
        """
        self.hypertext = self.__toHtml()
        return self.hypertext

    # This function is not accessible by the instance
    # Used encapsulation principle from OOP
    # https://www.programiz.com/python-programming/object-oriented-programming#:~:text=the%20child%20class.-,Encapsulation,i.e%20single%20_%20or%20double%20__%20.
    def __toHtml(self):
        """
        Convert Markdown to HTML
        """
        
        edited_content = self.markdown
        edited_content = self.__clearWrappedLinks(edited_content)
        edited_content = self.__substitutePatterns(edited_content)
        edited_content = self.__insertTags(edited_content)

        return edited_content


    def __substitutePatterns(self, markdown):
        """
        Substitutes strings of headings, list items, italic and bold texts, and links into HTML format
        
        Returns converted HTML content from Markdown
        """
        # https://docs.python.org/3/library/re.html#re.sub
        # This function is based on the re.sub() from Python Docs

        p = Patterns()

        for pattern in p._getPatterns():
            # Get the groups of the pattern
            groups = pattern.groupindex
            # Substitute Markdown into HTML accordingly
            if 'heading' in groups:
                markdown = re.sub(
                    p.md_heading,
                    lambda match: 
                    '<h'+str(match.group('level').count('#', 0, 6))+'>'+
                    match.group('heading')+
                    '</h'+str(match.group('level').count('#', 0, 6))+'>',
                    markdown
                )
            elif 'list' in groups:
                markdown = re.sub(p.md_list, lambda match: '    <li>'+match.group('list')+'</li>', markdown)
            elif 'italic' in groups:
                markdown = re.sub(p.md_italic, lambda match: '<i>'+match.group('italic')+'</i>', markdown)
            elif 'bold' in groups:
                markdown = re.sub(p.md_bold, lambda match: '<b>'+match.group('bold')+'</b>', markdown)
            elif 'link_text' in groups and 'link_href' in groups:
                markdown = re.sub(
                    p.md_links,
                    lambda match:
                    '<a href="'+match.group('link_href')+'">'+match.group('link_text')+'</a>',
                    markdown
                )

        return markdown


    def __insertTags(self, markdown):
        """
        Insert <ul> and <p> tags in the content
        """
        p = Patterns()

        markdown_lines = markdown.splitlines()

        index = 0
        while index < len(markdown_lines):
            # ********
            # Insert opening and closing <ul> in its respective lines of the text
            # ********
            # If a list item (<li>) is found and the previous line doesn't have an <ul> tag
            if '    <li>' in markdown_lines[index] and '<ul>' not in markdown_lines[index - 1]:
                # Inserts opening ul tag
                markdown_lines.insert(index, '<ul>')
                
                # Count <li> items to insert closing <ul> tag after the last <li>
                # Used in the for loop below
                count = 0

                # OBS: You can skip reading this comment
                # Used slicing to prevent starting from the beginning of the list
                # But this is terrible for large lists, since slicing usually copies 
                # the content of the list (according to UndeadKernel's response to
                # the answer of this Stack Overflow question:
                # https://stackoverflow.com/questions/6148619/start-index-for-iterating-python-list)
                #
                # As John La Rooy commented, must use islice from itertools
                
                for item in islice(markdown_lines, index + 1, None):
                    # Counts number of <li> items
                    if '    <li>' in item:
                        count += 1
                    
                    # If there's no more <li> tag following the previous one, the list has ended
                    elif '    <li>' not in item:
                        break

                markdown_lines.insert(index + 1 + count, '</ul>') # Inserts closing ul tag at the end of a group of <li> items
                index += count + 1 # Skip iteration to the end of the list

            # ********
            # Insert <p> tags when the line of the text doesn't contain any paragraphs, titles or list items (which
            # are excluded patterns)
            # ********
            excluded = p._getPatterns(excluded=True)
            allowParagraph = False
          
            if markdown_lines[index]:
                # If no pattern matches, paragraph is allowed 
                for pattern in excluded:
                    if not re.search(pattern, markdown_lines[index]):
                        allowParagraph = True
                    else:
                        allowParagraph = False
                        break


            if allowParagraph:
                markdown_lines[index] = f"<p>{markdown_lines[index]}</p>"

            index += 1
            
        # Converts list of strings into one string
        parsed_html = '' 
        for item in markdown_lines:
            parsed_html = '\n'.join(markdown_lines)

        return parsed_html


    def __clearWrappedLinks(self, markdown):
        """
        Clears Markdown links that are wrapped 
        by parentheses or brackets by substituting them with
        HTML entities.
        """
        # Ex: Without this function, a wrapped link like 
        # ([Link text](https://example.com)) would not be
        # captured correctly by regexes. Must be called
        # before any other converting function, as seen
        # in __toHTML() function.
        
        p = Patterns()

        # Get number of matches and loop on them
        num_links = len(re.findall(p.md_links, markdown))
        # Looks for opening and closing parentheses
        for i in range(num_links):
            # Get current matches in a list
            matches = re.finditer(p.md_links, markdown)     
            # List comprehension used as sintatic sugar for storing the iterable as a list
            # https://www.w3schools.com/python/python_lists_comprehension.asp       
            match = [matches for matches in matches]

            # Gets current match span (i.e. the starting and ending indexes of the captured substring)
            index = match[i].span()

            # Position of possible opening and closing parentheses
            openingPar = index[0] - 1
            closingPar = index[1] - 1

            # If there's opening and closing parentheses, substitute them with HTML entities to avoid 
            # confusion with the closing parentheses from the markdown link
            if markdown[openingPar] == "(" and markdown[closingPar] == ")" and markdown[index[1] - 2] == ")":
                markdown = markdown[:closingPar] + '&rpar;' + markdown[index[1]:]
            
            try:
                # If the link is wrapped by brackets, replace them with HTML entities to avoid parsing confusion
                if markdown[index[0]] == '[' and markdown[index[1]] == ']':
                    markdown = markdown[:index[0]] + '&lbrack;' + markdown[index[0] + 1:index[1]] + '&rbrack;' + markdown[index[1] + 1:]
            except IndexError:
                # In case the link is the very last element in the markdown string, to avoid IndexError by the line above (markdown[index[1]),
                # this try except block is used to treat this case.
                #
                # According to the Stack Overflow answer below, it is ok to try except a specific type of error, instead of
                # doing some kind of except: pass (without passing any specific Error), which would skip every error, not 
                # treating them. Of course, doing this would make a try except block useless.
                #
                # https://stackoverflow.com/questions/21553327/why-is-except-pass-a-bad-programming-practice
                pass

                
        return markdown
          
        
class Patterns:
    # https://docs.python.org/3/howto/regex.html
    # re.compile with named groups and flags are based from the Python Docs (also, CS50W Project 1 specs encourages the use of regex)
    
    # According to the links below, encapsulation can be done via @property decorator which is a more pythonic way of 
    # implementing it. You can create getters and setters (and other functionalities too)

    # https://www.programiz.com/python-programming/property
    # https://stackoverflow.com/questions/14594120/python-read-only-property
    # https://www.geeksforgeeks.org/read-only-properties-in-python/

    # *************
    # Using @property decorator to make the regex patterns read-only. 
    # *************
    # Markdown tags
    # *************
    @property
    def md_heading(self):
        return re.compile(r'^(?P<level>#{1,6}) (?P<heading>[^\r\n]+(?=\r|\n))', flags=re.MULTILINE)

    @property
    def md_list(self):
        return re.compile(r'^(\*|-) (?P<list>[^\r\n]*)', flags=re.MULTILINE)

    @property
    def md_italic(self):
        return re.compile(r'(?<!\*)\*(?P<italic>[^*\n\r]+)\*(?!\*)')

    @property
    def md_bold(self):
        return re.compile(r'\*{2}(?P<bold>[^*]+)\*{2}')

    @property
    def md_links(self):
    # https://www.urlencoder.io/learn/#url-encoding-percent-encoding
    # https://www.abramillar.com/2018/01/15/special-characters-short-words-urls/
    # According to these articles, URLs are ASCII based and special characters include
    # "-", ".", "_", "~", "#" and "%" for escaping and URL encoding
        return re.compile(r'\[+?(?P<link_text>[ \w/|\[\]\(\){}\'.-^%~:;,ªº°¹³£¢¬§!@#$%¨&*+"´`]+?)\]\((?P<link_href>(https?://(w{3}.)?[\w\-.~]+.[\w]+/?|/)([\w\-.~%/\#\(\)]+)?)\)+?', flags=re.ASCII)

    # *********
    # HTML tags
    # *********
    @property
    def html_heading(self):
        return re.compile(r'(<h[1-6]>).*(</h[1-6]>)')

    @property
    def html_li(self):
        return re.compile(r'(    <li>).*(</li>)?')

    @property
    def html_ul(self):
        return re.compile(r'(</?ul>).*(</ul>)?')


    def _getPatterns(self, excluded=False):
        """
        Returns a tuple of regexes to match markdown patterns for headings, lists, italic, bold and links

        Keyword arguments:

        excluded -- returns tuple of regexes that matches HTML tags (headings and lists) if set to True
        """
        return self.__loadExcludedPatterns() if excluded else self.__loadMarkdownPatterns()


    def __loadMarkdownPatterns(self):
        """
        Returns a tuple of regexes to match markdown headings, lists, italic, bold and links
        """
        patterns = (self.md_heading, self.md_list, self.md_italic, self.md_bold, self.md_links)
        return patterns


    def __loadExcludedPatterns(self):
        """
        Returns a tuple of regexes to match HTML headings and unordered lists
        """
        excluded_patterns = (self.html_heading, self.html_li, self.html_ul)
        return excluded_patterns
