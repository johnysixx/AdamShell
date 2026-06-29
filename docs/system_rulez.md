# System Rules

## Rule 1 – Word integrity
Every Word must have a unique identity and immutable state.

## Rule 2 – Chronicle is source of truth
Universe state must always be derivable from Chronicle.

## Rule 3 – No direct Universe mutation
Only Word → Voice → Chronicle → Replay path is valid.

## Rule 4 – Determinism
Replaying the same Chronicle must always produce the same Universe state.

## Rule 5 – Divergence is explicit
Any fork or divergence must be declared via DivergenceInjector.

## Rule 6 – Genesis Separation Rule

Genesis (Day-based logic) must never live inside core/word.

core/word = abstract model of reality
core/genesis = historical sequence of creation