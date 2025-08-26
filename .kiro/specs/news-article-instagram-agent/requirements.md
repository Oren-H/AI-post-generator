# Requirements Document

## Introduction

This feature involves building a simple sequential agent using LangGraph that reads news articles from PDF files stored locally in the repository and generates Instagram captions using OpenAI's language model. The workflow is straightforward: load PDF as text, then prompt OpenAI to generate an engaging Instagram caption.

## Requirements

### Requirement 1

**User Story:** As a content creator, I want to load a news article PDF from the repository, so that I can extract its text content for caption generation.

#### Acceptance Criteria

1. WHEN a PDF file path is provided THEN the system SHALL extract all readable text from the document
2. WHEN the PDF contains text content THEN the system SHALL return the full text as a string
3. IF the PDF is corrupted or unreadable THEN the system SHALL provide a clear error message
4. WHEN text extraction is complete THEN the system SHALL pass the text to the next step

### Requirement 2

**User Story:** As a social media manager, I want to generate an Instagram caption using OpenAI, so that I can create engaging content from the article text.

#### Acceptance Criteria

1. WHEN article text is received THEN the system SHALL send it to OpenAI with an appropriate prompt
2. WHEN prompting OpenAI THEN the system SHALL request an Instagram-optimized caption with hashtags
3. WHEN the caption is generated THEN the system SHALL return the complete caption text
4. IF the OpenAI API call fails THEN the system SHALL provide a clear error message

### Requirement 3

**User Story:** As a user, I want to run the agent with a simple sequential workflow, so that I can process PDFs without complex orchestration.

#### Acceptance Criteria

1. WHEN the agent runs THEN the system SHALL execute PDF loading followed by caption generation in sequence
2. WHEN each step completes THEN the system SHALL pass data to the next step automatically
3. WHEN the workflow finishes THEN the system SHALL output the generated Instagram caption
4. IF any step fails THEN the system SHALL stop execution and report the error

### Requirement 4

**User Story:** As a developer, I want the agent built using LangGraph, so that I can have a clear workflow structure even for this simple sequential process.

#### Acceptance Criteria

1. WHEN implementing the agent THEN the system SHALL use LangGraph with two nodes: PDF loader and caption generator
2. WHEN designing the workflow THEN the system SHALL connect nodes in a simple linear sequence
3. WHEN the agent executes THEN the system SHALL follow the defined LangGraph workflow
4. WHEN errors occur THEN the system SHALL handle them within the LangGraph framework