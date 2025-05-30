from __future__ import annotations
import re
from typing import Self
from pydantic import BaseModel, ConfigDict
from bs4 import BeautifulSoup
from loguru import logger


class ParsingMethod(BaseModel):
    """
    Method to parse HTML for needed elements.

    - Pass keyword arguments during initialization (e.g., `name='div'`, `class_='my-class'`) 
      to be used directly by BeautifulSoup's `find_all` method. These are stored in `model_extra`.
    - `regex`: If set, regular expression to apply.
        - If find_all criteria (kwargs) are also set, regex applies to the string content of each tag found by find_all.
        - If no find_all criteria, regex applies to the whole HTML input.
    - `look_for`: Attribute to extract from found tags (e.g., 'href', 'src'). 
        - Special values: 'text' (for `tag.get_text()`) or 'html' (for `str(tag)`).
        - Applied if `regex` is not set or does not yield results for a specific tag.
    - `parsing_methods`: A list of sub-ParsingMethod instances to apply recursively.
        - If tags are found by find_all, sub-methods apply to each tag's HTML.
        - If no tags are found (or find_all not used), sub-methods apply to the original HTML input.
    - `path`: An optional descriptive path or context for this parsing rule (not used in parsing logic directly).
    """
    model_config = ConfigDict(
        extra="allow",  # Allow arbitrary kwargs to be captured in self.model_extra
        arbitrary_types_allowed=True # Useful if you ever decide to store BsTag objects
    )
    
    path: str = ''
    regex: str = r''
    look_for: str = ''
    
    parsing_methods: list[ParsingMethod] = []
    
    def add_parsing_method(self, parsing_method: ParsingMethod) -> Self:
        """
        Add another parsing method to the list of parsing methods.
        
        :param parsing_method: Instance of ParsingMethod
        :return: Self
        """
        if self.path or self.regex or self.model_extra:
            self.parsing_methods.append(parsing_method)
            return self
        else:
            raise Exception('Set parsing method before adding another one')
        
    def parse_html(self, html: str) -> list:
        """
        Parses the given HTML string based on this method's configuration.
        Returns a list of extracted items or results from sub-parsers.
        The results from sub-parsers are appended as lists, creating nested structures if sub-parsers also return lists.
        """
        soup = BeautifulSoup(html, 'html.parser')
        final_results = []
        
        bs_kwargs = self.model_extra if self.model_extra is not None else {}
        
        tags_found_by_bs = []
        if bs_kwargs:
            try:
                tags_found_by_bs = soup.find_all(**bs_kwargs)
                logger.trace(f"BS find_all({bs_kwargs}) found {len(tags_found_by_bs)} tags.")
            except Exception as e:
                logger.error(f"BeautifulSoup find_all failed with kwargs {bs_kwargs}: {e}")
                return final_results # Critical error, stop processing for this method
        
        # Scenario A: Tags were found by BeautifulSoup's find_all
        if tags_found_by_bs:
            for tag in tags_found_by_bs:
                tag_as_str = str(tag)
                current_level_tag_extraction = []

                # 2A.1: Apply regex to the string content of the current tag
                if self.regex:
                    try:
                        regex_matches_on_tag = re.findall(self.regex, tag_as_str)
                        current_level_tag_extraction.extend(regex_matches_on_tag)
                    except re.error as e:
                        logger.error(f"Regex error '{e}' with pattern '{self.regex}' on tag content.")
                
                # 2A.2: Apply 'look_for' if regex is not defined for this level.
                # (If regex is defined, its results are prioritized for this level's direct extraction from the tag)
                elif self.look_for:
                    value_to_add = None
                    if self.look_for == 'text':
                        value_to_add = tag.get_text(strip=True)
                    elif self.look_for == 'html':
                        value_to_add = str(tag) # outerHTML of the tag
                    elif hasattr(tag, 'get'): # For standard attributes like 'href', 'class', etc.
                        value_to_add = tag.get(self.look_for)
                    else: 
                        logger.warning(f"'look_for: {self.look_for}' is not 'text', 'html', or a gettable attribute for tag: {tag.name}")
                    
                    if value_to_add is not None:
                        current_level_tag_extraction.append(value_to_add)
                
                # 2A.3: If tag was selected by find_all, but no specific regex/look_for at this level,
                # AND no sub-parsers are defined, then the tag itself (as string) is the result from this level.
                elif not self.parsing_methods:
                    current_level_tag_extraction.append(tag_as_str)
                
                # Add what was extracted from this tag at this level to the final results.
                final_results.extend(current_level_tag_extraction)

                # 2A.4: Apply sub-parsers to the HTML of the current tag
                if self.parsing_methods:
                    try:
                        sub_html = tag.prettify()
                        for sub_parser in self.parsing_methods:
                            # Appends the list returned by the sub_parser, creating nested lists (original behavior)
                            final_results.append(sub_parser.parse_html(sub_html))
                    except Exception as e:
                        logger.error(f"Error processing sub-parsers for tag {tag.name}: {e}")
        
        # Scenario B: No tags found by find_all (or find_all not used because no kwargs)
        else:
            # 2B.1: Apply regex to the entire original HTML if specified
            if self.regex:
                try:
                    regex_matches_on_html = re.findall(self.regex, html)
                    final_results.extend(regex_matches_on_html)
                except re.error as e:
                    logger.error(f"Regex error '{e}' with pattern '{self.regex}' on full HTML.")
            
            # 2B.2: Apply sub-parsers to the original HTML.
            # This runs if find_all wasn't used (no bs_find_all_kwargs) or if it yielded no tags.
            # It allows a ParsingMethod to act as a container or apply to whole doc if find_all fails.
            if self.parsing_methods:
                logger.trace("No BS tags processed or BS not used at this level. Applying sub-parsers to original HTML.")
                for sub_parser in self.parsing_methods:
                    try:
                        final_results.append(sub_parser.parse_html(html))
                    except Exception as e:
                        logger.error(f"Error processing sub-parsers on full HTML: {e}")
            
            # 2B.3: If no find_all, no regex, no sub-parsers, but 'look_for' is set (e.g., 'text' on whole doc)
            elif not self.regex and not self.parsing_methods and self.look_for:
                logger.trace(f"No BS tags, no regex, no sub-parsers. Applying 'look_for: {self.look_for}' to whole document.")
                if self.look_for == 'text':
                    final_results.append(soup.get_text(strip=True))
                elif self.look_for == 'html':
                    final_results.append(str(soup)) # Full HTML content from soup
                else: # 'look_for' for a specific attribute doesn't make sense on the whole doc without a tag context.
                    logger.warning(f"'look_for: {self.look_for}' on whole document without tags is only supported for 'text' or 'html'.")

        # logger.debug(f"parse_html for method ({self.model_dump_json(exclude_defaults=True, exclude_none=True, exclude={'parsing_methods'})}) on HTML (len={len(html)}) -> results (len={len(final_results)}): {str(final_results)[:300]}...")
        return final_results