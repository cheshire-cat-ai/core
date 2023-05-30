# Language Models

A language model is a Deep Learning Neural Network trained on a huge amount of text data to perform different types of language tasks.
Commonly, they are also referred to as Large Language Models (LLM).
Language models comes in many architectures, size and specializations.  
The peculiarity of the Cheshire Cat is to be model-agnostic. This means it supports many different language models.

By default, there are two classes of language models that tackles two different tasks.

## Completion Model
This is the most known type of language models 
(see for examples [ChatGPT](https://openai.com/blog/chatgpt),[Cohere](https://cohere.com/) and many others). A completion model takes a string as input and generates a plausible answer by completion.

!!! warning
    A LLM answer should not be accepted as-is, since LLM are subjected to hallucinations.
    Namely, their main goal is to generate plausible answers from the syntactical point of view.
    Thus, the provided answer could come from completely invented information.

## Embedding Model
This type of model takes a string as input and returns a vector as output. This is known as an *embedding*.
Namely, this is a condensed representation of the input content. 
The output vector, indeed, embeds the semantic information of the input text. 

Despite being non-human readable, the embedding comes with the advantage of living in a Euclidean geometrical space.
Hence, the embedding can be seen as a point in a multidimensional space, thus, geometrical operations can be applied to it.
For instance, measuring the distance between two points can inform us about the similarity between two sentences.

## Language Models flow :material-information-outline:{ title="click on the nodes with hooks to see their documentation" }

!!! note "Developer documentation"
    [Language Models hooks](../technical/plugins/hooks.md)

Nodes with the :hook: point the execution places where there is an available [hook](../plugins.md) to customize the execution pipeline.

