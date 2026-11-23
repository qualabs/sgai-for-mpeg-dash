"""The level-2 catalogue: every criterion of context/03, as a check or as a
NOT_VERIFIABLE with its reason (ADR 0050).

A rule's id is its criterion's (R4.1), with a letter when the criterion is
split (R4.1a, R4.1b). Its quote and criterion_sha256 come from pins.json,
the criteria as they read when the rule was written; stale() compares them
with context/03 as it reads now.

applies_to:  mpd / sps-mpd   an MPD that may declare windows (a main
                             presentation, or an alternative one, R40.6)
             list-mpd        the linear resolution document
             overlay-list    the non-linear resolution document
             request         an example resolution request
             spec            the specification itself: its extension schema
"""
from __future__ import annotations

import re
from functools import partial

from ..model import Rule
from . import checks as C
from . import criteria

PINS = criteria.pins()
PLAYER = "Player behaviour: level 3 (reference-player)"
MPDS = ("mpd", "sps-mpd")
RES = ("overlay-list",)
REQ = ("request",)
SPEC = ("spec",)

# Reasons shared by several criteria. Each names what the criterion is about.
TEXT = "a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec"
CONTRACT = "an obligation between parties outside the documents (the APS-to-ADS contract, R18): no document shows it"
NO_CARRIER = ("no carrier is bound for it: context/06 leaves the name to the build and the specification under "
              "test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py")


def rule(rid, applies=SPEC, check=None, nv="", notes=""):
    cid = re.match(r"R\d+\.\d+", rid).group(0)
    pin = PINS[cid]
    r = Rule(id=rid, level=2, source=f"context/03 {cid}", quote=pin["text"], applies_to=tuple(applies),
             not_verifiable=nv, criterion=cid, criterion_sha256=pin["sha256"], notes=notes)
    if check is not None:
        r.check = partial(check, r)
    return r


def player(cid, extra=""):
    return rule(cid, nv=PLAYER + (f". {extra}" if extra else ""))


R = []
add = R.append

# --- Contract foundations ------------------------------------------------------------
add(rule("R1.1", nv="the document property (removing every extension leaves a valid MPD) is level 1, E-4; that the primary content keeps playing is level 3a"))
add(rule("R1.2", nv="that every construct hangs from an enumerated extension point is level 1 (E-3 and the DR rules of ADR 0049)"))
add(rule("R1.3", nv="whether a base construct's semantics were altered is a reading of the specification's prose against the base; " + TEXT))
add(rule("R1.5", nv=TEXT))
add(player("R1.4")); add(player("R1.6"))
add(rule("R2.1", nv="forbids inference at runtime by other actors; the declarations it requires on a document are checked by R4.1 and R12.2"))
add(rule("R2.2", nv="what the ADS decides and how the APS converts it are processes, and the ADS's output is not a document this specification defines"))
add(rule("R2.4", nv=TEXT))
add(player("R2.3"))
for c in ("R11.1", "R11.3", "R11.4", "R11.5"):
    add(rule(c, nv=TEXT))
add(player("R11.2"))
add(rule("R18.1", nv="the event URL is the window's @uri (typed by the schema, level 1); whether a request is sent to it is "
                     "Player behaviour, and an example request is tied to its window only by prose, not by data the check can follow"))
add(rule("R18.2", nv=CONTRACT))

# R29.1: the transport, the closed set, and the value of each reserved parameter.
add(rule("R29.1a", REQ, C.reserved_set_closed, notes="a `sgai-` name outside the two tables is not reserved, the set being closed"))
add(rule("R29.1b", REQ, C.param_values("sgai-video-decoders", lambda v: v in ("1", "2", "3"), "values are 1, 2, 3"),
         notes="sgai-video-decoders takes 1, 2 or 3"))
for i, (p, word) in enumerate([("sgai-image-over-video", "image"), ("sgai-html-over-video", "HTML"),
                              ("sgai-custom-layout", "custom layout"), ("sgai-ad-audio", "ad audio")]):
    add(rule(f"R29.1{'cdef'[i]}", REQ, C.param_values(p, lambda v: v in ("1", "0"), "values are 1, 0"),
             notes=f"{p} takes 1 or 0"))
add(rule("R29.1g", REQ, C.param_values("sgai-allowed-layouts", lambda v: bool(v.split()) and all(t in C.V.TOKENS for t in v.split()),
                                       "the slot's declared allowed layouts, R12.2 tokens"),
         notes="sgai-allowed-layouts is a non-empty list of R12.2 tokens"))
add(rule("R29.1h", REQ, C.param_values("sgai-custom-region", lambda v: C.percents(v) is not None and all(0 <= x <= 100 for x in C.percents(v)),
                                       "the slot's declared custom region, four percentages"),
         notes="sgai-custom-region is four percentages"))
add(rule("R29.1i", REQ, C.param_values("sgai-ad-audio-allowed", lambda v: v == "1", "the only value is 1"),
         notes="sgai-ad-audio-allowed takes only 1"))
add(rule("R29.1j", MPDS + ("list-mpd",), C.no_reserved_in_url_template,
         notes="the transport: query parameters, never the MPD's URL-parameter template (DASH Annex I)"))
add(player("R29.2", "Whether a capability parameter is sent is the Player's choice, and a slot parameter is due only when the slot "
                    "declares it, which needs the window the request was built from"))
add(rule("R29.3", REQ, C.no_empty_reserved,
         notes="held by the Player, but it states a property of the request, the document the Player writes (I-REQ)"))
add(player("R29.4", "A request does not show which parameters the Player added and which came with the Publisher's event URL (R18.2), "
                    "and only the first need the vendor prefix"))
add(rule("R29.5", nv="how an APS behaves on receiving a request without a parameter; no document records it"))
add(rule("R29.7", nv="an absent capability parameter is legal; its meaning (undetermined) binds the APS's resolution, which no document records"))
add(player("R29.10", "Whether a declared value is the device's real capability is a property of the device, not of the request"))

# --- Opportunity declaration ----------------------------------------------------------
add(rule("R4.1", MPDS, C.cap_declared))
add(rule("R4.4", nv=CONTRACT + "; it limits what a conformance check on the ADS may fail"))
add(rule("R4.6", MPDS, C.clip_only_on_replacement,
         notes="the document part: @clip exists only on the replacement; what the cap bounds at runtime is level 3"))
add(rule("R4.7a", nv="a zero cap is a legal declaration (typed by the schema); what it means, not executing, binds the Player"))
add(player("R4.7b"))
for c in ("R4.2", "R4.5", "R4.9", "R4.10"):
    add(player(c))
add(rule("R4.8", nv="@maxDuration on an inherited linear event is optional and typed by the base schema; no document can violate "
                    "R4.8, which fixes how absence is read (level 3)"))
add(rule("R4.11", nv="the timeline the cap accrues on is a Player computation; the document carries only the cap and its timescale"))
add(rule("R31.1", MPDS, C.pause_range,
         notes="the window is a declared range of the primary timeline; the trigger itself is level 3"))
add(rule("R31.2a", nv="the Publisher part forbids an interpretation, not a value: any declared cap on a pause window is legal"))
add(player("R31.2b"))
add(rule("R12.1a", SPEC, C.token_enumeration, notes="the extension schema's layout-token enumeration against R12.2"))
add(rule("R12.1b", nv="citing the IAB source for each accepted value is " + TEXT))
add(rule("R12.2", MPDS, C.layout_vocabulary))
add(rule("R12.3", RES, C.option_layout_vocabulary))
add(rule("R12.4", nv=TEXT + "; the bounds are the IAB's, inherited by reference"))
add(rule("R12.5", nv="the composition a token denotes is what the Player builds on screen (level 3); the document carries only the token, "
                     "checked by R12.2 and R12.3"))
add(rule("R15.1", nv=TEXT))
add(rule("R15.2a", RES, C.option_mime, notes="video (video/*, application/dash+xml), image/* except SVG (OOS-4), text/html"))
add(rule("R15.2b", nv="the Publisher part: an MPD declares windows, not creatives, so no Publisher document carries a form's mimeType"))
add(player("R15.3"))

# --- Selection and ordering ----------------------------------------------------------
add(rule("R5.1", RES, C.candidate_has_option))
add(rule("R5.4", nv=CONTRACT + "; it fixes what the specification may not be read as requiring"))
add(rule("R5.8", nv="what the options represent (the formats the advertiser allowed) is not visible in the document"))
for c in ("R5.3", "R5.6", "R5.9"):
    add(player(c))
add(rule("R7.1", nv="any order of candidates is legal; it binds presentation, which is level 3"))
add(rule("R30.1", nv="that the empty resolution is a complete, well-formed document is the schema's (level 1); that it is not an error "
                     "status or an empty body is a property of the HTTP response, which no example carries"))
add(player("R30.2"))

# --- Presentation ----------------------------------------------------------------------
add(rule("R3.1", nv="the class is derived and never sent: a reserved-looking name for it fails R29.1a, and a vendor-named one cannot be "
                    "recognised by code; giving each class its behaviour is " + TEXT))
add(player("R3.2")); add(player("R16.1"))
add(rule("R32.1a", RES, C.exhaustion_declared, notes="a pause document declares which behaviour applies"))
add(rule("R32.1b", nv="what repeat, request-again and stop mean, and the default, bind the Player (level 3)"))
add(rule("R32.4", nv=TEXT))
add(player("R32.2"))
add(rule("R34.1a", SPEC, C.execute_once_carrier, notes="the spec lets both window families carry the declaration (carrier named by context/06)"))
add(rule("R34.1b", nv="the declaration is optional and boolean (schema, level 1); what it means binds the Player (level 3)"))
add(rule("R34.4", nv="when a window is consumed is the base's execution counter at runtime; no document records it"))
add(rule("R34.6", nv="what an execution is and how it resolves are runtime events (level 3)"))
add(rule("R34.9a", SPEC, C.start_with_offset_carrier, notes="the spec lets an overlay window declare the offset (carrier named by context/06)"))
add(rule("R34.9b", nv="the declaration is optional; where a late execution starts binds the Player (level 3)"))
add(player("R34.3")); add(player("R34.10"))
add(rule("R35.1", RES, C.dismissal_declared, notes="every non-linear resolution document declares dismissibility"))
add(rule("R35.2", RES, C.dismiss_delay, notes="the delay is a number of seconds that must elapse: never negative"))
add(rule("R35.7", nv=TEXT))
add(rule("R35.8", MPDS + ("list-mpd",), C.linear_has_no_dismissal,
         notes="the document part: the base skip control governs, so the overlay/pause dismissal carrier appears on no linear slot"))
add(player("R35.4")); add(player("R35.5"))
add(rule("R36.1a", SPEC, C.earliest_carrier, notes="the spec lets both window families carry the offset (carrier named by context/06)"))
add(rule("R36.1b", nv="the offset is optional with the base default, typed by the schema (level 1); when a Player requests is level 3"))
add(rule("R36.4", RES, C.valid_for, notes="a usable lifetime is never negative; absence is legal"))
add(rule("R36.7", nv=TEXT))
add(player("R36.5"))
add(rule("R37.3", nv=TEXT))
add(player("R37.1")); add(player("R37.2"))
add(rule("R38.1", nv="any declared set of R12.2 tokens is legal (the tokens are R12.2's rule) and absence is legal; what the set, or the "
                     "family default, admits binds the APS (R38.4) and the Player (R5.6)"))
add(rule("R38.4", nv="needs the set the APS received, which the resolution document does not carry; the examples pair a document with "
                     "its request only in prose"))
add(rule("R38.6", nv="a scope statement; the document property it implies, nothing of ours on a linear event, is checked by R40.7"))
add(player("R38.2"))
add(rule("R39.1", MPDS + RES, C.custom_overlay_only, notes="`custom` on no pause window and in no pause document"))
add(rule("R39.2a", MPDS, C.region_with_custom, notes="a region is declared by a Publisher that admits `custom`, which it does by listing it"))
add(rule("R39.2b", MPDS, C.region_in_viewport, notes="x, y, width, height in percent of the viewport, origin top-left"))
add(rule("R39.4a", RES, C.custom_has_rect, notes="a `custom` option carries its rectangle"))
add(rule("R39.4b", RES, C.rect_in_viewport,
         notes="the region received is not in the document, but every region lies inside the viewport"))
add(player("R39.3")); add(player("R39.5"))
add(player("R19.1"))
add(rule("R19.3a", RES, C.non_av_duration))
add(rule("R19.3b", nv="the wall-clock length and the timeline the cap and beacons run on are Player computations (level 3)"))
add(player("R21.1")); add(player("R25.1"))
add(rule("R26.1a", RES, C.background_required, notes="a squeezeback-double-box-background option carries a background"))
add(rule("R26.1b", RES, C.background_forbidden, notes="a squeezeback-double-box option carries none"))
add(rule("R26.1c", nv="that the background is a still image and how the boxes and bands are composed is what the Player renders (level 3)"))
add(player("R26.3"))
add(rule("R27.1a", RES, C.lshape_one_creative, notes="an L-shape or frame option carries no background: one creative, no third element"))
add(rule("R27.1b", nv="that the creative covers the frame under the shrunk primary content is what the Player renders (level 3)"))
add(player("R27.3"))
add(rule("R41.2", nv="ad-audio allowance: " + NO_CARRIER + ". A window that declares nothing does not allow audio, so no document "
                     "violates R41.2 today"))
add(rule("R41.3", nv="audio declared on an option: " + NO_CARRIER))
add(rule("R41.5a", nv="the APS part needs the request (did it carry the allowance?) and an option-audio carrier; " + NO_CARRIER))
add(player("R41.5b"))
for c in ("R41.4", "R41.6", "R41.7"):
    add(player(c))

# --- Interaction & composition rules -----------------------------------------------
add(rule("R14.3", nv=TEXT))
add(rule("R17.4", nv=TEXT))
for c in ("R17.1", "R17.2", "R17.5"):
    add(player(c))
add(rule("R20.2a", MPDS, C.one_stream_per_family))
add(rule("R20.2b", MPDS, C.no_value_on_sgai_stream))
add(rule("R20.4", nv="whether the document's family matches the requesting slot needs the slot, which the document does not carry; "
                     "that it declares a family is the schema's (level 1); what follows is level 3"))
add(rule("R20.6", nv=TEXT))
for c in ("R20.1", "R20.3", "R20.5", "R22.1"):
    add(player(c))
add(rule("R40.1", MPDS, C.pause_on_top_only, notes="optional and at most one are given by a single optional attribute (schema)"))
add(rule("R40.2", nv="says where a Publisher declares a window it wants during an alternative presentation; a document cannot show the want"))
add(rule("R40.9a", MPDS, C.window_family, notes="a window's family is the one its event scheme names"))
add(rule("R40.9b", MPDS, C.overlay_range, notes="an overlay window declares the media-time range it is anchored to"))
add(rule("R40.9c", nv="what the anchoring and each relation mean (presented, suspended, resumed, executed) is level 3"))
add(rule("R40.7", MPDS, C.nothing_on_linear))
add(rule("R40.8", nv=TEXT))
for c in ("R40.3", "R40.4", "R40.5", "R40.6"):
    add(player(c))

# --- Tracking ------------------------------------------------------------------------
add(rule("R6.1", nv=TEXT))
add(rule("R6.3", nv=TEXT))
add(rule("R6.5", nv="any assignment of @id is legal; its scope decides which beacons fire once, which is level 3"))
add(rule("R6.7", nv=TEXT))
add(player("R6.4"))
add(rule("R13.1a", RES, C.tracking_is_callback))
add(rule("R13.1b", nv="that times are relative to the hosting candidate and that each beacon fires then is level 3"))
add(rule("R13.4", nv="the document property, beacons bound to a time travel as callback events, is checked by R13.1a; that the "
                     "specification introduces no scheme is " + TEXT))
add(rule("R13.5", nv=CONTRACT))
add(rule("R13.6a", SPEC, C.option_tracking_carrier, notes="the option can carry the tracking carrier (named by context/06)"))
add(rule("R13.6b", nv="that an option's beacon fires only when that option is presented is level 3"))
add(rule("R13.7", nv="slot-start and slot-end beacons: " + NO_CARRIER))
add(rule("R13.8", nv=TEXT))
add(player("R13.3"))
add(rule("R23.1a", SPEC, C.metadata_elements))
add(rule("R23.1b", nv="stating that emitting and reading the metadata are optional is " + TEXT))
add(rule("R23.2", nv="creative identifiers: " + NO_CARRIER + " (context/06 names AssetIdentifier only for a sub-MPD Period)"))
add(rule("R24.1", ("list-mpd", "sps-mpd"), C.non_av_not_as_mimetype,
         notes="image/* and HTML media types as AdaptationSet or Representation @mimeType on the resolution path"))
add(rule("R33.1", nv=TEXT)); add(rule("R33.3", nv=TEXT))
add(rule("R33.4", MPDS, C.playlist_metric))
add(player("R33.2"))
add(rule("R28.1a", RES + ("list-mpd",), C.clickthrough_placement))
add(rule("R28.1b", nv="firing the click-tracking and offering the destination on activation is level 3"))
add(rule("R28.3", nv=CONTRACT))
add(player("R28.2"))
add(rule("R42.1", nv="occurrence beacons: " + NO_CARRIER))
add(rule("R42.2", nv="needs the occurrence carrier and what the ADS declared; " + NO_CARRIER))
add(rule("R42.4", nv=TEXT))
add(player("R42.3"))
add(rule("R44.1", nv="verification resources: " + NO_CARRIER))
add(rule("R44.2", nv=CONTRACT + "; and " + NO_CARRIER))
add(player("R44.3"))
add(rule("R47.1", nv="viewability beacons ride the occurrence carrier of R42.1: " + NO_CARRIER))
add(rule("R47.3", nv=TEXT))
add(player("R47.2"))
add(rule("R48.1", nv="regulatory disclosure: " + NO_CARRIER))
add(rule("R48.2", nv=CONTRACT + "; and " + NO_CARRIER))
add(player("R48.3"))

# --- Governance --------------------------------------------------------------------
for c in ("R8.1", "R8.2", "R9.1", "R9.2", "R9.3", "R10.1", "R10.2", "R10.3"):
    add(rule(c, nv=TEXT))

RULES = tuple(R)
