# TalentCopilot Domain Model v1

## 1. Product Domain

TalentCopilot is an Explainable Talent Decision Intelligence Platform.

Its core purpose is to help recruiters and HR leaders make transparent, explainable and strategy-aware hiring decisions.

## 2. Core Domain Objects

### Recruitment

Represents one hiring process.

Contains:

- job
- candidates
- hiring strategy
- candidate decisions
- reports

### Job

Represents the role to be filled.

Contains:

- title
- requirements
- expected capabilities
- context

### Candidate

Represents the person being evaluated.

Contains:

- identity
- current role
- capabilities
- documents

### CandidateDecision

Central object of TalentCopilot.

Represents the decision view of one candidate for one recruitment.

Contains:

- candidate
- job
- match score
- rank
- recommendation
- confidence
- evidence
- risks
- interview focus
- candidate intelligence
- future candidate fit profiles

### Evidence

Represents facts supporting the analysis.

Contains:

- competency
- status
- score
- confidence
- excerpts
- recommendation

### HiringStrategy

Represents the evaluation strategy selected by the recruiter.

Examples:

- Official Match Score
- International Profile
- Technical Expert
- Leadership
- Executive
- Custom

### CandidateFit

Represents strategy-specific fit scores.

Examples:

- technical fit
- international fit
- leadership fit
- executive fit
- potential fit

### InterviewPlan

Represents the structured interview preparation.

Contains:

- questions
- competency focus
- risk validation points

## 3. Responsibility Rules

### Matching Engine

Owns:

- match score
- match details
- gaps
- interview questions

### Evidence Engine

Owns:

- evidence list
- evidence status
- confidence per competency

### Candidate Intelligence Engine

Owns:

- executive summary
- strengths
- development areas
- readiness
- why explanation

### Ranking Service

Owns:

- sorting candidates
- assigning rank

Default official ranking is based on match_result.overall_score.

### Future Candidate Fit Engine

Will own:

- technical fit
- international fit
- leadership fit
- executive fit
- potential fit

### Future Hiring Strategy Engine

Will own:

- strategy selection
- strategy configuration
- strategy explanation

## 4. Official Ranking Rule

The default official ranking must remain based on:

match_result.overall_score

Candidate Fit or Hiring Strategy rankings may exist, but they must be explicit modes selected by the recruiter.

## 5. Target Architecture

Recruitment
    |
    v
Job + Candidates
    |
    v
Matching Engine
    |
    v
CandidateDecision
    |
    +--> Evidence Engine
    +--> Candidate Intelligence Engine
    +--> Candidate Fit Engine
    +--> Ranking Service
    |
    v
Decision Center

## 6. Product Principle

TalentCopilot should not only rank candidates.

It should explain hiring decisions.

Core question:

Why is this candidate recommended for this job, under this hiring strategy?
