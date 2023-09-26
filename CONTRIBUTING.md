# Contributing to SafeSCARF Connector

We welcome contributions to SafeSCARF Connector! Before you start, please read
this guide to learn how to contribute effectively to the project.

## Table of Contents

- [Contributing to SafeSCARF Connector](#contributing-to-safescarf-connector)
  - [Table of Contents](#table-of-contents)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Development Workflow](#development-workflow)
    - [Code Style](#code-style)
    - [Testing](#testing)
  - [Commit Guidelines](#commit-guidelines)
    - [Pre-Commit Hooks](#pre-commit-hooks)
  - [Submitting Changes](#submitting-changes)

## Getting Started

### Prerequisites

Before you begin, make sure you have the following tools installed:

- [Git](https://git-scm.com/)
- [Python](https://www.python.org/)

### Installation

1. Clone the repository:

    ```bash
    git clone https://gitlab.devops.telekom.de/secureops/safescarf/safescarf-connector.git
    cd safescarf-connector
    ```

1. Create a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

1. Install the project dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Development Workflow

### Code Style

We use pre-commit to ensure code consistency. Before making any commits, please
install it by running:

```bash
pip install pre-commit
pre-commit install
```

This will set up pre-commit hooks that will run checks on your code for things
like trailing whitespace, YAML formatting, and Markdown linting. These checks
help ensure that your contributions meet our coding standards.

### Testing

> There are no test available currently - therefore this step can be skipped!

Make sure your code passes all tests before submitting a pull request. You can
run the tests using:

```bash
pytest
```

## Commit Guidelines

### Pre-Commit Hooks

To ensure that your commits pass the pre-commit hooks, you can manually run the
hooks with:

```bash
pre-commit run --all-files
```

We highly recommend running this command before making a commit. If any issues
are found, pre-commit will provide instructions on how to fix them.

## Submitting Changes

1. Create a new branch:

    ```bash
    git checkout -b my-feature-branch
    ```

1. Make your changes, add and commit:

    ```bash
    git add .
    git commit -m "Description of your changes"
    ```

1. Push your branch to the repository:

    ```bash
    git push origin my-feature-branch
    ```

1. Create a pull request on GitHub with a clear description of your changes.

1. Wait for the code review and address any feedback.

1. Once your changes are approved, they will be merged into the main branch.

Thank you for contributing to SafeSCARF Connector!
