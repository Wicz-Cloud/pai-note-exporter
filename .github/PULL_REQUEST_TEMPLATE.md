---
name: Pull Request
description: Create a pull request
title: "[PR] "
labels: []
assignees: []
body:
  - type: markdown
    attributes:
      value: |
        Thanks for contributing! Please fill out the form below to help us review your changes.

  - type: textarea
    id: description
    attributes:
      label: Description
      description: Describe the changes you made and why.
      placeholder: "What changes did you make and why?"
    validations:
      required: true

  - type: textarea
    id: related-issues
    attributes:
      label: Related Issues
      description: Link to any related issues this PR addresses.
      placeholder: "Fixes #123, Addresses #456"

  - type: textarea
    id: changes
    attributes:
      label: Changes Made
      description: List the specific changes you made.
      placeholder: |
        - Added new feature X
        - Fixed bug in Y
        - Updated documentation for Z
    validations:
      required: true

  - type: textarea
    id: testing
    attributes:
      label: Testing
      description: How did you test these changes?
      placeholder: |
        - Added unit tests for X
        - Ran existing tests
        - Manual testing of Y
    validations:
      required: true

  - type: textarea
    id: breaking-changes
    attributes:
      label: Breaking Changes
      description: Are there any breaking changes? If so, describe them and migration steps.
      placeholder: "None"

  - type: checkboxes
    id: checklist
    attributes:
      label: Checklist
      description: Please check all that apply
      options:
        - label: I have read the [Contributing Guidelines](https://github.com/Wicz-Cloud/pai-note-exporter/blob/master/CONTRIBUTING.md)
          required: true
        - label: My code follows the project's coding standards
          required: true
        - label: I have added/updated tests for my changes
          required: true
        - label: All tests pass locally
          required: true
        - label: I have updated documentation if needed
          required: true
        - label: My commits follow the project's commit conventions
          required: true
        - label: I have tested my changes on multiple Python versions (if applicable)
          required: false
