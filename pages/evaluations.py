"""
Streamlit page: trigger ground-truth generation and run retrieval/answer
evaluation, and see the resulting metrics.

TODO overall flow:
1. Button: "Generate ground truth" -> calls build_ground_truth() (this is
   slow/costly, so cache the result to a file and only regenerate on demand,
   not on every page load).
2. Button: "Run retrieval evaluation" -> loads the ground truth, calls
   evaluate_retrieval() with a retrieve_fn wrapping your actual search/
   query_data, and displays hit_rate/mrr.
3. Button: "Run answer evaluation" -> for a sample of ground-truth questions,
   run them through RAGClient.rag(), then judge_answer() each result, and
   show aggregate pass/fail or scores.
"""

import streamlit as st
from openai import OpenAI

from llm.rag.search import get_index, load_data
from llm.rag.rag import RAGClient
from llm.eval.ground_truth import build_ground_truth
from llm.eval.metrics import evaluate_retrieval
from llm.eval.judge import judge_answer

st.title("Evaluations")

# TODO: wire up the three steps above as buttons/sections.
# Things to decide as you build this:
# - Where does ground truth get cached? (e.g. data/ground_truth.json, so you
#   don't regenerate 350+ records worth of questions every time you load
#   this page)
# - What does `retrieve_fn` look like for evaluate_retrieval()? It needs to
#   take a question string and return a list of dicts with an 'id' field —
#   RAGClient.search() and RAGClient.query_data() both return records that
#   already have 'id', so either can be wrapped directly.
# - Sample size: full retrieval eval over 357 questions might be fine (cheap,
#   no LLM calls, just search), but full answer eval means 1 rag() call +
#   1 judge call PER question — likely want to sample a subset for that.
