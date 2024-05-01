import pprint as pprint_orig

def pprint(object, stream=None, indent=1, width=80, depth=None, *,
           compact=False, sort_dicts=True, underscore_numbers=False):
    print(pprint_orig.pformat(object, indent, width, depth, compact=compact, sort_dicts=sort_dicts, underscore_numbers=underscore_numbers))

pprint_orig.pprint=pprint
