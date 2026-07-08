# 06 — Evidence Graph

## Purpose

The Evidence Graph is the structured representation of all evidence used by TalentCopilot.

It transforms unstructured candidate and job information into connected facts.

## Why it exists

A CV is text.  
A hiring decision requires structured evidence.

The Evidence Graph connects:

- candidate facts;
- experiences;
- skills;
- achievements;
- responsibilities;
- technologies;
- competencies;
- risks;
- sources.

## Core concepts

### Evidence Node

A node represents a fact or concept.

Examples:

- candidate identity;
- skill;
- experience;
- achievement;
- certification;
- language;
- responsibility;
- quantified result.

### Evidence Edge

An edge connects two nodes.

Examples:

- candidate `HAS_SKILL` HRIS;
- experience `DEMONSTRATES` leadership;
- achievement `SUPPORTS` transformation;
- skill `REQUIRED_BY` job.

### Evidence Source

Every important node should be traceable to a source.

Examples:

- CV paragraph;
- job description requirement;
- interview note;
- recruiter input.

## Design principle

No critical decision should be made from untraceable evidence.
