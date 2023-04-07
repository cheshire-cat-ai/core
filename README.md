# 📚 How to contribute documentation

1. Fork the repository and checkout to the `docs` branch.
2. Using Markdown syntax, edit or create new files for the documentation in the `/mkdocs` directory.
3. Use headings, bullet points or numbered lists, code blocks and other formatting tools to make the documentation easy to read and understand.
4. Use clear and concise language to explain the features, functions or concepts that are being documented.
5. Use hyperlinks, images or other visual aids to enhance the documentation.
6. Use the appropriate `/assets` folder for your static assets. Eg. Images goes under `/assets/img`
7. When finished, commit and push your changes to your forked repository.
8. Open a pull request and ask for feedback from the community.
9. Keep your contributions up-to-date with any changes or updates made to the main repository.

There is a [dedicated channel for Docs on our official Discord](https://discord.com/channels/1092359754917089350/1092360068269359206), don't be shy and contact us there if you need help! 

## 🤹 Manage the tecnology [mkdocs]

### 📦 Requirements

- Python 3.8+
- Pip 20+

Install dependencies:  

`$ pip install -r requirements.txt`

### 🛠️ Develop

`$ mkdocs serve` or `$ python -m mkdocs serve` will launch a local, non static, instance of the documentation website.

### 🏗️ Build

The build stage is automated using GitHub action, you don't need to do it in order to contribute. However, if you want to have a static copy of the documentation on your local machine you are free to do it.  

`$ mkdocs build` or `$ python -m mkdocs build` will create the actual docs static website in a folder named `/docs`.