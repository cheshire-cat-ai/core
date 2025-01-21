# Contributing to Cheshire Cat

First off, thanks for joining the project as a contributor! ❤️
The community looks forward to your contributions. 🎉

All types of contributions are encouraged and valued. See the [Table of Contents](#table-of-contents) for different ways to help and details about how this project handles them. Please make sure to read the relevant section before making your contribution. It will make it a lot easier for us maintainers and smooth out the experience for all involved.

> If you like the project but just don't have time to contribute, there are other easy ways to support the project and show your appreciation:
>
> - Star the project
> - Sharing on social media
> - Refer this project in your project's readme
> - Mention the project at local meetups and tell your friends/colleagues

## Table of Contents

- [Contributing to Cheshire Cat](#contributing-to-cheshire-cat)
  - [Table of Contents](#table-of-contents)
  - [I Have a Question](#i-have-a-question)
  - [I Want To Contribute](#i-want-to-contribute)
    - [Reporting Bugs](#reporting-bugs)
      - [Before Submitting a Bug Report](#before-submitting-a-bug-report)
      - [How Do I Submit a Good Bug Report?](#how-do-i-submit-a-good-bug-report)
    - [Suggesting Enhancements](#suggesting-enhancements)
      - [Before Submitting an Enhancement](#before-submitting-an-enhancement)
      - [How Do I Submit a Good Enhancement Suggestion?](#how-do-i-submit-a-good-enhancement-suggestion)
    - [Your First Code Contribution](#your-first-code-contribution)
    - [Improving The Documentation](#improving-the-documentation)
  - [Attribution](#attribution)

## I Have a Question

> If you want to ask a question, we assume that you have read the available [Documentation](https://cheshire-cat-ai.github.io/docs/) and [FAQs](https://cheshire-cat-ai.github.io/docs/faq/general/).

Before you ask a question, it is best to search for existing [Issues](https://github.com/cheshire-cat-ai/core/issues/) that might help you. In case you have found a suitable issue and still need clarification, you can comment in the issue. If the problem you encountered is not strictly related to the Cat, try to search the internet for answers first.

If you then still feel the need to ask a question and need clarification, we recommend the following:

- Open an [Issue](https://github.com/cheshire-cat-ai/core/issues/new/choose).
- Provide as much context as you can about what you're running into.
- Provide a description on how to repeat the error, in case you have one.

We will then take care of the issue as soon as possible.
We have also a [Discord server](https://discord.gg/bHX5sNFCYU) to engage with the community.

## I Want To Contribute

> ### Legal Notice
>
> When contributing to this project, you must agree that you have authored 100% of the content, that you have the necessary rights to the content and that the content you contribute may be provided under the project license.

### Reporting Bugs

#### Before Submitting a Bug Report

A good bug report shouldn't leave others needing to chase you up for more information. Therefore, we ask you to investigate carefully, collect information and describe the issue in detail in your report. Please complete the following steps in advance to help us fix any potential bug as fast as possible.

- Make sure that you are using the latest version.
- Determine if your bug is really a bug and not an error on your side e.g. using incompatible environment components/versions (Make sure that you have read the [documentation](https://cheshire-cat-ai.github.io/docs/). If you are looking for support, you might want to check [this section](#i-have-a-question)).
- To see if other users have experienced (and potentially already solved) the same issue you are having, check if there is not already a bug report existing for your bug or error in the [bug tracker](https://github.com/cheshire-cat-ai/core/issues?q=label%3Abug).
- Also make sure to search the internet (including Stack Overflow) to see if users outside of the GitHub community have discussed the issue.
- Collect information about the bug:
  - Stack trace (Traceback)
  - OS, Platform and Version (Windows, Linux, macOS, x86, ARM)
  - Version of the interpreter, compiler, SDK, runtime environment, package manager, depending on what seems relevant.
  - Possibly your input and the output
  - Can you reliably reproduce the issue? And can you also reproduce it with older versions?

#### How Do I Submit a Good Bug Report?

> You must never report security related issues, vulnerabilities or bugs including sensitive information to the issue tracker, or elsewhere in public. Instead sensitive bugs must be reported to main contributors.

We use GitHub issues to track bugs and errors. If you run into an issue with the project:

- Open an [Issue](https://github.com/cheshire-cat-ai/core/issues/new/choose). (Since we can't be sure at this point whether it is a bug or not, we ask you not to talk about a bug yet and not to label the issue.)
- Explain the behavior you would expect and the actual behavior.
- Please provide as much context as possible and describe the _reproduction steps_ that someone else can follow to recreate the issue on their own. This usually includes your code. For good bug reports you should isolate the problem and create a reduced test case.
- Provide the information you collected in the previous section.

Once it's filed, a team member will try to reproduce the issue with your provided steps and help finding a solution.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for Cheshire Cat, **including completely new features and minor improvements to existing functionality**. Following these guidelines will help maintainers and the community to understand your suggestion and find related suggestions.

#### Before Submitting an Enhancement

- Make sure that you are using the latest version.
- Read the [roadmap](./ROADMAP.md) to see if the feature is already planned.
- Read the [documentation](https://cheshire-cat-ai.github.io/docs/) carefully and find out if the functionality is already covered, maybe by an individual configuration.
- Perform an [issue search](https://github.com/cheshire-cat-ai/core/issues/) to see if the enhancement has already been suggested. If it has, add a comment to the existing issue instead of opening a new one.
- Find out whether your idea fits with the scope and aims of the project. It's up to you to make a strong case to convince the project's developers of the merits of this feature. Keep in mind that we want features that will be useful to the majority of our users and not just a small subset. If you're just targeting a minority of users, consider writing an add-on/plugin library.

#### How Do I Submit a Good Enhancement Suggestion?

Enhancement suggestions are tracked as [GitHub issues](https://github.com/cheshire-cat-ai/core/issues/).

- Use a **clear and descriptive title** for the issue to identify the suggestion.
- Provide a **step-by-step description of the suggested enhancement** in as many details as possible.
- **Describe the current behavior** and **explain which behavior you expected to see instead** and why. At this point you can also tell which alternatives do not work for you.
- You may want to **include screenshots and animated GIFs** which help you demonstrate the steps or point out the part which the suggestion is related to. You can use [this tool](https://www.cockos.com/licecap/) to record GIFs on macOS and Windows, and [this tool](https://github.com/colinkeenan/silentcast) or [this tool](https://github.com/GNOME/byzanz) on Linux. <!-- this should only be included if the project has a GUI -->
- **Explain why this enhancement would be useful** to most Cheshire Cat users. You may also want to point out the other projects that solved it better and which could serve as inspiration.

### Your First Code Contribution

1. Fork the Project (all branches) and clone the forked repository to your machine (`git clone "url of repository"`), where the "url of repository" means the url of your fork of the project.
2. Checkout the `develop` branch (`git checkout develop` and then `git pull origin develop`)
3. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
4. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the Branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request against the `develop` branch (if it contains lots of code, please discuss it beforehand opening a issue)

Try to keep your PRs small and in line with roadmap and issues.

### Improving The Documentation

Docs contribution are highly valuable for the project.
See details on how to help with the docs [here](https://github.com/cheshire-cat-ai/docs/).

## Attribution

This guide is based on the **contributing-gen**. [Make your own](https://github.com/bttger/contributing-gen)!
