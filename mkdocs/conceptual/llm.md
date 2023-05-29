# Language Models

A language model is a Deep Learning Neural Network model trained on a huge amount of text data to perform different types of language tasks.   
Language models comes in many architectures, size and specializations. The Cheshire Cat, by default, has two types of language models.

## Large Language Model (LLM)
This is the most known type language models. A LLM takes a string as input and generates a plausible by completion.

!!! warning
    A LLM answer should be accepted as-is, since LLM are subjected to hallucinations.
    Namely, their main goal is to generate plausible answers from the syntactical point of view.
    Thus, the provided answer could come from completely invented information.

## Embedder
This type of model takes a string as input and returns a vector as output. This is knows as an *embedding*.
Namely, this is a condensed representation of the semantic content of the input text. 
The output vector, indeed, embeds the semantic information of input. 

Despite being non-human readable, the embedding comes with the advantage of living in a Euclidean geometrical space.
Hence, the embedding can be seen as a point in a multidimensional space and geometrical operation are applicable to it.
For instance, measuring the distance between two points can inform us about the similarity between two sentences.

## Language Models flow :material-information-outline:{ title="click on the hooks node to see the hooks documentation" }

!!! note "Developer documentation"
    [Language Models hooks](../technical/plugins/hooks.md)

Nodes with the :hook: point the execution places where there is an available [hook](../plugins.md) to customize the execution pipeline.

