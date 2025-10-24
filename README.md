# lazyreport
![lazyReport](https://image.prntscr.com/image/cmYRWQBsTL61frAjQiBGXw.png)
<p>
	<a href="https://python.org"><img src="https://img.shields.io/badge/made%20with-Python-red"></a>
	<a href="https://github.com/narlyseorg/lazyreport/blob/master/LICENSE"><img src="https://img.shields.io/badge/License-MIT-red"></a>
	<a href="#"><img src="https://img.shields.io/badge/platform-osx%2Flinux%2Fwindows-red"></a>
</p>

## Background

Had hoped to build this in Go, but surprise; every decent document library is commercial and the free alternatives? Let's just say they're only fun if you have a masochistic streak. So, here we are, in Python; at least the open-source ecosystem actually works.

## Introduction

lazyreport is a semi-automated, AI-powered penetration testing report generator. You feed it the details, it leans on Hugging Face API to craft technical writeups and then churns out a Word document so you can look professional with minimal effort. It's not perfect—then again, neither are you.

## Features

- Swap markers in your template with AI-crafted content.
- Toggle Scope and CVSS inputs on or off.
- Flexible scope: stick with fixed endpoints or define your own.
- Support for CVSS 4.0 and 3.1 standards.
- Auto-sort vulnerabilities by severity.
- Customize prompts to bend the AI to your will.

## Installation

### Prerequisites

You need **Python 3.8+** installed on your system.

### 1. Clone

    git clone https://github.com/narlyseorg/lazyreport.git
    cd lazyreport

### 2. Venv

It's highly recommended to use a virtual environment.

#### macOS/Linux:

    python3 -m venv .venv
    source .venv/bin/activate

#### Windows:

    python -m venv .venv
    .venv\Scripts\activate

### 3. Install

Install the project in editable mode:

    pip install -e .

### 4. APIKey

lazyreport requires a Hugging Face API Token to access the models for content generation.

- Head over to https://huggingface.co/settings/tokens
- Click "New token" (read access is sufficient)
- Copy your token and set it as an environment variable:

      export HF_API_KEY=hf_...yourtoken...

  Or drop it directly into `config.py` as `HF_API_KEY`.

## Configuration

All the fun happens in `config.py`:
- Rename the template file if you dare (default: `template.docx`).
- Tweak the model name, toggles, and especially the prompts.
- You can add or remove report sections, change CVSS settings, and more.

> [!NOTE]
> Prompts are, frankly, premature and need serious fine-tuning.

## Usage

Once the environment is set up and your HF_API_KEY is configured, run directly:

    lazyreport

or

    python -m lazyreport

Follow the prompts. Answer honestly. Or don't. The AI doesn't care.

## Limitations
- Prompts aren't fine-tuned. Expect weirdness.
- Only supports text input for now.
- Automatic CVSS? Not on my watch.

## Roadmap (Future)
- Support for image input.
- OpenAI/Anthropic/Ollama integration.
- Web-based UI.

## Demonstration
[![Demonstration](https://drive.google.com/thumbnail?id=1si_1o2iRa5SpM2ICRL-27RVvBaYSc0X9&sz=w400)](https://drive.google.com/file/d/1si_1o2iRa5SpM2ICRL-27RVvBaYSc0X9/view)

## Contributing

PRs welcome, but if you break it, you get to keep both pieces.

## Shout-out!

- [Hugging Face](https://huggingface.co/)
- [CVSS by FIRST.org](https://www.first.org/cvss/)

## License

This program is free software: Feel free to copy, tweak or abuse it; as long as you play nice under the terms of the [MIT License](https://github.com/narlyseorg/lazyreport/blob/master/LICENSE). Author: [Zoey](https://github.com/narlyseorg)
