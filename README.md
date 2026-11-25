# solidworks-cad-modeling

Version **0.2.0** — Native SolidWorks CAD modeling and DFMA workflow skill for Windows.

- Paper geometry reproduction, editable SLDPRT/SLDASM, named materials and configurations, STEP handoff for COMSOL.
- Source-grounded DFM/DFA review, sheet-metal fold/unfold checks, machining and fixture planning, assembly positioning and error-proofing, material nesting review.
- Key-design parameter edit/rebuild/restore/disk-reopen evidence, optional batch freeze and retrospective workflow.
- Fourteen generalized experience rules derived from the supplied DFMA v3 notes; original COM helpers retained.

Start with [SKILL.md](SKILL.md). See [DFMA design](references/dfma-design.md) and [evidence loop](references/evidence-loop.md).

This is an agent workflow, not a standalone CAD engine or manufacturing certification. Actual native CAD execution requires a Windows host with SolidWorks, verified COM access and templates. New features require local API preflight. The integration has not been rerun in SolidWorks; historical training cases do not establish independent generalization. Course answer data and local paths are not published.
