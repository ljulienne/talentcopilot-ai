# TalentCopilot v0.2 - Domain Model

## Core idea

TalentCopilot is competency-centered.

- A `Job` contains expected requirements.
- A `Candidate` contains demonstrated capabilities.
- A `MatchResult` compares job requirements with candidate capabilities.

## Main entities

### Job
Represents the role to fill.

### JobRequirement
Represents what the job expects.

### Candidate
Represents the applicant.

### CandidateCapability
Represents what the candidate demonstrates.

### Evidence
Represents proof found in the CV.

### MatchResult
Represents the comparison between the job and the candidate.

## Product philosophy

The AI helps extract and explain information.
TalentCopilot owns the scoring and decision support logic.