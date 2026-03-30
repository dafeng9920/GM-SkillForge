# GM-LITE Conversational Worksurface Minimal Implementation V1 Change Control Rules

## Allowed

- adding a dedicated console view
- wiring quick actions into the console surface
- surfacing task/output snapshot data in one place
- refining explorer-first entry if it reduces friction

## Not Allowed

- silently replacing explicit task/object visibility with free-form chat only
- expanding plugin scope into heavy orchestration logic
- degrading existing worksurface / writeback / followback capabilities
- treating diagnostic output as the primary user route

## Re-entry Trigger

If console interaction works but output/action visibility is still fragmented, patch the surface and re-enter `CV3` before allowing `CV4` to summarize.
