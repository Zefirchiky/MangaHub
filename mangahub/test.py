from models.novels import NovelFormatter
from services.scrapers import NovelsSiteScraper


novel = NovelFormatter(NovelsSiteScraper.get_temp_novel_text())
novel.get_novel_chapter()


# def _fix_new_lines(text: list[str]) -> str:
#     prev = ''
#     i = 0
#     while i < len(text):
#         p = text[i]
#         if not p or p.isspace() or p == "\n":
#             text.pop(i)
#             continue
                        
#         print(p)
#         merge = False
#         if ((p == '"' or p == "'") and len(p) == 1):    # if a whole paragraph is a quote, merge it with the previous paragraph
#             merge = True
#         elif p[0].isspace() or not p[0].isalnum() and not p[0] in ['"', "'"]:      # if it's a space or a quote
#             merge = True
#         elif p[0].islower():      # if it's not the start of the sentence
#             p = ' ' + p
#             merge = True
            
#         if merge and prev:
#             print(f'Merging "{p}" with "{prev}"')
#             prev += p
#             text[i-1] = prev
#             text.pop(i)
#             print(f'Result: "{prev}"')
#         else:
#             i += 1
#             prev = p
            
#     return text

# print(_fix_new_lines(["'", '"', ' ', '2', 'a', 'A', '_', '\n']))
# print()
# print(_fix_new_lines(['"What', '...', '?', '"']))