"""AI Mentor — the central intelligence layer of PrepOS.

This module is deliberately decoupled from Knowledge Base, Mission Engine,
Progress Tracking and Auth. It CONSUMES those services (read-only) but never
duplicates their logic.

Public surface:
  - mentor_service.answer(...)         # main chat entry-point
  - conversation_store                 # persistence
  - context_builder.build_context(...) # everything the LLM needs to reason about
  - mentor_routes.router               # /api/mentor/*
"""
