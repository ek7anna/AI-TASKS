"""
utils.py - Shared Utility Helper Functions

Contains vector formatting and Solr query payload helpers.
"""

def format_vector_for_solr(vector_list):
    """Formats a floating point vector array into Solr KNN query bracket string [0.1,0.2,...]"""
    return "[" + ",".join(map(str, vector_list)) + "]"

def clean_context_string(results):
    """Parses list of Solr documents and extracts clean concatenated context text."""
    context_chunks = []
    for result in results:
        content = result.get("content", "")
        if isinstance(content, list):
            context_chunks.append(content[0])
        else:
            context_chunks.append(str(content))
    return "\n---\n".join(context_chunks)
