# Basic tacpac functions

def remove_header (content):
    lines = str(content).splitlines()
    if lines[0].startswith("`"):
        #Return everything without the first line
        return "\n".join(lines[1:])
    else:
        #Return what came in
        return content
    
