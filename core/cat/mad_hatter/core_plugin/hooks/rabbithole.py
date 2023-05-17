from cat.mad_hatter.decorators import hook


# Hook called just before of inserting documents in vector memory
@hook(priority=0)
def before_rabbithole_insert_memory(doc, cat):
    return doc


# Hook called before an ingested file is summarized.
# Should return a boolean indicating if the summarization has to be done or not
@hook(priority=0)
def before_rabbithole_summarizes_file(doc, cat):
    return True


# Hook called before an ingested URL is summarized.
# Should return a boolean indicating if the summarization has to be done or not
@hook(priority=0)
def before_rabbithole_summarizes_url(doc, cat):
    return True
