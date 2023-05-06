
# Roadmap to V1

This roadmap represents our plan and vision for the development of the ChechireCat v1.
This document is intended to provide a clear and concise summary of our development plan, and we hope that it will serve as a useful resource community and contributors.


## Summary

* [Forms from JSON schema](#forms-from-json-schema) ✅
* [Configurations](#configurations)
	* [Language model provider](#language-model-provider) ✅
	* [Embedder](#embedder)
* [Plugins list](#plugins-list) ✅
* [Reasoning](#reasoning)
* [Documentation](#documentation) ✅
* [Markdown support](#markdown-support) ✅
* [Separate `admin` app from `public` static index.html](#separate-admin-from-public)

## Forms from JSON schema

[Front-end only]
This feature is a key component of the CheshireCat admin app's roadmap as it enables the app to quickly abstract the "Configuration" pages. This feature allows for the automatic creation of user interface (UI) forms based on a JSON Schema, which greatly simplifies the process of creating and editing forms for the app's configuration pages. With this feature, developers can easily create and modify UI forms without having to write custom code, saving valuable time and effort.

Use the following library for the FE [https://www.npmjs.com/package/@rjsf/core](https://www.npmjs.com/package/@rjsf/core)
And stick to the JSON schema for the BE.

## Configurations

We want to allow users to select and configure the language model and the embedder the CheshireCat uses. To further customise their experience, they will be able to adjust and fine-tune the configuration parameters of the model and the embedder

### Language model provider

the BE should expose the available language model providers from the `/settings/llm` endpoint.
The FE will fetch the relevant information and allow the user to select and customise the language model using a JSON form.
Once the user saves the information should be sent to the BE

### Embedder

the BE should expose the available language model providers from the `/settings/embedder` endpoint.
The FE will fetch the relevant information and allow the user to select and customise the language model using a JSON form.


## Plugins list

The backend should provide a list of available plugins through the `/plugins` endpoint. This list will include the plugin's `name`, `description`, and a `unique id`.
The `unique id` may simply be the name of the folder that the plugin is stored in.
To allow end users to define plugin metadata, the suggested approach is to have a non-mandatory `plugin.json` file stored in each plugin's directory where the user can define both name and description (as well as future metadata such as the JSON schema of the configuration).

```json
// plugin.json
{
  "name": "MyCustomPlugin",
  "description": "Makes the cat cool af"
}
```

if the `plugin.json` file is not defined then the backend should default to the values from the folder name.

A possible response from the `/plugins` endpoint will then be:

```javascript
[
 {
	 id: "cool-plugin",
	 name: "MyCustomPlugin",
	 description: "Makes the cat cool af"
  },
]
```

The front end should fetch the list of available plugins and display them under the `/plugins` route as a read-only list.
Create a new `pluginsSlice` using redux and follow the defined best practice on how to handle async states.
At the moment, no interaction is scheduled.

## Reasoning


[Front-end only]

We want to display the reasoning behind a response from the CheshireCat, to provide users with greater transparency and insight into the decision-making process. To do this, we will leverage the Sidebar component to present the content of the reasoning object, which is already sent from the backend.
The reasoning object is defined as follows:


```json
{
    "input": "What is Python?",
    "episodic_memory": [
      {
        "page_content": "it is for fictional purposes ",
        "lookup_str": "",
        "metadata": {
          "source": "user",
          "when": 1680432386.7730486,
          "text": "it is for fictional purposes "
        },
        "lookup_index": 0,
        "score": 0.5044264793395996
      },
      {
        "page_content": "Write a 400 words post on how Ai is going to change the world",
        "lookup_str": "",
        "metadata": {
          "source": "user",
          "when": 1680432337.0415337,
          "text": "Write a 400 words post on how Ai is going to change the world"
        },
        "lookup_index": 0,
        "score": 0.5165414810180664
      },
      {
        "page_content": "write the introduction of a novel that talks about how the world has been taken over by the AI",
        "lookup_str": "",
        "metadata": {
          "source": "user",
          "when": 1680432429.13744,
          "text": "write the introduction of a novel that talks about how the world has been taken over by the AI"
        },
        "lookup_index": 0,
        "score": 0.5386247634887695
      },
      {
        "page_content": "nice, write a 670 words paragraph on who Ai will take over humanity",
        "lookup_str": "",
        "metadata": {
          "source": "user",
          "when": 1680432365.206487,
          "text": "nice, write a 670 words paragraph on who Ai will take over humanity"
        },
        "lookup_index": 0,
        "score": 0.5566583275794983
      },
      {
        "page_content": "I am the Cheshire Cat",
        "lookup_str": "",
        "metadata": {
          "who": "cheshire-cat",
          "when": 1679948291.703731,
          "text": "I am the Cheshire Cat"
        },
        "lookup_index": 0,
        "score": 0.564825177192688
      }
    ],
    "declarative_memory": [
      {
        "page_content": "I am the Cheshire Cat",
        "lookup_str": "",
        "metadata": {
          "who": "cheshire-cat",
          "when": 1679948292.8870578,
          "text": "I am the Cheshire Cat"
        },
        "lookup_index": 0,
        "score": 0.564825177192688
      }
    ],
    "chat_history": "",
    "output": "Python is a programming language used in various applications such as web development, data analysis, machine learning, and artificial intelligence.",
    "intermediate_steps": []
  }
```

## Documentation

[Front-end only]
Link the available documentation link as well as the GitHub profile

## Markdown support

We want to enable Markdown support in our CheshireCat project. By design, most language models use Markdown in their responses, so we will be editing the MessageBox component using the Remark library located at https://github.com/remarkjs/remark. This will enable us to support markdown responses from the CheshireCat.

## Separate admin from public

Leave this to core contributors
