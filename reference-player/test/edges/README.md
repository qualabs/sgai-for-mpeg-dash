# Edge vectors of the linear model

E1-E18: the reference's regression tests of the 6th edition's linear model
(the execution queue, Table 57's arithmetic, `@executeOnce`, `@clip`,
`@startWithOffset`, `@returnOffset`, a List MPD whose Linked Period fails, a
pause during a linear ad, an execution on time at playback rate 2, a live
alternative MPD). Where a live alternative starts on its own timeline is not
observed (the observation records no position of an alternative), so E15-E18
judge only its duration and the return. Each expected value is worked from the base
standard in the vector's header, not from the reference. They are not
criteria of `context/03`, so they are not in `spec-source/behaviour/`.

```bash
python3 reference-player/test/edges/run-edges.py            # all, in D1 (minutes; Chromium)
python3 reference-player/test/edges/run-edges.py E3 E5      # some
```

Opt-in, like the battery they run on (ADR 0087). `make_fixtures.py` and
`make_vectors.py` wrote `fixtures/` and `E*.yaml`; edit those and run them
again rather than the YAML.
